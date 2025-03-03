# Copyright (c) 2025 Faith O. Oyedemi
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
import os
import subprocess
from pathlib import Path

import toml
import typer

from irorun.helpers import (
	EnvManager,
	create_poetry_project,
	create_subdirectories,
	create_uv_project,
	create_virtualenv_project,
)
from irorun.logger_setup import setup_logging

DEFAULT_PACKAGE_MANAGER: EnvManager = EnvManager.VIRTUALENV.value

app = typer.Typer()
logger = setup_logging()


@app.callback()
def main(
	verbose: bool = typer.Option(
		False, '--verbose', '-v', help='Enable verbose logging.'
	),
):
	"""Global callback to adjust logging level based on the --verbose flag."""
	if verbose:
		logger.setLevel(logging.DEBUG)
		logger.debug('Verbose logging enabled.')
	else:
		logger.setLevel(logging.INFO)


def load_config(config_path: str = 'project_config.toml') -> dict:
	config_path = Path(config_path)
	if not config_path.exists():
		typer.echo(
			'Please ensure the file exists and is properly formatted. Or use `irorun gen-config` to generate one that you can edit.'
		)
		logger.warning(f'Configuration file not found at {config_path}')
		return {}
	else:
		logger.info(f'Configuration file found at {config_path}. Attempting to load...')
		try:
			config = toml.load(config_path).get('init', {})
			logger.info(f'Loaded configuration: {config}')
			return config
		except Exception as e:
			logger.error(f'Error loading configuration: {e}')
			raise typer.Exit(1)


@app.command()
def init(
	project_dir: str = typer.Option(
		None,
		'--project-directory',
		help='Project directory. If not provided, uses configuration value.',
	),
	package_manager: EnvManager = typer.Option(
		DEFAULT_PACKAGE_MANAGER,
		'--package-manager',
		help='Environment manager to use: poetry, uv, or virtualenv.',
	),
):
	"""
	Bootstraps a new project environment using settings from project_config.toml.
	"""
	# Load configuration
	config = load_config()
	logging.info('Back from loading configuration')

	# Use configuration values (or defaults) if CLI arguments are not provided.
	# Note: Since package_manager is given a default, it will override any config value.
	if project_dir is None:
		project_dir = config.get('project_name', 'my_project')

	config_package_manager = config.get('package_manager', 'uv')
	package_manager = (
		package_manager
		if package_manager is not None
		else EnvManager(config_package_manager)
	)
	venv_name = config.get('venv_name', 'venv')
	dependencies = config.get('dependencies', [])

	logging.info('Now checking if project directory exists')
	proj_path = Path(project_dir)
	if not proj_path.exists():
		if package_manager == EnvManager.POETRY:
			create_poetry_project(project_dir, dependencies)
		elif package_manager == EnvManager.UV:
			create_uv_project(project_dir, venv_name, dependencies)
		elif package_manager == EnvManager.VIRTUALENV:
			create_virtualenv_project(project_dir, venv_name, dependencies)
		else:
			typer.echo('Invalid package manager specified.', err=True)
			logging.error('Invalid package manager specified.')
			raise typer.Exit(1)
	else:
		typer.echo(f'Project directory already exists: {project_dir}')
		logging.warning(f'Project directory already exists: {project_dir}')
		raise typer.Exit(0)

	# Create subdirectories inside the project directory.
	subdirectories = config.get('subdirectories', [])
	extra_subdirectories = config.get('extra_subdirectories', [])
	all_subdirectories = subdirectories + extra_subdirectories

	if len(all_subdirectories) > 0:
		typer.echo(f'Creating subdirectories: {all_subdirectories}')
		logging.info(f'Creating subdirectories: {all_subdirectories}')
		create_subdirectories(project_dir, all_subdirectories)
		typer.echo('Subdirectories created')
		logging.info('Subdirectories created')
	else:
		typer.echo('No subdirectories specified')
		logging.warning('No subdirectories specified')


@app.command()
def check():
	"""
	Runs the code quality and formatting checks.
	"""
	typer.echo('\nSorting imports...')
	subprocess.run(['ruff check --select I --fix'], shell=True, check=False)

	typer.echo('\nFormatting code...')
	subprocess.run(['ruff format'], shell=True, check=False)

	typer.echo('\nChecking code quality...')
	subprocess.run(['ruff check'], shell=True, check=False)
	typer.echo('Code quality completely checked')
	typer.Exit(0)


@app.command()
def check_upgrade(
	fix: bool = typer.Option(False, '--fix', help='Implement code syntax upgrade'),
):
	"""
	Checks your code syntax to see where it can be upgraded to meet the latest version.
	"""
	typer.echo('Checking code syntax')
	if fix:
		subprocess.run(['ruff check --select UP --fix'], shell=True, check=False)
		typer.echo('Code syntax upgraded')
	else:
		subprocess.run(['ruff check --select UP'], shell=True, check=False)
		typer.echo('Code syntax checked')


@app.command()
def check_codestyle():
	"""
	Checks your code style against some of the style conventions in PEP 8.
	"""
	typer.echo('Checking code style')
	subprocess.run(['ruff check --select E'], shell=True, check=False)
	typer.echo('Code style checked')


@app.command()
def format():
	"""
	Runs the formatting checks using ruff. This command does the following:
	- Sorts imports and removes unused imports.
	"""
	typer.echo('Formatting your code')
	subprocess.run(['ruff format'], shell=True, check=False)
	typer.echo('Formatting completed')


@app.command()
def gen_config():
	"""
	Generates a configuration file for the project named project_config.toml.
	"""
	typer.echo('Generating configuration file')
	config_path = 'project_config.toml'
	if os.path.exists(config_path):
		typer.echo(f'Configuration file {config_path} already exists')
		return
	config = {
		'init': {
			'project_name': 'project_name',
			'package_manager': 'virtualenv',  # options - poetry, uv, or virtualenv
			'venv_name': 'venv',
			'subdirectories': ['src', 'docs', 'tests'],
			'extra_subdirectories': [
				'data',
				'data/january',
				'data/february',
				'notebooks',
			],
			'dependencies': ['numpy', 'pandas', 'matplotlib'],
		}
	}
	with open(config_path, 'w') as f:
		toml.dump(config, f)
	typer.echo(f'Configuration file {config_path} created')


@app.command()
def document(
	docs_dir=typer.Argument('docs', help='Directory for documentation files'),
	author: str = typer.Option('Unset', help='Author name for documentation'),
) -> None:
	"""
	Generates or updates the project documentation from documentation strings.

	Notes
	-----
	Uses sphinx + reStructuredText and numpydoc.
	"""
	raise NotImplementedError('Not implemented yet')


if __name__ == '__main__':
	logger.info('Starting the application')
	app()
