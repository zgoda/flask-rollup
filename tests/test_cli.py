import os

from flask_rollup import Rollup
from flask_rollup.cli import rollup_init_cmd


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
