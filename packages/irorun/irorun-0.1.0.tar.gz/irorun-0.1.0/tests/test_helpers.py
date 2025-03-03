import os
import subprocess
import sys
from pathlib import Path

# Add the src directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent / 'src'))

import pytest
import typer

from irorun.helpers import (
	EnvManager,
	add_dependencies,
	change_dir,
	create_subdirectories,
	create_virtualenv_project,
	run_command,
)

# --- Helper for recording run_command calls ---


class DummyRun:
	def __init__(self):
		self.calls = []

	def __call__(self, cmd, cwd=None):
		self.calls.append((cmd, cwd))


# Dummy implementations to record calls


@pytest.fixture(autouse=True)
def reset_dummy_run():
	# This fixture runs before each test
	dummy = DummyRun()
	yield dummy
	# No teardown necessary


# --- Tests for change_dir ---


def test_change_dir(tmp_path):
	original_dir = os.getcwd()
	new_dir = tmp_path / 'subdir'
	new_dir.mkdir()
	with change_dir(str(new_dir)):
		assert os.getcwd() == str(new_dir)
	# After the context manager, the working directory should be restored.
	assert os.getcwd() == original_dir


# --- Tests for run_command ---


def test_run_command_success(monkeypatch):
	# Monkeypatch subprocess.run to simply return without error.
	monkeypatch.setattr(subprocess, 'run', lambda cmd, check, cwd=None: None)
	# run_command should not raise an exception
	run_command(['echo', 'hello'])


def test_run_command_failure(monkeypatch):
	def fake_run(cmd, check, cwd=None):
		raise subprocess.CalledProcessError(returncode=1, cmd=cmd, output='error')

	monkeypatch.setattr(subprocess, 'run', fake_run)
	with pytest.raises(typer.Exit):
		run_command(['false', 'command'])


# --- Tests for add_dependencies ---


def test_add_dependencies_valid(monkeypatch):
	dummy = DummyRun()
	monkeypatch.setattr('irorun.helpers.run_command', dummy)
	add_dependencies(EnvManager.POETRY, ['dep1', 'dep2'])
	expected_cmd = [EnvManager.POETRY.value, 'add', 'dep1', 'dep2']
	assert dummy.calls[0][0] == expected_cmd


def test_add_dependencies_invalid():
	with pytest.raises(typer.Exit):
		add_dependencies(EnvManager.VIRTUALENV, ['dep1'])


# --- Test for create_subdirectories ---


def test_create_subdirectories(tmp_path, capsys):
	project_dir = tmp_path / 'project'
	project_dir.mkdir()
	subdirs = ['dir1', 'dir2/nested']
	create_subdirectories(str(project_dir), subdirs)
	for sub in subdirs:
		sub_path = project_dir / sub
		assert sub_path.is_dir()
	output = capsys.readouterr().out
	for sub in subdirs:
		expected_line = f'Created subdirectory: {project_dir / sub}'
		assert expected_line in output


# --- Tests for project creation functions ---
# We override run_command so that no real commands are executed. Instead, we record the calls.


@pytest.fixture
def dummy_run(monkeypatch):
	dummy = DummyRun()
	monkeypatch.setattr('irorun.helpers.run_command', dummy)
	return dummy


def test_create_virtualenv_project(dummy_run, tmp_path, capsys):
	project_dir = str(tmp_path / 'virtualenv_project')
	venv_name = 'venv'
	create_virtualenv_project(project_dir, venv_name, ['depC'])
	# Verify the project directory was created.
	assert Path(project_dir).is_dir()
	# We expect a command that creates the virtualenv and pip upgrade/install commands.
	pip_calls = [cmd for (cmd, _) in dummy_run.calls if 'pip' in cmd[0]]
	assert any('install' in ' '.join(cmd) for cmd in pip_calls)
