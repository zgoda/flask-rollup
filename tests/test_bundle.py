import hashlib
import os

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
    ['some/input/file1.js', Entrypoint(path='some/input/file2.js', name='p2')],
    [
        Entrypoint(path='some/input/file1.js', name='p1'),
        Entrypoint(path='some/input/file2.js', name='p2'),
    ]
], ids=['mixed', 'objects'])
def test_multiple_entrypoints(entrypoints):
    name = 'name 1'
    target_dir = 'some/where'
    b = Bundle(name, target_dir, entrypoints)
    assert len(b.entrypoints) == len(entrypoints)


def test_resolve_paths_simple():
    b = Bundle('p1', 'some/where', ['some/input/file.js'])
    b.resolve_paths('/static/directory')
    assert os.path.isabs(b.target_dir)
    for e in b.entrypoints:
        assert os.path.isabs(e.path)


def test_resolve_paths_with_dependencies():
    b = Bundle(
        'p1', 'some/where', ['some/input/file1.js'],
        dependencies=['some/input/file2.js', 'some/input/file3.js'],
    )
    b.resolve_paths('/static/directory')
    for p in b.dependencies:
        assert os.path.isabs(p)


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


def test_calc_state(mocker):
    mocker.patch(
        'flask_rollup.os.stat', mocker.Mock(return_value=mocker.Mock(st_mtime_ns=100))
    )
    b = Bundle(
        'p1', 'some/where', ['some/input/file1.js'],
        dependencies=['some/input/file2.js', 'some/input/file3.js'],
    )
    b.resolve_paths('/static/directory')
    rv = b.calc_state()
    assert rv == hashlib.sha256('\n'.join(['100'] * 3).encode('utf-8')).hexdigest()


def test_bundle_argv():
    b = Bundle(
        'p1', 'some/where', ['some/input/file1.js'],
        dependencies=['some/input/file2.js', 'some/input/file3.js'],
    )
    b.resolve_paths('/static/directory')
    rv = b.argv()
    assert len(rv) == 2 + len(b.entrypoints)
    assert rv[0] == '-d'
    assert rv[1] == b.target_dir


def test_resolve_output_ok(mocker):
    tgt_path = '/static/directory/some/where/file1.js'
    mocker.patch(
        'flask_rollup.glob.glob', mocker.Mock(return_value=[tgt_path])
    )
    b = Bundle('p1', 'some/where', ['some/input/file1.js'])
    b.resolve_paths('/static/directory')
    url_path = '/static'
    b.resolve_output('/static/directory', url_path)
    assert b.output.file_path == tgt_path
    assert b.output.static_path == tgt_path.replace('/static/directory/', '')
    assert b.output.url == os.path.join(url_path, b.output.static_path)


def test_resolve_output_fail(mocker):
    tgt_paths = [
        '/static/directory/some/where/file1.js',
        '/static/directory/some/where/file2.js'
    ]
    mocker.patch(
        'flask_rollup.glob.glob', mocker.Mock(return_value=tgt_paths)
    )
    b = Bundle('p1', 'some/where', ['some/input/file1.js'])
    b.resolve_paths('/static/directory')
    url_path = '/static'
    b.resolve_output('/static/directory', url_path)
    assert b.output is None
