CLI Reference
=============

irorun provides several commands to manage project bootstrapping, code quality, and configuration. This section documents each command.

init
----
**Description:**  
Bootstraps a new project environment using settings from ``project_config.toml``.

**Usage:**

.. code-block:: bash

   irorun init [PROJECT_DIR] [--package-manager PACKAGE_MANAGER]

**Parameters:**
- ``PROJECT_DIR``: Optional. Specifies the project directory. If omitted, the configuration value is used.
- ``--package-manager``: Select the environment manager. Options: ``poetry``, ``uv``, ``virtualenv``.

**Behavior:**
- Loads configuration from ``project_config.toml``.
- Creates the project directory and subdirectories.
- Initializes the virtual environment and installs dependencies.
- Exits with an error if the project directory already exists.

check
-----
**Description:**  
Runs a combined suite of code quality checks and formatting commands using tools such as Ruff.

**Usage:**

.. code-block:: bash

   irorun check

check_upgrade
-------------
**Description:**  
Checks code syntax for upgrades. Optionally applies fixes with ``--fix``.

**Usage:**

.. code-block:: bash

   irorun check_upgrade [--fix]

check_codestyle
---------------
**Description:**  
Checks your code style against PEP 8 conventions.

**Usage:**

.. code-block:: bash

   irorun check_codestyle

format
------
**Description:**  
Formats the code (e.g., sorts imports, removes unused imports).

**Usage:**

.. code-block:: bash

   irorun format

gen_config
----------
**Description:**  
Generates a default configuration file, ``project_config.toml``.

**Usage:**

.. code-block:: bash

   irorun gen_config

Additional commands and features may be added in future releases.