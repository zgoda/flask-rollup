import ast
import codecs
import re
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))


def read(*parts):
    with codecs.open(path.join(here, *parts), 'r', encoding='utf-8') as fp:
        return fp.read()


_version_re = re.compile(r"__version__\s+=\s+(.*)")


def find_version(*where):
    return str(ast.literal_eval(_version_re.search(read(*where)).group(1)))


test_reqs = [
    'pytest',
    'pytest-cov',
    'pytest-mock',
]


docs_reqs = [
    'Sphinx'
]


dev_reqs = [
    'ipdb',
    'flake8',
    'flake8-builtins',
    'flake8-bugbear',
    'flake8-comprehensions',
    'pep8-naming',
    'dlint',
    'rstcheck',
    'rope',
    'isort',
    'wheel',
    'flask-shell-ipython',
    'watchdog',
] + test_reqs + docs_reqs


setup(
    name='Flask-Rollup',
    url='https://github.com/zgoda/flask-rollup',
    license='BSD-3-Clause',
    author='Jarek Zgoda',
    description='Rollup integration with Flask web framework',
    long_description=read('README.rst'),
    long_description_content_type='text/x-rst',
    version=find_version('src/flask_rollup/__init__.py'),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask>=1.1,<2.1'
    ],
    extras_require={
        'test': test_reqs,
        'docs': docs_reqs,
        'dev': dev_reqs,
    },
    python_requires='~=3.7',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: JavaScript',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Build Tools',
    ],
    entry_points={
        'flask.commands': [
            'rollup=flask_rollup.cli:rollup_grp',
        ]
    },
    project_urls={
        'Documentation': 'https://flask-rollup.readthedocs.io/',
        'Source': 'https://github.com/zgoda/flask-rollup',
        'Issues': 'https://github.com/zgoda/flask-rollup/issues',
    },
)
