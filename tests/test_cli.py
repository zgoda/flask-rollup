import os

from flask_rollup import Bundle, Rollup
from flask_rollup.cli import rollup_init_cmd, rollup_run_cmd


def test_init_command(app, tmp_path, mocker):
    Rollup(app)
    pwd = tmp_path / 'flaskrolluptest'
    os.makedirs(pwd, exist_ok=True)
    os.chdir(pwd)
    fake_run = mocker.Mock()
    mocker.patch('flask_rollup.cli.subprocess.run', fake_run)
    runner = app.test_cli_runner()
    rv = runner.invoke(rollup_init_cmd)
    assert rv.exit_code == 0
    assert 'Rollup installation is ready' in rv.output
    assert fake_run.call_count == 2


def test_init_with_babel(app, tmp_path, mocker):
    Rollup(app)
    pwd = tmp_path / 'flaskrolluptest'
    os.makedirs(pwd, exist_ok=True)
    os.chdir(pwd)
    fake_run = mocker.Mock()
    mocker.patch('flask_rollup.cli.subprocess.run', fake_run)
    runner = app.test_cli_runner()
    rv = runner.invoke(rollup_init_cmd, ['--babel'])
    assert rv.exit_code == 0
    assert 'Rollup installation is ready' in rv.output
    assert fake_run.call_count == 2
    install_cmd = fake_run.call_args_list[-1][0][0]
    assert '@babel/core' in install_cmd


def test_run_command(app, mocker):
    b = Bundle('p1', 'some/where', ['some/input/file.js'])
    rollup = Rollup(app)
    rollup.register(b)
    fake_run = mocker.Mock()
    mocker.patch.object(rollup, 'run_rollup', fake_run)
    runner = app.test_cli_runner()
    rv = runner.invoke(rollup_run_cmd)
    assert rv.exit_code == 0
    assert 'All done' in rv.output
    fake_run.assert_called_once()
