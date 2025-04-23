#!/bin/bash

echo "Sorting imports with isort..."
isort . --skip venv

echo "Reformatting with black..."
black . --exclude 'venv/'

echo "Linting with flake8..."
flake8 . --exclude=venv

echo "Linting with pylint..."
pylint . --ignore=venv
