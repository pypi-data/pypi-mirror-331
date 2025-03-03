Project Architecture
====================

This section describes the design and structure of the irorun project.

Directory Layout
----------------

A typical directory structure is as follows:

.. code-block:: text

   irorun/
   ├── irorun/              # Main package directory
   │   ├── __init__.py
   │   ├── cli.py           # Entry point for the CLI
   │   ├── helpers.py       # Helper functions for project creation and command execution
   │   └── logger_setup.py  # Custom logging configuration and handler
   ├── tests/               # Unit and integration tests
   ├── docs/                # Sphinx documentation sources
   ├── project_config.toml  # Configuration for project bootstrapping
   ├── logging.conf         # Logging configuration file
   └── pyproject.toml       # Build and metadata configuration

Key Modules
-----------

- **cli.py:**  
  Implements the Typer-based CLI, defining commands such as ``init``, ``check``, and others.

- **helpers.py:**  
  Contains functions to create projects using various environment managers and manage subdirectory creation.

- **logger_setup.py:**  
  Configures logging using a custom ``TyperLoggerHandler`` that outputs elegant, color-coded logs.

- **Configuration Files:**  
  - *project_config.toml* defines project setup parameters.
  - *logging.conf* controls logging output and format.

Design Principles
-----------------
- **Modularity:** Each component (CLI, logging, configuration) is isolated for easy maintenance.
- **Extensibility:** New commands and features can be added with minimal changes to existing code.
- **Configurability:** Project behavior and logging are driven by external configuration files.