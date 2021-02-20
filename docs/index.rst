.. module:: flask_rollup

Flask-Rollup
============

`Rollup`_ Javascript bundler integration with `Flask`_ web framework. Because we need modern tools for modern web development.

While development of :abbr:`SPA (Single Page Applications)` is pretty straightforward since there is strict separation of backend and frontend code, the development of Javascript-rich Multi-Page Applications requires great deal of extra code that needs to be put to properly process Javascript and produce appropriately bundled output. While it is possible to go with pre-bundled dependencies, such approach limits the ability to debug and analyse program execution, since usually these bundles are already minified and rarely provide source maps. This is where bundlers come in handy, these programs can output either non-minified bundles for development and minified for production, provide *tree shaking* feature for unused code removal and can limit included code to only what's used on particular page (*code splitting*).

There are many Javascript bundlers out there, providing different feature sets and with different goals. The idea of Flask-Rollup came from a specific set of requirements:

* ES6 modules as the output of the bundling process
* *tree shaking* done well
* extensive command line operation supported by configuration loaded from file
* can process CommonJS dependencies to include code in form that's compatible with output

`Rollup`_ meets all these requirements. It's possible others do that too, but for now let's focus on Rollup.

The goal is to integrate Rollup as Javascript bundler with Flask application development process as seamlessly as it is possible. In most basic case this should not require any interaction with ``npm``/``npx`` but instead provide familiar interface of Flask :abbr:`CLI (Command Line Interface)`, extended to support Rollup commands and process.

.. _Rollup: https://rollupjs.org/
.. _Flask: https://palletsprojects.com/p/flask/

Dependencies
------------

NodeJS 10 (with ``npm``), Python 3.7 and Flask 1.1. We're modern.

Installation
------------

Use pip to install officially released version from PyPI.

.. code-block:: shell-session

    $ pip install -U flask-rollup

It does not matter how NodeJS has been installed, it just needs to be available in system search path along with ``npm``. If unsure use either system provided ones (Ubuntu 20.04: NodeJS 10.19.0 and npm 6.14.4) or use `nvm tool`_ to install locally any arbitrary version.

.. _nvm tool: https://github.com/nvm-sh/nvm

Basic usage
-----------

After installing Flask-Rollup in Python virtual environment an environment for Rollup has to be initialised. This extension adds CLI command group ``rollup`` and one of provided commands initialise all Javascript tooling for Rollup.

.. code-block:: shell-session

    $ flask rollup --help
    Usage: flask rollup [OPTIONS] COMMAND [ARGS]...

      Rollup Javascript bundler commands

    Options:
      --help  Show this message and exit.

    Commands:
      init  Initialise Rollup environment
      run   Run Rollup and generate all registered bundles

Running ``flask rollup init`` will create bare bones Javascript project control file ``package.json``, install Rollup and all required plugins and finally create generic Rollup configuration file in ``rollup.config.js``. All these artifacts are generated in current working directory so these commands may be safely tested outside of application code tree.

``init`` command takes optional flag ``--babel`` which signals if `Babel transpiler`_ should also be installed along with related plugins. This is important if you want your Javascript code to be transpiled down to ES6 and allows you to write it using features from any newer or experimental ES version, like `spread operator for object literals`_ from ES9 that's still marked as *experimental* with `CanIUse`_. With this option enabled, a bare bones Babel configuration file will be written as ``babel.config.json``. This configuration will include only options related to transpilation to target ES version so you can freely modify it to include other Babel options.

Once initialisation is done, the extension does not modify anything in Javascript environment so all updates to packages have to be processed *the Javascript way* (eg. with ``npm i -D rollup-plugin-something-fancy`` and then adding it to Rollup pipeline in ``rollup.config.js``).

With Javascript environment ready Rollup can start bundling Javascript code of the application. Internally definition expressed as instance of :class:`Bundle` is translated into series of Rollup command line params. Simplest bundle definition can look like the below code.

.. code-block:: python

    from flask_rollup import Bundle

    bundle = Bundle(
        name='auth.login', target_dir='dist/js',
        entrypoints=['js/auth.login.js']
    )

Both entrypoint and target paths are relative to application static folder. The above definition will produce ES6 module ``dist/js/auth.login.[hash].js`` and source map file ``dist/js/auth.login.[hash].js.map``. The module will include all code that was imported from installed modules thanks to preconfigured plugin that resolves imports from NodeJS location (``node_modules`` directory). In production mode the bundle code will also be minified with `Terser`_.

If entrypoints Javascript code depends on any other module that's not installed in ``node_modules``, it should be listed in bundle's ``dependencies`` list. Rollup bundles this code without any issues, but in Python the module content is not parsed so all such dependencies have to be specified manually so the bundle gets rebuilt once they change. This is important only in development mode when bundles are automatically rebuilt upon code changes.

