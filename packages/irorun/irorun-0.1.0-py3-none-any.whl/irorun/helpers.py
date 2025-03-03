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

import os
import subprocess
from collections.abc import Iterable
from contextlib import contextmanager
from enum import Enum
from pathlib import Path
from typing import Optional

import typer


class EnvManager(Enum):
	POETRY = 'poetry'
	UV = 'uv'
	VIRTUALENV = 'virtualenv'


@contextmanager
def change_dir(new_dir: str):
	"""Context manager for changing the current working directory."""
	previous_dir = os.getcwd()
	os.chdir(new_dir)
	try:
		yield
	finally:
		os.chdir(previous_dir)


def run_command(cmd: list[str], cwd: Optional[str] = None) -> None:
	"""Wrapper for subprocess.run to execute a command and handle errors."""
	try:
		subprocess.run(cmd, check=True, cwd=cwd)
	except subprocess.CalledProcessError as e:
		typer.echo(f'Error running command {cmd}: {e}', err=True)
		raise typer.Exit(1) from e


def add_dependencies(package_manager: EnvManager, dependencies: list[str]) -> None:
	"""
	Adds dependencies using the specified package manager.
	Only supports POETRY and UV.
	"""
	if package_manager not in (EnvManager.POETRY, EnvManager.UV):
		typer.echo('Invalid package manager', err=True)
		raise typer.Exit(1)
	run_command([package_manager.value, 'add'] + dependencies)
	typer.echo(f'Added dependencies: {dependencies}')


def create_poetry_project(
	project_dir: str, dependencies: Optional[list[str]] = None
) -> None:
	"""
	Creates a new Poetry project and optionally installs dependencies.
	"""
	run_command(['poetry', 'new', project_dir])
	typer.echo(f'Created new Poetry project in {project_dir}')
	with change_dir(project_dir):
		if dependencies:
			typer.echo(f'Installing dependencies: {dependencies}')
			add_dependencies(EnvManager.POETRY, dependencies)


def create_uv_project(
	project_dir: str, venv_name: str, dependencies: Optional[list[str]] = None
) -> None:
	"""
	Creates a new project with a virtual environment using uv.
	"""
	run_command(['uv', 'init', project_dir])
	with change_dir(project_dir):
		run_command(['uv', 'venv', venv_name])
		typer.echo(f'Created virtual environment "{venv_name}" in {project_dir}')
		if dependencies:
			typer.echo(f'Installing dependencies: {dependencies}')
			add_dependencies(EnvManager.UV, dependencies)


def create_virtualenv_project(
	project_dir: str, venv_name: str, dependencies: Optional[list[str]] = None
) -> None:
	"""
	Creates a new project directory and virtual environment using virtualenv.
	"""
	Path(project_dir).mkdir(parents=True, exist_ok=True)
	with change_dir(project_dir):
		run_command(['virtualenv', venv_name])

		# Determine the correct path for the pip executable in the virtual environment.
		venv_path = Path(venv_name)
		bin_dir = 'Scripts' if os.name == 'nt' else 'bin'
		pip_executable = str(venv_path / bin_dir / 'pip')

		run_command([pip_executable, 'install', '-U', 'pip'])
		if dependencies:
			typer.echo(f'Installing dependencies: {dependencies}')
			run_command([pip_executable, 'install'] + dependencies)
			typer.echo('Dependencies installed successfully.')
	typer.echo(f'Created virtual environment project in {project_dir}')


def create_subdirectories(project_dir: str, subdirectories: Iterable[str]) -> None:
	"""
	Creates subdirectories within a project directory.

	Parameters:
	project_dir: The base project directory.
	subdirectories: An iterable of subdirectory names to create under project_dir.
	"""
	base = Path(project_dir)
	for subdir in subdirectories:
		sub_path = base / subdir
		sub_path.mkdir(parents=True, exist_ok=True)
		typer.echo(f'Created subdirectory: {sub_path}')
