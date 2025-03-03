Configuration
=============

irorun relies on external configuration files to dictate its behavior. The two primary configuration files are:

1. **project_config.toml:**  
   Controls project bootstrapping parameters such as project directory, environment manager, subdirectories, dependencies, and additional options like Git initialization.

2. **logging.conf:**  
   Defines the logging setup, including loggers, handlers, and formatters. It uses a custom handler to output color-coded logs.

Example: project_config.toml
----------------------------

.. code-block:: toml

   [init]
   project_directory = "apriquot"
   subdirectories = ["src", "docs", "tests"]
   extra_subdirectories = []  # Additional directories if needed
   package_manager = "poetry" # Options: "poetry", "uv", "virtualenv"
   venv_name = "venv"
   dependencies = ["numpy", "pandas", "matplotlib"]

Example: logging.conf
---------------------

.. code-block:: ini

   [loggers]
   keys=root,irorun

   [handlers]
   keys=typerHandler,fileHandler

   [formatters]
   keys=coloredFormatter

   [logger_root]
   level=INFO
   handlers=typerHandler

   [logger_irorun]
   level=DEBUG
   handlers=typerHandler,fileHandler
   qualname=irorun
   propagate=0

   [handler_typerHandler]
   class=irorun.logger_setup.TyperLoggerHandler
   level=DEBUG
   formatter=coloredFormatter
   args=()

   [handler_fileHandler]
   class=FileHandler
   level=INFO
   formatter=coloredFormatter
   args=('irorun.log', 'a')

   [formatter_coloredFormatter]
   format=[%(asctime)s] %(levelname)s in %(module)s: %(message)s
   datefmt=%Y-%m-%d %H:%M:%S

This structure allows you to modify behavior without changing code, ensuring consistency across environments.