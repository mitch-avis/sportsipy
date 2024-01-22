#!/bin/bash

echo "Sorting imports with isort..."
isort .
isort tests/*.py

echo "Reformatting with black..."
black .
black tests/*.py

echo "Linting with flake8..."
flake8 .
flake8 tests/*.py

echo "Linting with pylint..."
pylint sportsipy/
pylint tests/*.py
