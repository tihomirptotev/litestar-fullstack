===================
Starting the server
===================

This section describes how to start the application in development and production mode.

Development
^^^^^^^^^^^

Run the Vite dev server (via bun) in one terminal:

.. code-block:: bash

    cd src/js/web
    bun run dev

And the Litestar server in another:

.. code-block:: bash

    uv run app run

The dev server listens on ``VITE_PORT`` (default ``3006``) and proxies API
requests to the backend application. Assets are served under ``/static/web/``.

Production
^^^^^^^^^^

Build the frontend assets into ``src/py/app/server/static/web``:

.. code-block:: bash

    cd src/js/web
    bun run build

Then run the server:

.. code-block:: bash

    uv run app run

.. note::
   - ``VITE_PORT``: Optional dev server port override.
   - ``ASSET_URL``: Optional asset base path (defaults to ``/static/web/``).
   - ``SAQ_USE_SERVER_LIFESPAN``: Auto start/stop SAQ processes with the app.