.. code-block:: python

    from flask_rollup import Bundle

    bundle = Bundle(
        name='auth.login', target_dir='dist/js',
        entrypoints=['js/auth.login.js'],
        dependencies=['js/utils.js', 'js/security.js'],
    )

Once bundle is registered it may be generated with ``flask rollup run``. For convenience in development mode bundles are built automatically if there are any changes to its entrypoints or dependencies.

.. _Terser: https://terser.org/
.. _Babel transpiler: https://babeljs.io/
.. _spread operator for object literals: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Spread_syntax#spread_in_object_literals
.. _CanIUse: https://caniuse.com/mdn-javascript_operators_spread_spread_in_destructuring

Production vs development mode
------------------------------

The operation of Rollup with regards to environment is controlled by Flask environment variable ``FLASK_ENV``. It's automatically set by Flask but may be also controlled with startup scripts or `python-dotenv`_ package. This variable is directly translated to ``NODE_ENV`` and to ``process.environment`` in Javascript code in consequence.

.. _python-dotenv: https://pypi.org/project/python-dotenv/

Extension configuration
-----------------------

This extension uses following configuration options.

``ROLLUP_PATH``
    path to ``rollup`` executable, if not provided it will be assumed it's available in system search path as ``rollup``

``ROLLUP_CONFIG_JS``
    path to ``rollup.config.js`` file with Rollup configuration, it has to be provided for running web application and may be omitted for CLI operations, it will be assumed this file is present in current working directory; this must be set when in ``production`` mode

Rollup bundling configuration
-----------------------------

Initialisation function produces generic Rollup config file ``rollup.config.js`` which in most cases is sufficient but may be modified to specific needs. Since the extension controls Rollup command line, the only way to change Rollup behaviour is with this configuration file. The distinction between values coming from Rollup configuration and command line should be kept strict and resolved as follows:

* command line options tell Rollup *what to do* (what input files to process)
* configuration tells Rollup *how to do it* (how to process input files)

.. note::

    Modifications to ``rollup.config.js`` should take into consideration how Rollup processes configuration and command line - the options are **not** overwritten but merged instead. Including bundle parameters like entrypoints or paths in ``rollup.config.js`` (iow *what to do*) may produce undesirable side effects.

The *what to do* part is controlled by bundle definitions in your code.

Be aware that processing additional (non-Javascript) files is neither natively supported by Rollup or this extension. In other words, if you think you can make Rollup (or Flask-Rollup) to process your SCSS or PostCSS modules then you better stop. It's not intended to do that. Use `Flask-Assets`_.

.. _Flask-Assets: https://pypi.org/project/Flask-Assets/

Template function
-----------------

This extension registers global template function ``jsbundle`` that takes bundle name as an argument and returns bundle url to be included in Jinja2 template. In particular, it can be used in Javascript code like below.

.. code-block:: html+jinja

    {% block scripts %}
    <script type="module">
        import { html, render, Dashboard } from '{{ jsbundle(request.endpoint) }}';
        render(
            html`<${Dashboard} />`,
            document.getElementById('dashboard-block'),
        );
    </script>
    {% endblock %}

To make this work, bundles should be named after route endpoints where they are supposed to be included.

API Documentation
-----------------

.. autoclass:: Rollup
    :members:

.. autoclass:: Bundle
    :members:

.. autoclass:: Entrypoint
    :members:


Advanced usage patterns
-----------------------

Local Javascript code dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If Javascript code uses local dependencies (eg imported from local modules, as opposed to installed libraries), Rollup will properly pick up modifications to both entrypoint and to imported code. Unfortunately Flask-Rollup does not analyse Javascript code and has to be provided with static list of local dependencies to be able to determine state of bundle while in development mode (whether it's *dirty* and needs to be regenerated or did not change). :class:`Bundle` takes ``dependencies`` argument which is a list of paths (still - relative to static directory) to be considered a dependency when calculating bundle state.

Multiple entrypoints
^^^^^^^^^^^^^^^^^^^^

Specify multiple entrypoints to get chunked output. This is not always usable for code splitting (which with the above mentioned convention of naming bundles after Flask view endpoints may be easily implemented on Python side) but for example to conditionally include some debug code. If the bundle should produce chunked output, ``entrypoints`` param to :class:`Bundle` constructor can include more elements. These elements may be :class:`Entrypoint` instances or plain strings but the rule is that only one of them may be unnamed (string entrypoint elements are unnamed by its nature). Generated chunks will have names of respective entrypoints.

.. toctree::
    :maxdepth: 2
    :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
