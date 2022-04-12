#!/bin/bash
set -euo pipefail

# Update pip
python -m pip install --upgrade pip

# Install poetry and dependencies
pip install --user --upgrade poetry
