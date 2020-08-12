import os

import pytest
from flask import url_for, render_template_string

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


def test_autobuild_running_in_development(app, mocker):
    def handler():
        return 'something'
    app.config['SERVER_NAME'] = '127.0.0.1'
    name = 'p1'
    mocker.patch.dict('os.environ', {'FLASK_ENV': 'development'})
    rollup = Rollup(app)
    b = Bundle(name, 'some/where', ['some/input/file.js'])
    rollup.register(b)
    app.add_url_rule('/something', endpoint=name, view_func=handler)
    fake_run = mocker.Mock()
    mocker.patch.object(rollup, 'run_rollup', fake_run)
    with app.test_client() as client:
        with app.app_context():
            url = url_for(name)
        client.get(url)
    fake_run.assert_called_once_with(name)


def test_autobuild_skipped_for_other_endpoint(app, mocker):
    def handler():
        return 'something'
    app.config['SERVER_NAME'] = '127.0.0.1'
    name = 'p1'
    other_name = 'p2'
    mocker.patch.dict('os.environ', {'FLASK_ENV': 'development'})
    rollup = Rollup(app)
    b = Bundle(name, 'some/where', ['some/input/file.js'])
    rollup.register(b)
    app.add_url_rule('/something', endpoint=name, view_func=handler)
    app.add_url_rule('/otherthing', endpoint=other_name, view_func=handler)
    fake_run = mocker.Mock()
    mocker.patch.object(rollup, 'run_rollup', fake_run)
    with app.test_client() as client:
        with app.app_context():
            url = url_for(other_name)
        client.get(url)
    fake_run.assert_not_called()


def test_autobuild_disabled_in_production(app, mocker):
    mocker.patch.dict('os.environ', {'FLASK_ENV': 'production'})
    Rollup(app)
    assert len(app.before_request_funcs) == 0


def test_autobuild_not_running_in_production(app, mocker):
    def handler():
        return 'something'
    app.config['SERVER_NAME'] = '127.0.0.1'
    name = 'p1'
    mocker.patch.dict('os.environ', {'FLASK_ENV': 'production'})
    rollup = Rollup(app)
    b = Bundle(name, 'some/where', ['some/input/file.js'])
    rollup.register(b)
    app.add_url_rule('/something', endpoint=name, view_func=handler)
    fake_run = mocker.Mock()
    mocker.patch.object(rollup, 'run_rollup', fake_run)
    with app.test_client() as client:
        with app.app_context():
            url = url_for(name)
        client.get(url)
    fake_run.assert_not_called()


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


def test_template_global(app, mocker):
    def handler():
        return render_template_string('{{ jsbundle(request.endpoint) }}')
    app.config['SERVER_NAME'] = '127.0.0.1'
    name = 'p1'
    b = Bundle(name, 'some/where', ['some/input/file.js'])
    mocker.patch.object(b, 'calc_state', mocker.Mock(return_value='state'))
    rollup = Rollup(app)
    rollup.register(b)
    app.add_url_rule('/something', endpoint=name, view_func=handler)
    mocker.patch('flask_rollup.subprocess.run', mocker.Mock())
    tgt_path = '/static/directory/some/where/file1.js'
    mocker.patch(
        'flask_rollup.glob.glob', mocker.Mock(return_value=[tgt_path])
    )
    rollup.run_rollup(name)
    with app.test_client() as client:
        with app.app_context():
            url = url_for(name)
        rv = client.get(url)
        assert b.output.url.encode('utf-8') in rv.data
