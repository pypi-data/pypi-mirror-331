# irorun

[![PyPI version](https://img.shields.io/pypi/v/irorun.svg)](https://pypi.org/project/irorun/)
[![License](https://img.shields.io/pypi/l/irorun.svg)](https://github.com/yourusername/irorun/blob/main/LICENSE)
[![Python Version](https://img.shields.io/pypi/pyversions/irorun.svg)](https://www.python.org/downloads/)

**irorun** is a unified command-line tool designed specifically for research teams—especially in physics—who need to maintain high-quality Python code without the overhead of mastering complex development tools. Born out of the challenges faced by scientists who prioritize research over extensive software engineering, irorun streamlines project bootstrapping by integrating environment management, code quality checks, and formatting into a single, user-friendly interface. By automating the setup of virtual environments and the orchestration of tools like ruff, pylint, and sphinx (with plans for documentation), irorun aims to empower researchers to focus on their scientific pursuits while ensuring their code remains robust, scalable, and collaborative across different platforms.

## Features

- **Project Bootstrapping:**  
  Quickly create a new project directory structure along with standard subdirectories.
  
- **Environment Management:**  
  Supports multiple environment managers such as Poetry, uv, and virtualenv to create virtual environments.
  
- **Integrated Code Quality:**  
  Run linters, formatters, and static code analysis (using tools like Ruff) with one command.
  
- **Configurable Setup:**  
  Customize your project scaffold via an editable configuration file (`project_config.toml`).
  
- **Extensible & Modular:**  
  Easily extend functionality and integrate additional tools as your workflow evolves.

## Installation

Install irorun from PyPI:

```bash
pip install irorun
```

Or clone the repository and install locally:

```bash
git clone https://github.com/lere01/irorun.git
cd irorun
pip install .
```

## Usage

### Bootstrapping a New Project

Create a new project using the default configuration - ```bash irorun init```. Or specify a project directory and select an environment manager - ```bash irorun init my_project --package-manager poetry```. There are currently three environment managers supported: `Poetry`, `uv`, and `virtualenv`.

## Code Quality & Formatting

### Check your code with a single command

```bash irorun check```

### Upgrade your code syntax (with optional fixes)

```irorun check_upgrade --fix```

### Check your code style against some [PEP8](https://www.python.org/dev/peps/pep-0008/) guidelines

```bash irorun check_codestyle```

### Format your code

```bash irorun format```

### Generate documentation from your docstrings (**Future Feature**)

### Generate a sample configuration file to customize your project setup

```bash irorun gen-config```

Edit project_config.toml to customize project scaffolding and setup. An example configuration:

```toml
project_directory = "project-name"
subdirectories = ["src", "docs", "tests"]
extra_subdirectories = []  # Any extra subdirectories to create under the project directory
package_manager = "poetry" # Options: ["poetry", "uv", "virtualenv"]
venv_name = "venv"

dependencies = ["numpy", "pandas", "matplotlib"]
```

## Testing and Coverage

### Run tests

```bash pytest tests/ --maxfail=[your-choice] --disable-warnings -q```

### Generate coverage report

```bash pytest tests/ --cov=src/irorun --cov-report=term-missing```
