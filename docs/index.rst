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

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
