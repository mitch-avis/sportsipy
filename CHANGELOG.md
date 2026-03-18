# Changelog

All notable changes to sportsipy are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.8.1] — 2026-03-18

### Fixed in 0.8.1

- Synced `master` with upstream `davidjkrause/sportsipy` and incorporated the
  FBref squad ID correction commit (`Updated Premier League Team Ids`).
- Updated Premier League team ID mappings in `sportsipy/fb/squad_ids.py`
  (including `chelsea`, `liverpool`, `everton`, `west ham united`, and
  `bournemouth` aliases) to reflect current upstream values.

---

## [0.8.0] — 2026-03-18

### Added in 0.8.0

- **Camoufox bot-evasion tier** — a hardened Firefox fork (`camoufox`) is now
  tried as Tier 2 in the `get_page_source()` fetch pipeline (between
  `curl_cffi` and Playwright).  Camoufox patches fingerprint signals at the
  engine level, making it significantly more effective against Cloudflare
  Turnstile than Chromium-based stealth scripts.  Suppressed by setting
  `SPORTSIPY_DISABLE_CAMOUFOX=1`.
- `camoufox` added as an optional `[bot-evasion]` extra in `pyproject.toml`;
  install with `pip install sportsipy[bot-evasion]`.
- `--camoufox` / `--no-camoufox` CLI flags for `scripts/live_site_audit.py`.

### Removed in 0.8.0

- **Playwright stealth JS injection** — the hand-rolled
  `_PLAYWRIGHT_STEALTH_SCRIPT` blob, `_apply_playwright_stealth()`, and
  `_playwright_stealth_enabled()` have been removed.  The script was disabled
  by default, introduced fingerprint inconsistencies (e.g. `Win32` platform on
  Linux), and was ineffective against Turnstile.  Camoufox replaces this
  approach with engine-level patching.
- `--playwright-stealth` CLI flag and `SPORTSIPY_PLAYWRIGHT_STEALTH` env var
  removed from `scripts/live_site_audit.py`.

---

## [0.7.0] — 2026-01-27

### Breaking Changes

- **Dropped pandas dependency** — all `dataframe` properties now return
  [Polars](https://pola.rs) `DataFrame` objects instead of pandas `DataFrame`
  objects. Update any downstream code that calls pandas-specific methods
  (e.g. replace `.to_csv()` / `.to_pickle()` with Polars equivalents such as
  `.write_csv()` / `.write_parquet()`).
- **Minimum Python version raised to 3.12** — Python 3.7–3.11 are no longer
  supported or tested.

### Added

- **Bot-detection & live-site compatibility layer** (`utils.py`):
  - `BotChallengeError(RuntimeError)` — public exception raised when a URL
    returns a Cloudflare challenge body; carries the challenged URL for
    debuggability.
  - `_is_bot_challenge(html)` — detects Cloudflare JS-challenge responses from
    known fingerprints (`"Just a moment…"`, `challenges.cloudflare.com`,
    `"Enable JavaScript and cookies to continue"`, `cf-browser-verification`,
    `"Checking if the site connection is secure"`).
  - `_http_get()` routing function: uses `curl_cffi` (Chrome TLS fingerprint
    impersonation) when installed, falls back to `requests` automatically.
  - `_BROWSER_HEADERS` — realistic Chrome/Linux headers sent on every HTTP
    request to reduce user-agent-based blocking.
  - Playwright auto-fallback: if `curl_cffi` returns a challenge body,
    `get_page_source()` automatically retries with a headless Playwright browser
    (no `SPORTSIPY_ENABLE_PLAYWRIGHT=1` required for this path).
  - `_apply_playwright_stealth(page)` — injects anti-detection scripts into
    every Playwright page (masks `navigator.webdriver`, `chrome.runtime`,
    `permissions`, `plugins`; randomises `navigator.languages`).
  - `SPORTSIPY_DISABLE_PLAYWRIGHT=1` env var — suppresses Playwright even on
    challenge detection (useful for CI or restricted environments).
- `curl_cffi` and `playwright` added as optional `[bot-evasion]` extras in
  `pyproject.toml`; install with `pip install sportsipy[bot-evasion]`.

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

- `url_exists()` now uses GET via `get_page_source()` instead of HEAD requests,
  fixing Cloudflare 403 blocks on NCAAB and NCAAF conference/rankings pages.
  The fetched response is cached so a subsequent `pull_page()` call for the
  same URL is a no-op (eliminates double-fetch on conference iterations).
- NCAAF `SEASON_PAGE_URL` changed from `http://` to `https://` to match all
  other NCAAF constants.

- `utils.py` `local_file` path resolution now falls back to package root
  correctly, fixing fixture loading for installed packages outside the project
  directory.
- Various implicit `Optional` annotations that were silently accepting `None`
  in stat-parsing code are now properly typed and handled.

### Removed

- pandas dependency removed from `requirements.txt`.
- Sphinx documentation build infrastructure (`docs/conf.py`, `docs/Makefile`,
  all `.rst` source files) replaced by plain Markdown docs.

---

## [0.6.x and earlier]

Prior releases were managed under the original
[davidjkrause/sportsipy](https://github.com/davidjkrause/sportsipy) repository.
See that repository's history for earlier release notes.
