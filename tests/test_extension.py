import os

import pytest

from flask_rollup import Bundle, Rollup


def test_create_simple(app):
    rv = Rollup(app)
    assert rv.app == app
    assert app.extensions['rollup'] == rv


def test_init_app(app):
    r = Rollup()
    r.init_app(app)
    assert r.app is None
    assert app.extensions['rollup'] == r


def test_config_path_provided(app):
    config_file_path = '/some/where/rollup.config.js'
    app.config['ROLLUP_CONFIG_JS'] = config_file_path
    rv = Rollup(app)
    assert len(rv.argv) == 3
    assert rv.argv[-1] == config_file_path


def test_autobuild_enabled_in_development(app, mocker):
    mocker.patch.dict('os.environ', {'FLASK_ENV': 'development'})
    Rollup(app)
    assert len(app.before_request_funcs) == 1


def test_autobuild_disabled_in_production(app, mocker):
    mocker.patch.dict('os.environ', {'FLASK_ENV': 'production'})
    Rollup(app)
    assert len(app.before_request_funcs) == 0


def test_register(app):
    b = Bundle('p1', 'some/where', ['some/input/file.js'])
    rollup = Rollup(app)
    rollup.register(b)
    assert len(rollup.bundles) == 1
    assert os.path.isabs(b.target_dir)


@pytest.mark.parametrize('environment', ['development', 'production'])
def test_run(environment, app, mocker):
    name = 'p1'
    mocker.patch.dict('os.environ', {'FLASK_ENV': environment})
    b = Bundle(name, 'some/where', ['some/input/file.js'])
    rollup = Rollup(app)
    rollup.register(b)
    fake_run = mocker.Mock()
    mocker.patch('flask_rollup.subprocess.run', fake_run)
    mocker.patch(
        'flask_rollup.os.stat', mocker.Mock(return_value=mocker.Mock(st_mtime_ns=100))
    )
    rollup.run_rollup(name)
    rollup.run_rollup(name)
    fake_run.assert_called_once()
