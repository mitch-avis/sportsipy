# Testing

Sportsipy contains a testing suite which aims to test all major portions of
code for proper functionality.

## Running the Tests

Ensure the virtual environment is active and all requirements are installed:

```bash
uv venv
uv pip install -r requirements.txt -r requirements-dev.txt
```

Run the unit tests:

```bash
pytest tests/unit/ -v
```

Run the integration tests (uses offline HTML fixtures — no network access):

```bash
pytest tests/integration/ -v
```

Run both suites together with coverage:

```bash
pytest tests/unit/ tests/integration/ --cov=sportsipy --cov-report=term-missing
```

## What to Expect

Successful output ends with a summary similar to:

```text
799 passed in 137.28s (0:02:17)
```

If a test fails, it will show the failed test name and traceback in the output.
Ensure you have the latest version of code and are in a supported environment
(Python 3.12+). Otherwise, create an issue on GitHub to get it resolved.

## Development Checks

Before committing, run the full validation suite in order:

```bash
ruff format .
ruff check .
pyright .
pytest tests/unit/ tests/integration/ -q
```

All four must pass cleanly before merging or sharing code on the `big-update`
branch.

## Offline Fixture System

Integration tests run entirely offline using captured HTML fixtures. The
fixtures are stored in `tests/integration/` and mapped to URLs via
`tests/integration/url_map.json`.

To capture new fixtures from the live site:

```bash
python scripts/capture_fixtures.py --url <URL> --name <fixture-name>
```

See `scripts/capture_fixtures.py --help` for full usage.
