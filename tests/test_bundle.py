import pytest

from flask_rollup import Bundle, BundleDefinitionError, Entrypoint


def test_create_params():
    name = 'name 1'
    target_dir = 'some/where'
    entrypoint = 'some/input/file.js'
    b = Bundle(name, target_dir, [entrypoint])
    assert b.entrypoints[0].name == name
    with pytest.raises(TypeError):
        Bundle(name)


@pytest.mark.parametrize('entrypoints', [
    ['some/input/file1.js', 'some/input/file2.js'],
    [Entrypoint(path='some/input/file1.js'), Entrypoint(path='some/input/file2.js')],
    ['some/input/file1.js', Entrypoint(path='some/input/file2.js')],
    [Entrypoint(path='some/input/file1.js'), 'some/input/file2.js'],
], ids=['strings', 'objects', 'mixed-string-1st', 'mixed-object-1st'])
def test_simple_entrypoints_limited(entrypoints):
    name = 'name 1'
    target_dir = 'some/where'
    with pytest.raises(BundleDefinitionError):
        Bundle(name, target_dir, entrypoints)
