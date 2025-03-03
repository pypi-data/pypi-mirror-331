Testing and Coverage
====================

A robust test suite is vital for maintaining irorun. This section details how to run tests and generate coverage reports.

Running Tests
-------------
irorun uses pytest as its testing framework. To run the full test suite, use:

.. code-block:: bash

   pytest

For more detailed output, add the verbose flag:

.. code-block:: bash

   pytest -v

Coverage Reporting
------------------
The project uses pytest-cov to measure test coverage.

**Terminal Summary:**

.. code-block:: bash

   pytest --cov=irorun --cov-report=term-missing

**HTML Report:**

.. code-block:: bash

   pytest --cov=irorun --cov-report=html

Then open ``htmlcov/index.html`` in your browser for a detailed report.

Continuous Integration
----------------------
It is recommended to integrate testing and coverage into your CI/CD pipeline (e.g., using GitHub Actions) to ensure high-quality code and prevent regressions.