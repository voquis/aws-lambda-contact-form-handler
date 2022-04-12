#!/bin/bash
# Packages lambda with dependencies per:
# https://docs.aws.amazon.com/lambda/latest/dg/python-package.html#python-package-create-package-with-dependency
set -euo pipefail

# Install dependencies, excluding development dependencies
poetry install --no-dev --no-root

# Build distributable wheel
poetry build -f wheel

# Install wheel to local package path
pip install --target build dist/* --upgrade

# remove existing zip if exists
rm -f lambda.zip

# Zip the contents of the local package
cd build
zip -r ../lambda.zip .

# Add the lambda handler file to the zip
cd ..
zip -g lambda.zip app.py
