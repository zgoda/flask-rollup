import shlex
import subprocess

import click
from flask import current_app
from flask.cli import with_appcontext


@click.group(name='rollup')
def rollup_grp():
    """Rollup commands
    """
    pass


@rollup_grp.command(name='init')
@with_appcontext
def rollup_init_cmd():
    """Initialize Rollup environment"""
    rollup_config = """import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';

const isProduction = process.env.NODE_ENV === 'production';

const terserOpts = {
    compress: {ecma: 2015, module: true},
    mangle: {module: true},
    output: {ecma: 2015},
    parse: {ecma: 2015},
    rename: {},
}

export default (async () => ({
    output: {
        format: 'es',
        sourcemap: true,
        entryFileNames: '[name].[hash].js',
    },
    plugins: [
        resolve(),
        commonjs(),
        isProduction && (await import('rollup-plugin-terser')).terser(terserOpts),
    ]
}))();
"""
    init_cmd = shlex.split('npm init -y')
    click.echo('Initializing npm environment')
    subprocess.run(
        init_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    install_cmd = shlex.split(
        'npm install --save-dev rollup '
        '@rollup/plugin-commonjs @rollup/plugin-node-resolve rollup-plugin-terser'
    )
    click.echo('Installing Rollup and plugins')
    subprocess.run(
        install_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    click.echo('Creating Rollup configuration module')
    with open('rollup.config.js', 'w') as fp:
        fp.write(rollup_config)
    click.echo('All done, Rollup installation is ready')


@rollup_grp.command(name='run')
@with_appcontext
def rollup_run_cmd():
    """Run rollup and generate all registered bundles"""
    rollup = current_app.extensions['rollup']
    for name in rollup.bundles.keys():
        click.echo(f'Building bundle {name}')
        rollup.run_rollup(name)
    click.echo('All done')
