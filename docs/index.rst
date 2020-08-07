.. currentmodule:: flask_rollup

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

Installation
------------

*TBD*

Since Rollup is Javascript package, installation of NodeJS is required for operation. Specifically, recent versions of Rollup require NodeJS version 10.0 or newer.

Basic usage
-----------

After installing Flask-Rollup in Python virtual environment, an environment for Rollup has to be initialised. This extension adds CLI command group ``rollup`` and one of provided commands initialise all Javascript tooling for Rollup.

.. code-block:: shell-session

    $ flask rollup --help
    Usage: flask rollup [OPTIONS] COMMAND [ARGS]...

      Rollup Javascript bundler commands

    Options:
      --help  Show this message and exit.

    Commands:
      init  Initialise Rollup environment
      run   Run Rollup and generate all registered bundles

Running ``flask rollup init`` will create bare bones Javascript project control file ``package.json``, install Rollup and all required plugins and finally create generic Rolup configuration file ``rollup.config.js``. All these artifacts are generated in current working directory so these commands may be safely tested outside application code tree.

Once initialisation is done, the extension does not modify anything in Javascript environment so all updates to packages have to be processed *the Javascript way* (eg. with ``npm i --save-dev rollup-plugin-something-fancy``).

With Javascript environment ready Rollup can begin bundling Javascript code of the application. Internally definition expressed as instance of :class:`Bundle` is translated into series of Rollup command line params. Simplest bundle definition can look the below code.

.. code-block:: python

    from flask_rollup import Bundle

    bundle = Bundle(
        name='auth.login', target_dir='dist/js',
        entrypoints=['js/auth.login.js']
    )

This definition will produce ES6 module ``dist/js/auth.login.[hash].js`` and source map file ``dist/js/auth.login.[hash].js.map`` - all these paths are relative to application static folder path. The module will include all code that was imported from installed modules thanks to included plugin that resolves imports from NodeJS location (``node_modules`` directory). In production mode the bundle code will be minified.

The distinction between values coming from Rollup configuration and command line is clear:

* command line options tell Rollup *what to do*
* configuration tells Rollup *how to do it*

.. note::

    Modifications to ``rollup.config.js`` should take into consideration how Rollup processes configuration and command line - the options are **not** overwritten but merged instead. Including bundle parameters like entrypoints or paths in ``rollup.config.js`` may produce undesirable side effects.

Bundle instance then needs to be registered with extension object and once that's done the bundle may be generated with ``flask rollup run``.

Advanced usage patterns
-----------------------

Local Javascript code dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If Javascript code uses local dependencies (eg imported from local module) Rollup will properly pick up modifications to both entrypoint and to imported code. Unfortunately Flask-Rollup does not analyse Javascript code and has to be provided with static list of local dependencies to be able to determine state of bundle while in development mode (whether it's *dirty* and needs to be regenerated or did not change). :class:`Bundle` takes ``dependencies`` argument which is a list of paths (still relative to static directory) to be considered a dependency when calculating bundle state.

Multiple entrypoints
^^^^^^^^^^^^^^^^^^^^

Specify multiple entrypoints to get chunked output. This is not very usable for code splitting (which with some convention may be easily implemented on Python/Flask side) but for example to conditionally include some debug code. If the bundle should produce chunked output, ``entrypoints`` param to :class:`Bundle` constructor can include more elements. These elements may be :class:`Entrypoint` instances or plain strings but the rule is that only one of them may be unnamed (string entrypoint elements are unnamed by its nature).

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
