#!/bin/bash

echo "Sorting imports with isort..."
isort . --skip venv --skip tests --skip docs --skip build --skip dist

echo "Reformatting with black..."
black . --exclude 'venv/|tests/|docs/|build/|dist/' 

echo "Linting with flake8..."
flake8 . --exclude=venv,tests,docs,build,dist

echo "Linting with pylint..."
pylint . --ignore=venv,tests,docs,build,dist
