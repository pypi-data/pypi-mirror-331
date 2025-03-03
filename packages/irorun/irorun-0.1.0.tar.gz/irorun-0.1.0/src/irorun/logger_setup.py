# Copyright 2025 Faith O. Oyedemi
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For more details, see the full text of the Apache License at:
# http://www.apache.org/licenses/LICENSE-2.0

import logging
import logging.config
import os

import typer


class TyperLoggerHandler(logging.Handler):
	"""
	A custom logging handler that uses Typer's secho to produce elegant, color-coded log messages.
	"""

	def emit(self, record: logging.LogRecord) -> None:
		fg = None
		bg = None

		# Map log levels to Typer colors.
		match record.levelno:
			case logging.DEBUG:
				fg = typer.colors.BLACK
			case logging.INFO:
				fg = typer.colors.BRIGHT_BLUE
			case logging.WARNING:
				fg = typer.colors.BRIGHT_MAGENTA
			case logging.ERROR:
				fg = typer.colors.BRIGHT_WHITE
				bg = typer.colors.RED
			case logging.CRITICAL:
				fg = typer.colors.BRIGHT_RED

		message = self.format(record)
		typer.secho(message, fg=fg, bg=bg)


def setup_logging(config_path: str = 'logging.conf') -> logging.Logger:
	"""
	Loads logging configuration from the specified configuration file.
	Falls back to a basic configuration using TyperLoggerHandler if the config file is not found.
	"""
	if os.path.exists(config_path):
		logging.config.fileConfig(config_path, disable_existing_loggers=False)
	else:
		# Fallback configuration: use TyperLoggerHandler directly.
		handler = TyperLoggerHandler()
		formatter = logging.Formatter(
			'[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
			datefmt='%Y-%m-%d %H:%M:%S',
		)
		handler.setFormatter(formatter)
		logging.basicConfig(level=logging.INFO, handlers=[handler])
	return logging.getLogger('irorun')


# Initialize and export the logger.
def get_logger() -> logging.Logger:
	"""
	Returns the configured logger.
	"""
	return setup_logging()
