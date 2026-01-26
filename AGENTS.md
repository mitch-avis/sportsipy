# AGENTS.md

## Overview
- `sportsipy` scrapes the sports-reference family of sites (sports-reference.com, baseball-reference, basketball-reference, pro-football-reference, hockey-reference, fbref) and exposes league-specific APIs.
- Source layout: `sportsipy/<league>/` modules for `constants`, `teams`, `schedule`, `roster`, `player`, `boxscore`; shared helpers in `sportsipy/utils.py` and `sportsipy/decorators.py`.

## Architecture Notes
- Parsing is driven by per-league `PARSING_SCHEME` dicts. Most classes iterate `self.__dict__` and call `utils.parse_field` to populate values.
- `decorators.py` provides `@int_property_decorator` and `@float_property_decorator` which convert missing values to `None` (not `0`).
- `utils.get_stats_table` strips HTML comment wrappers and returns generators of `<tr>` rows; many code paths assume non-`None` PyQuery pages.

## Environment & Tooling
- Python: `>=3.12` per `pyproject.toml`.
- Dependencies are managed via `uv`:
  - Edit `requirements.in` / `requirements-dev.in`, then run `./update_requirements.sh`.
- Formatting/linting: `black` and `ruff` (line length 100).

## Testing
- Pytest config lives in `pyproject.toml` and writes logs to `logs/pytest.log`.
- Unit tests are mostly offline: `pytest tests/unit`.
- Some integration tests still hit the network via `utils.url_exists` (HEAD requests) and can be rate-limited (429), especially on pro-football-reference.
  - Prefer offline fixtures where available (see `tests/integration/**` HTML fixtures).
  - If running full integration, be mindful of network flakiness and server limits.

## Versioning & Packaging
- Keep `VERSION` and `pyproject.toml` `version` in sync; `dev-version-bump` only updates `VERSION`.
- `README.rst` exists but `pyproject.toml` references `README.md` (fix if packaging metadata matters).
- README build instructions still mention `setup.py` even though the build backend is `hatchling`.

## Docs
- Sphinx docs live in `docs/`; update them with API changes or new fields.

## Safety/Respectful Scraping
- There is a `RATE_LIMIT_INTERVAL` constant but no enforced sleep; avoid adding tight loops that hit live endpoints without throttling.
