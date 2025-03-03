import sys
from contextlib import contextmanager
from pathlib import Path

# Add the src directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent / 'src'))

import pytest

from irorun.helpers import (
	EnvManager,
	create_poetry_project,
	create_uv_project,
)


class DummyRecorder:
	def __init__(self):
		self.calls = []

	def record(self, label, *args, **kwargs):
		self.calls.append((label, args, kwargs))


@contextmanager
def dummy_change_dir(new_dir: str):
	# A no-op context manager that does not change directories.
	yield


@pytest.fixture
def dummy_recorder():
	return DummyRecorder()


def test_create_poetry_project(monkeypatch, tmp_path, capsys, dummy_recorder):
	# Create dummy functions that record calls
	def dummy_run_command(cmd, cwd=None):
		dummy_recorder.record('run_command', cmd, cwd)

	def dummy_add_dependencies(pm, deps):
		dummy_recorder.record('add_dependencies', pm, deps)

	# Monkey-patch the functions in the module.
	monkeypatch.setattr('irorun.helpers.run_command', dummy_run_command)
	monkeypatch.setattr('irorun.helpers.add_dependencies', dummy_add_dependencies)
	monkeypatch.setattr('irorun.helpers.change_dir', dummy_change_dir)

	# Prepare a fake project directory (using tmp_path ensures it's isolated)
	project_dir = str(tmp_path / 'poetry_project')
	dependencies = ['dep1', 'dep2']

	# Call create_poetry_project with dependencies.
	create_poetry_project(project_dir, dependencies)

	# Capture output so we can check typer.echo calls (if needed)
	_ = capsys.readouterr().out

	# Verify that run_command was called with the correct command.
	assert dummy_recorder.calls[0][0] == 'run_command'
	assert dummy_recorder.calls[0][1][0] == ['poetry', 'new', project_dir]

	# Verify that add_dependencies was called with the expected arguments.
	# Note: Since the code uses "if dependencies:" in the change_dir block,
	# we expect an "add_dependencies" call.
	found = False
	for call in dummy_recorder.calls:
		if call[0] == 'add_dependencies':
			found = True
			# The first argument should be EnvManager.POETRY and the second should be our dependencies list.
			assert call[1][0] == EnvManager.POETRY
			assert call[1][1] == dependencies
	assert found, 'add_dependencies was not called'


def test_create_uv_project(monkeypatch, tmp_path, dummy_recorder, capsys):
	# Define dummy versions of run_command and add_dependencies that record calls.
	def dummy_run_command(cmd, cwd=None):
		dummy_recorder.record('run_command', cmd, cwd)

	def dummy_add_dependencies(pm, deps):
		dummy_recorder.record('add_dependencies', pm, deps)

	# Monkey-patch the helpers to use our dummy functions.
	monkeypatch.setattr('irorun.helpers.run_command', dummy_run_command)
	monkeypatch.setattr('irorun.helpers.add_dependencies', dummy_add_dependencies)
	monkeypatch.setattr('irorun.helpers.change_dir', dummy_change_dir)

	# Create a temporary project directory.
	project_dir = str(tmp_path / 'uv_project')
	venv_name = 'myvenv'
	dependencies = ['depA', 'depB']

	# Call the function under test.
	create_uv_project(project_dir, venv_name, dependencies)

	# Check that the first call is to run the 'uv init' command.
	assert dummy_recorder.calls[0][0] == 'run_command'
	assert dummy_recorder.calls[0][1][0] == ['uv', 'init', project_dir]

	# Check that the next call (inside the dummy change_dir context) is the 'uv venv' command.
	assert dummy_recorder.calls[1][0] == 'run_command'
	assert dummy_recorder.calls[1][1][0] == ['uv', 'venv', venv_name]

	# Check that add_dependencies is called if dependencies are provided.
	found = False
	for call in dummy_recorder.calls:
		if call[0] == 'add_dependencies':
			found = True
			assert call[1][0] == EnvManager.UV
			assert call[1][1] == dependencies
	assert found, 'Expected add_dependencies call was not found.'

	# Optionally, check the output captured by capsys (if any echo messages were printed).
	output = capsys.readouterr().out
	assert f'Created virtual environment "{venv_name}" in {project_dir}' in output
	assert f'Installing dependencies: {dependencies}' in output
