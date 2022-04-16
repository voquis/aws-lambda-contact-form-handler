#!/bin/bash
set -euo pipefail

# Install dependencies, including development dependencies
poetry install --no-root

PACKAGE_NAME="app_handler"

# Run linting checks on package, tests and app entrypoint
poetry run pylint "${PACKAGE_NAME}" tests app.py

# Run tests and generate test coverage report
poetry run coverage run -m pytest tests/unit
poetry run coverage report --omit="tests/*"
poetry run coverage html --omit="tests*"
poetry run coverage xml --omit="tests/*"
