@echo off

REM Upgrade pip to the latest version for optimal performance
python -m pip install --upgrade pip

REM Install pip-tools if not already installed
pip install --upgrade pip-tools

REM Compile requirements.in to requirements.txt, upgrading all packages
pip-compile --upgrade requirements.in --output-file requirements.txt --strip-extras

REM Install all other dependencies from the lock file
pip install -Ur requirements.txt

REM Compile requirements-dev.in to requirements-dev.txt, upgrading all packages
pip-compile --upgrade requirements-dev.in --output-file requirements-dev.txt --strip-extras

REM Install all other dependencies from the lock file
pip install -Ur requirements-dev.txt
