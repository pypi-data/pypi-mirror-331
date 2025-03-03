Logging
=======

irorun utilizes a custom logging system to provide elegant, color-coded log output. This section details the logging design and how to adjust it.

Custom TyperLoggerHandler
-------------------------
The custom handler, ``TyperLoggerHandler``, is defined in ``logger_setup.py``. It maps log levels to colors:

- **DEBUG:** Black
- **INFO:** Bright blue
- **WARNING:** Bright magenta
- **ERROR:** Bright white on red
- **CRITICAL:** Bright red

It uses Typer's ``secho`` function to print log messages with color.

Logging Configuration (logging.conf)
--------------------------------------
The file ``logging.conf`` contains settings for:
- **Loggers:** A root logger and a dedicated ``irorun`` logger.
- **Handlers:** The custom ``typerHandler`` (for console output) and a file handler (to write logs to ``irorun.log``).
- **Formatters:** The ``coloredFormatter`` formats messages with a timestamp, log level, and module name.

Dynamic Logging Control
-----------------------
You can adjust the logging level at runtime via the CLI's ``--verbose`` option. In the main Typer callback, the logger’s level is set to ``DEBUG`` if verbose mode is enabled.

Modifying Logging Behavior
--------------------------
- **Change Log Level:** Edit ``logging.conf`` or use the CLI option.
- **Extend the Handler:** Modify ``TyperLoggerHandler`` in ``logger_setup.py`` for additional customizations.
- **File Logging:** Adjust the file handler settings to rotate logs or change file paths as needed.