# AI Instructions — sportsipy (Python)

## Project Overview

sportsipy is a Python library that scrapes sports statistics from the sports-reference.com family of
sites (PFR, Basketball-Reference, Baseball-Reference, Hockey-Reference, FBref, and college sports
sections). This repository is maintained on the `big-update` branch and is focused on build
modernization, type-hinting adoption, offline fixture testing, and a pandas-to-polars migration.

## Tech Stack

- Python 3.12+
- Build system: hatchling via `pyproject.toml`
- Runtime libraries: `requests`, `pyquery`, `lxml`, `numpy`, `pandas` (migrating to `polars`)
- Developer tooling: `uv`, `pytest`, `pytest-cov`, `ruff`, `flexmock`
- Type checking direction: `pyright` (incremental adoption)

## Python Environment Requirement

All sportsipy Python tooling commands must run from the virtual environment at `./sportsipy/.venv/`.
This includes `python`, `uv`, `pip`, `ruff`, `pytest`, `pyright`, and related tools.

## Build & Run

```bash
# Install dependencies
uv pip install -r requirements.txt -r requirements-dev.txt

# Build package artifacts
python -m build

# Editable install
pip install -e .
```

## Test Commands

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests (offline fixtures, network blocked)
pytest tests/integration/ -v

# Unit + integration
pytest tests/unit/ tests/integration/ -v

# Coverage
pytest tests/unit/ tests/integration/ --cov=sportsipy --cov-report=term-missing
```

## Lint, Format, and Type Check

```bash
# Format
ruff format . --check
ruff format .

# Lint — rules: B (bugbear), C4 (comprehensions), D (pydocstyle), E, F, I (isort),
#         N (naming), S (bandit security), SIM (simplify), UP (pyupgrade),
#         W, NPY, PGH — see pyproject.toml for full config
ruff check .
ruff check . --fix

# Type check (as configured)
pyright sportsipy/
```

## Repository Structure

- `sportsipy/`: main package with shared modules and per-sport implementations.
- `sportsipy/utils.py`: core HTTP fetch, retries, rate limiting, HTML comment stripping, parsing,
  response caching, and fixture loading.
- `sportsipy/{sport}/`: sport modules with `constants.py`, `teams.py`, `schedule.py`, `boxscore.py`,
  `roster.py`, `player.py`, and `{sport}_utils.py`.
- `sportsipy/fb/`: soccer module variant with `team.py`, `league_ids.py`, and `squad_ids.py`.
- `tests/unit/`: mocked tests, primarily with `flexmock`.
- `tests/integration/`: fixture-driven integration tests with network blocked.
- `tests/fixtures/url_map.json`: URL-to-fixture mapping.
- `scripts/capture_fixtures.py`: fixture capture and registration helper.

## Core Architecture Patterns

### Parsing scheme mapping

Each sport defines `PARSING_SCHEME` dictionaries in `constants.py` mapping attribute names to CSS
selectors. Most scraping breakages are fixed by updating these selectors.

### Shared parsing utilities

`utils.parse_field()` and related helpers apply parsing schemes to HTML rows and normalize values.

### Property decorators

`int_property_decorator` and `float_property_decorator` coerce property values and return `None` on
missing or invalid data instead of raising parse exceptions.

### HTML comment stripping

`remove_html_comment_tags()` is required because Sports-Reference often wraps tables in HTML comments.

### Rate limiting and retries

Requests are rate-limited to a minimum 3-second interval and should honor HTTP 429 `Retry-After`
headers.

## Testing and Data Collection Rules

- Never make live requests to sports-reference.com in CI or automated tests.
- Use fixture mode for integration tests (`SPORTSIPY_OFFLINE=1`).
- When testing a new URL, capture fixtures with `scripts/capture_fixtures.py` and update
  `tests/fixtures/url_map.json`.
- Verify parsing changes against fixture HTML before assuming selector correctness.

## Coding Standards

- Use `from __future__ import annotations` in all new or modified modules.
- Annotate function parameters, return types, and key instance attributes.
- Prefer `X | None` over `Optional[X]`.
- Write docstrings for **all** public items: modules, packages, classes, `__init__` methods,
  public methods, and public functions (enforced by ruff `D` rules / pydocstyle).
- Use NumPy-style docstrings. The first line is a brief **imperative** summary ending with a
  period, e.g. `"""Return the team abbreviation."""`. Separate a multi-line body from the
  summary with a blank line. Single-sentence docstrings must fit on one line.
- Use `Parameters`, `Returns`, `Raises`, and other NumPy section headers for extended docs.
- Do not import camelcase symbols under a lowercase alias (N813); e.g. use `PyQuery` not `pq`.
- Catch specific exceptions; do not use bare `except:`.
- Return `None` for missing data (not `0` or empty strings).
- Keep line length at 100 characters.

## Import Style Preference

- Prefer **absolute imports** in all Python modules and tests (for example,
  `from sportsipy import utils` and `from sportsipy.nba.schedule import Schedule`).
- Do not introduce new relative imports (`from .` / `from ..`) unless explicitly requested.

## Lint and Type Ignore Preference

- Avoid suppression directives such as `# pyright: ignore`, `# type: ignore`, `# noqa`,
  `# pylint: disable`, and similar comment-based bypasses.
- First fix issues in the correct, Pythonic way (improve types, refactor logic, tighten
  interfaces, or adjust tests).
- Only use ignore directives when there is no practical alternative, and keep them minimal,
  targeted, and clearly justified.

## Current Modernization Focus

- Complete type coverage across all sport modules.
- Complete pandas-to-polars migration while preserving behavior.
- Modernize CI (Python 3.12+, `ruff`, `ruff format --check .`, `python -m build`, test matrix updates).
- Standardize integration tests on fixture mode and reduce residual mixed mocking patterns.
