# Changelog

All notable changes to sportsipy are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.7.0] — Unreleased

### Breaking Changes

- **Dropped pandas dependency** — all `dataframe` properties now return
  [Polars](https://pola.rs) `DataFrame` objects instead of pandas `DataFrame`
  objects. Update any downstream code that calls pandas-specific methods
  (e.g. replace `.to_csv()` / `.to_pickle()` with Polars equivalents such as
  `.write_csv()` / `.write_parquet()`).
- **Minimum Python version raised to 3.12** — Python 3.7–3.11 are no longer
  supported or tested.

### Added

- Full type annotations (PEP 484 / PEP 526) across all sport modules: `fb`,
  `mlb`, `nba`, `ncaab`, `ncaaf`, `nfl`, `nhl`, and shared `utils` /
  `decorators`. Types are verified by `pyright` in strict-ish mode.
- `__repr__` and `__str__` on every public class, including `AbstractPlayer`,
  `BoxscorePlayer`, `CFPRankings`, `CoachesRankings`, and all `Team` /
  `Teams` / `Roster` / `Schedule` / `Boxscore` / `Boxscores` classes.
- Polars `DataFrame` return type on all `.dataframe` and `.dataframe_extended`
  properties.
- `py.typed` marker file — sportsipy is now a typed package (PEP 561).
- Structured logging via the standard `logging` module throughout all modules
  (replaces bare `print()` calls).
- `warnings.warn()` for soft-deprecation paths and missing-data notices
  (replaces silent no-ops).
- Comprehensive unit and integration test suite with offline fixtures — no
  live network requests needed to run tests.
- Branch-level test coverage for edge cases in `Schedule`, `Roster`, and
  `Boxscore` modules.
- Markdown documentation for all sport packages (`docs/*.md`), replacing the
  previous Sphinx RST docs. Includes updated examples using Polars and current
  tooling (`uv`, `ruff`, `pyright`).

### Changed

- Migrated build tooling from pip + setuptools to
  [uv](https://docs.astral.sh/uv/) + [pyproject.toml](pyproject.toml).
- Replaced Black + isort with [Ruff](https://docs.astral.sh/ruff/) for both
  formatting and linting.
- Updated CI pipeline (`pushtests.yml`) to Python 3.12 / 3.13, modern action
  versions (`actions/checkout@v4`, `actions/setup-python@v5`,
  `astral-sh/setup-uv@v5`), and Codecov integration.
- Updated exhaustive tests CI (`exhaustive.yml`) from Python 3.7/3.8 to 3.12/3.13
  with matching action version upgrades.
- Tightened exception handling — all bare `except:` and `except Exception:`
  clauses replaced with specific exception types.
- Refreshed test fixtures for NHL, NFL, and NCAAF to reflect current
  Sports-Reference HTML structure.
- Updated `README.md` and `CONTRIBUTING.md` for the new tooling, Python
  requirements, and development workflow.

### Fixed

- `utils.py` `local_file` path resolution now falls back to package root
  correctly, fixing fixture loading for installed packages outside the project
  directory.
- Various implicit `Optional` annotations that were silently accepting `None`
  in stat-parsing code are now properly typed and handled.

### Removed

- pandas dependency removed from `requirements.txt`.
- Sphinx documentation build infrastructure (`docs/conf.py`, `docs/Makefile`,
  all `.rst` source files) replaced by plain Markdown docs.
- AI instruction/context files removed from repository root.

---

## [0.6.x and earlier]

Prior releases were managed under the original
[davidjkrause/sportsipy](https://github.com/davidjkrause/sportsipy) repository.
See that repository's history for earlier release notes.
