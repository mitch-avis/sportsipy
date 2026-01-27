# TODO List

## TODO: Offline Integration Tests

### Goal (Offline Integration Tests)

Make integration tests fully offline and deterministic while keeping current coverage.

### Status

In progress: offline env/fixture registry scaffolding added. Tests not rewired yet.

### Plan (Offline Integration Tests)

1) Inventory live requests
   - Locate all paths calling `utils.url_exists`, `utils.pull_page`, or `requests.get/head`.
   - Tag tests that still hit the network (see `logs/pytest.log` for 429s).
2) Add fixture storage
   - Create a shared fixture directory (e.g., `tests/fixtures/`).
   - Store HTML snapshots keyed by full URL and a stable filename mapping.
3) Add offline switch
   - Add an env var like `SPORTSIPY_OFFLINE=1` that forces offline mode in `utils`.
   - In offline mode, `url_exists` checks a fixture index; `pull_page` reads fixtures.
4) Build a URL-to-fixture registry
   - Implement a small registry (JSON or Python dict) mapping URLs to fixture files.
   - Add a helper to resolve unknown URLs to a clear error with next steps.
5) Update tests
   - Replace direct `requests.get/head` patches with fixture-based helpers.
   - Ensure every integration test uses fixtures (no real HTTP).
6) Add capture tooling (optional but helpful)
   - Add a script to record fixtures from live URLs, gated behind explicit opt-in.
7) Add CI guardrails
   - Add a test that fails if network calls occur during integration tests.
   - Document offline mode and fixture update steps in `CONTRIBUTING.md`.

## TODO: Throttling / Retry / Caching

### Constraints

- Respect >= 3s delay between requests (20 requests/minute max).
- Scraping only; no API access.

### Status

Mostly complete: centralized request helper with rate limiting, retries, caching,
and offline gating added in `sportsipy/utils.py`. Remaining work includes
tests + Sphinx doc updates.

### Plan (Throttling / Retry / Caching)

1) Centralize HTTP access
   - Route all HTTP through a single utility (e.g., `utils.fetch`).
   - Avoid direct `requests.get/head` in league modules.
2) Rate limiting
   - Implement a simple global rate limiter (monotonic clock).
   - Enforce >= 3s between requests; add jitter (e.g., +/- 0.2s).
   - Ensure the limiter is shared across threads/processes if applicable.
3) Retries and backoff
   - Retry on 429/5xx with exponential backoff.
   - Respect `Retry-After` if present.
   - Cap retries to avoid long hangs; log when retries occur.
4) Caching
   - Add optional cache layer keyed by URL (memory + disk).
   - Prefer a small on-disk cache (e.g., `requests-cache` or simple file cache).
   - Provide TTL defaults and allow opt-out via env vars.
5) Configuration
   - Expose settings via environment variables:
     - `SPORTSIPY_RATE_LIMIT_SECONDS` (default 3.5)
     - `SPORTSIPY_CACHE_DIR`
     - `SPORTSIPY_CACHE_TTL_SECONDS`
     - `SPORTSIPY_MAX_RETRIES`
6) Tests
   - Unit tests for limiter timing and retry behavior (mock time).
   - Integration tests that verify no more than 1 request/3s in offline mode.
7) Documentation
   - Add a short "Responsible scraping" section in `README.md`.

## TODO: Convert README.rst to README.md + Update GitHub Links

### Goal (Convert README.rst to README.md + Update GitHub Links)

Move the project README to Markdown and point the primary repo links at the
current fork while preserving credit to the original and prior fork.

### Status

Completed: `README.md` created, `README.rst` removed, links updated, and
`pyproject.toml` updated to reference Markdown.

### Plan (Convert README.rst to README.md + Update GitHub Links)

1) Convert `README.rst` → `README.md`
   - Update headings, code blocks, links, and inline code to valid Markdown.
   - Preserve the existing structure and examples.
2) Update GitHub references
   - Primary fork: `github.com/mitch-avis/sportsipy`.
   - Credit section: link the original repo (`github.com/roclark/sportsipy`)
     and the intermediate fork (`github.com/davidjkrause/sportsipy`).
3) Packaging metadata update
   - Update `pyproject.toml` `readme` to `README.md` once conversion is done.
   - Remove or archive `README.rst` if it is no longer used.
4) Documentation touch-ups
   - Check docs or contributor docs for README references and update them.

## TODO: Fix Failing Tests (from `logs/pytest.log` on 2026-01-26)

### Goal (Fix Failing Tests)

Resolve all failing unit + integration tests and ensure offline/ratelimit
changes do not reintroduce regressions.

### Status

Completed for the latest run: all tests pass (see most recent `pytest` run).

### Observed Failures (grouped)

1) Invalid URL handling → `pq(None)` / `NoneType` errors
   - Unit: `test_*_boxscore` invalid URL returns `None` (MLB/NBA/NCAAB/NCAAF/NHL).
   - Unit: `test_*_roster` invalid URL returns `None` (NBA/NCAAB/NCAAF/NHL/MLB).
   - Unit: FB `team/schedule/roster` invalid page errors.
   - Integration: bad URL tests for conferences/rankings/rosters.
2) Date/season logic mismatch
   - `test__find_year_for_season_returns_correct_year` (returns 2017 vs 2018).
3) URL exception handling
   - `test_invalid_url_exception_returns_false` expects `url_exists` to return `False`.
4) NBA 2020 season fallback
   - `test_nba_2020_season_default_to_previous` uses 2021 → should fall back to 2020.
5) Default-year fallback in integration
   - `TestNBAScheduleInvalidError` and `TestNCAABIntegrationInvalidYear` expect
     invalid defaults to revert to previous year.
6) Playwright fallback noise/errors
   - `Playwright fetch failed` in logs; should not break tests or trigger in offline mode.

### Plan (Fix Failing Tests)

1) Fix core utils first (blocks most failures)
   - Guard `utils.get_page_source` and `utils.pq` usage so `None` never reaches PyQuery.
   - Ensure callers return `None` or raise `ValueError` as tests expect.
   - Make `url_exists` catch generic exceptions (not just `RequestException`).
2) Align season logic with tests
   - Update `find_year_for_season` to match expected month boundaries (start-1 rule).
3) Fix NBA season fallback logic
   - Avoid `pq(None)` in `_retrieve_all_teams` and fall back cleanly when 2021 is invalid.
4) Repair league modules with invalid-page handling
   - FB team/roster/schedule: exit early on `None` docs.
   - Boxscore/roster classes: return `None` for invalid URLs or 404.
   - Conferences/rankings: raise `ValueError` when pages missing.
5) Address integration failures after offline switch work
   - Offline mode from earlier TODO should eliminate unexpected live hits.
   - Re-run `pytest` and re-check `logs/pytest.log` for remaining failures.
6) Gate Playwright fallback
   - Only attempt Playwright when explicitly enabled (env var) and available,
     to avoid noisy failures during tests.
