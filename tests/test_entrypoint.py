from flask_rollup import Entrypoint


def test_cmdline_param_simple():
    name = 'name1'
    path = 'path1'
    e = Entrypoint(path, name)
    assert e.cmdline_param() == f'{name}={path}'
