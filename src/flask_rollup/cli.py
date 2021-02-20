import shlex
import subprocess

import click
from flask import current_app
from flask.cli import with_appcontext


@click.group(name='rollup')
def rollup_grp():  # pragma: no cover
    """Rollup commands
    """
    pass


@rollup_grp.command(name='init')
@with_appcontext
@click.option(
    '--babel', 'install_babel', is_flag=True, default=False,
    help='whether to install Babel and configure Rollup plugin',
)
def rollup_init_cmd(install_babel):
    """Initialise Rollup environment."""

    rollup_config_plain = """import resolve from '@rollup/plugin-node-resolve';
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

    rollup_config_babel = """import resolve from '@rollup/plugin-node-resolve';
import { babel } from '@rollup/plugin-babel';
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
        babel({ babelHelpers: 'bundled' })
        isProduction && (await import('rollup-plugin-terser')).terser(terserOpts),
    ]
}))();
"""

    babelrc = """{
  "presets": [
    [
      "@babel/preset-env",
      {
        "targets": {
          "esmodules": true
        },
        "bugfixes": true
        "modules": false
      }
    ]
  ]
}
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
    if install_babel:
        install_cmd.extend([
            '@rollup/plugin-babel',
            '@babel/core',
            '@babel/preset-env',
        ])
    click.echo('Installing Rollup and plugins')
    subprocess.run(
        install_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    click.echo('Creating Rollup configuration module')
    config = rollup_config_plain
    if install_babel:
        config = rollup_config_babel
        with open('babel.config.json', 'w') as fp:
            fp.write(babelrc)
    with open('rollup.config.js', 'w') as fp:
        fp.write(config)
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
