#!/bin/bash
set -euo pipefail

# Install dependencies, including development dependencies
poetry install --no-root

PACKAGE_NAME="example"

# Run linting checks on package, tests and app entrypoint
poetry run pylint "${PACKAGE_NAME}" tests app.py

# Run tests and generate test coverage report
poetry run coverage run -m pytest
poetry run coverage report
poetry run coverage html
poetry run coverage xml
