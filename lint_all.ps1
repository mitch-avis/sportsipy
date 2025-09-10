Write-Host "Sorting imports with isort..."
& isort . --skip venv --skip tests --skip docs --skip build --skip dist

Write-Host "Reformatting with black..."
& black . --exclude 'venv/|tests/|docs/|build/|dist/' 

Write-Host "Linting with flake8..."
& flake8 . --exclude=venv,tests,docs,build,dist

Write-Host "Linting with pylint..."
& pylint . --ignore=venv,tests,docs,build,dist
