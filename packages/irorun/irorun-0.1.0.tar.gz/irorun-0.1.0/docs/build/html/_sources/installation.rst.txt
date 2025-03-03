Installation and Development Setup
====================================

This section explains how to set up a development environment for irorun.

Requirements
------------
- Python 3.11 or later
- pip (or your preferred package manager)
- Virtual environment tools (e.g., virtualenv, Poetry, or uv)

Steps to Set Up Your Environment
--------------------------------

1. **Clone the Repository:**

   .. code-block:: bash

      git clone https://github.com/yourusername/irorun.git
      cd irorun

2. **Create a Virtual Environment:**

   Choose your preferred method. For example, using virtualenv:

   .. code-block:: bash

      python -m virtualenv venv
      source venv/bin/activate   # On Windows: venv\Scripts\activate

   Or with Poetry:

   .. code-block:: bash

      poetry install

3. **Install in Editable Mode:**

   To facilitate development, install irorun in editable mode:

   .. code-block:: bash

      pip install -e .

4. **Install Development Dependencies:**

   If you maintain a separate file (e.g., requirements-dev.txt) for development tools:

   .. code-block:: bash

      pip install -r requirements-dev.txt

5. **Verify Installation:**

   Run the following to ensure the CLI is working:

   .. code-block:: bash

      irorun --help

This should display the list of available commands and options.