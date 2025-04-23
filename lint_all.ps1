Write-Host "Sorting imports with isort..."
& isort . --skip venv

Write-Host "Reformatting with black..."
& black . --exclude 'venv/'

Write-Host "Linting with flake8..."
& flake8 . --exclude=venv

Write-Host "Linting with pylint..."
& pylint . --ignore=venv
