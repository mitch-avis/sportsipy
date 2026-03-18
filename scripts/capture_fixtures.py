#!/usr/bin/env python3
"""Provide utilities for capture fixtures."""

import argparse
import json
import logging
import os
import re
import time
from collections.abc import Iterable
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests

CANONICAL_URL_RE = re.compile(
    r'rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', re.IGNORECASE
)
OG_URL_RE = re.compile(r'property=["\']og:url["\'][^>]*content=["\']([^"\']+)["\']', re.IGNORECASE)
VALID_HOST_SNIPPETS = (
    "sports-reference.com",
    "baseball-reference.com",
    "basketball-reference.com",
    "pro-football-reference.com",
    "hockey-reference.com",
    "fbref.com",
)
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

LOGGER = logging.getLogger(__name__)


def _load_map(path: Path) -> dict[str, str] | list[dict[str, str]]:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _save_map(path: Path, data: dict[str, str] | list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False), encoding="utf-8")


def _is_valid_fixture_path(rel_path: Path) -> bool:
    return "__pycache__" not in rel_path.as_posix().lower() and rel_path.suffix.lower() in {
        ".html",
        ".htm",
        ".shtml",
    }


def _extract_url_from_html(path: Path) -> str | None:
    try:
        html = path.read_text(encoding="utf-8")
    except OSError:
        return None
    match = CANONICAL_URL_RE.search(html)
    if match:
        return match.group(1).strip()
    match = OG_URL_RE.search(html)
    if match:
        return match.group(1).strip()
    return None


def _normalize_candidate_url(candidate: str | None, *, base_url: str | None = None) -> str | None:
    if not candidate:
        return None
    value = candidate.strip()
    if not value:
        return None
    if value.startswith("//"):
        value = f"https:{value}"
    elif "http://" not in value and "https://" not in value:
        if base_url and (value.startswith("/") or "?" in value or "/" in value):
            if re.match(
                r"^(boxscores|boxes|cbb/|cfb/|teams/|players/|leagues/|years/|en/|squads/)",
                value,
            ):
                value = f"/{value.lstrip('/')}"
            value = urljoin(base_url, value)
            if any(host in value for host in VALID_HOST_SNIPPETS):
                return value
        if any(host in value for host in VALID_HOST_SNIPPETS):
            value = f"https://{value.lstrip('/')}"
        else:
            return None
    if not any(host in value for host in VALID_HOST_SNIPPETS):
        return None
    return value


def _is_specific_fragment(value: str) -> bool:
    return value.startswith("/") or "?" in value or "/" in value


def _prefer_contains_url(canonical_url: str, contains_url: str) -> bool:
    canonical = canonical_url.rstrip("/")
    if canonical.endswith("/boxscores"):
        return True
    return (
        "baseball-reference.com" in canonical
        and "/boxes/" in canonical
        and "?year=" in contains_url
    )


def _entry_urls(entry: dict[str, Any], fixtures_dir: Path) -> list[str]:
    rel_path = _entry_path(entry)
    if rel_path is None:
        return []

    fixture_path = fixtures_dir / rel_path
    canonical_url = _normalize_candidate_url(_extract_url_from_html(fixture_path))

    entry_url = None
    if isinstance(entry.get("url"), str):
        entry_url = _normalize_candidate_url(entry["url"], base_url=canonical_url)

    contains_url = None
    if isinstance(entry.get("contains"), str) and _is_specific_fragment(entry["contains"]):
        contains_url = _normalize_candidate_url(entry["contains"], base_url=canonical_url)

    ordered: list[str] = []
    if canonical_url and contains_url and _prefer_contains_url(canonical_url, contains_url):
        ordered.append(contains_url)
        ordered.append(canonical_url)
    else:
        for item in (canonical_url, entry_url, contains_url):
            if item:
                ordered.append(item)

    deduped: list[str] = []
    for item in ordered:
        if item and item not in deduped:
            deduped.append(item)
    return deduped


def _entry_path(entry: dict[str, Any]) -> Path | None:
    rel_path = entry.get("path")
    if not isinstance(rel_path, str):
        return None
    path = Path(rel_path)
    if path.is_absolute():
        return None
    if not _is_valid_fixture_path(path):
        return None
    return path


def _entry_url(entry: dict[str, Any], fixtures_dir: Path) -> str | None:
    urls = _entry_urls(entry, fixtures_dir)
    return urls[0] if urls else None


def _iter_map_entries(mapping: dict[str, str] | list[dict[str, str]]) -> list[dict[str, str]]:
    if isinstance(mapping, list):
        return [entry for entry in mapping if isinstance(entry, dict)]
    if isinstance(mapping, dict):
        return [{"url": url, "path": rel_path} for url, rel_path in mapping.items()]
    return []


def _build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": os.environ.get("SPORTSIPY_CAPTURE_USER_AGENT", DEFAULT_USER_AGENT),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }
    )
    return session


def _http_get(session: requests.Session, url: str, timeout_seconds: float) -> requests.Response:
    response = session.get(url, timeout=timeout_seconds)
    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After", "3")
        try:
            delay = max(3.0, float(retry_after))
        except ValueError:
            delay = 3.0
        time.sleep(delay)
        response = session.get(url, timeout=timeout_seconds)
    return response


def _capture_one(
    *,
    session: requests.Session,
    urls: Iterable[str],
    rel_path: Path,
    fixtures_dir: Path,
    overwrite: bool,
    allow_non_200: bool,
    timeout_seconds: float,
) -> tuple[bool, str]:
    if rel_path.is_absolute():
        return False, "--path must be relative to the fixtures directory"
    output_path = fixtures_dir / rel_path
    if output_path.exists() and not overwrite:
        return False, f"Fixture already exists: {output_path}"

    final_error = "No URL candidates available"
    for url in urls:
        response = _http_get(session, url, timeout_seconds)
        if response.status_code >= 400 and not allow_non_200:
            final_error = (
                f"Request failed ({response.status_code}) for {url}; "
                "use --allow-non-200 to save anyway"
            )
            continue

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(response.text, encoding="utf-8")
        return True, f"Saved fixture to {output_path} from {url}"

    return False, final_error


def _upsert_map_entry(
    mapping: dict[str, str] | list[dict[str, str]],
    *,
    url: str,
    rel_path: Path,
) -> dict[str, str] | list[dict[str, str]]:
    rel_path_str = rel_path.as_posix()
    if isinstance(mapping, dict):
        mapping[url] = rel_path_str
        return mapping
    if isinstance(mapping, list):
        entry = {"url": url, "path": rel_path_str}
        for idx, item in enumerate(mapping):
            if not isinstance(item, dict):
                continue
            if item.get("url") == url:
                mapping[idx] = entry
                return mapping
            if item.get("path") == rel_path_str and item.get("url") is None:
                mapping[idx] = entry
                return mapping
        mapping.append(entry)
        return mapping
    return [{"url": url, "path": rel_path_str}]


def _refresh_from_map(
    *,
    fixtures_dir: Path,
    map_path: Path,
    delay_seconds: float,
    timeout_seconds: float,
    allow_non_200: bool,
    limit: int | None,
    dry_run: bool,
) -> int:
    mapping = _load_map(map_path)
    entries = _iter_map_entries(mapping)

    seen_paths: set[str] = set()
    refreshed = 0
    skipped = 0
    failed = 0
    session = _build_session()

    for entry in entries:
        rel_path = _entry_path(entry)
        if rel_path is None:
            skipped += 1
            continue
        rel_key = rel_path.as_posix()
        if rel_key in seen_paths:
            skipped += 1
            continue
        seen_paths.add(rel_key)

        urls = _entry_urls(entry, fixtures_dir)
        if not urls:
            LOGGER.info(f"SKIP {rel_key}: unable to determine canonical URL")
            skipped += 1
            continue

        if dry_run:
            LOGGER.info(f"DRY-RUN {rel_key} <- {urls[0]}")
            refreshed += 1
        else:
            try:
                ok, message = _capture_one(
                    session=session,
                    urls=urls,
                    rel_path=rel_path,
                    fixtures_dir=fixtures_dir,
                    overwrite=True,
                    allow_non_200=allow_non_200,
                    timeout_seconds=timeout_seconds,
                )
            except requests.RequestException as exc:
                failed += 1
                LOGGER.info(f"FAIL {rel_key}: {exc}")
                continue
            if ok:
                refreshed += 1
                LOGGER.info(f"REFRESH {rel_key} <- {urls[0]}")
            else:
                failed += 1
                LOGGER.info(f"FAIL {rel_key}: {message}")

            # Respect crawl-delay and avoid session jail/429 responses.
            time.sleep(delay_seconds)

        if limit is not None and refreshed >= limit:
            break

    LOGGER.info(
        "Summary: "
        f"refreshed={refreshed}, skipped={skipped}, failed={failed}, unique_paths={len(seen_paths)}"
    )
    return 0 if failed == 0 else 6


def main() -> int:
    """Return main."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(
        description="Capture a fixture from a live URL and update the fixture map."
    )
    parser.add_argument("--url", help="URL to fetch")
    parser.add_argument(
        "--path",
        help="Relative fixture path (inside the fixtures directory)",
    )
    parser.add_argument(
        "--fixtures-dir",
        default="tests/integration",
        help="Root fixtures directory (default: tests/integration)",
    )
    parser.add_argument(
        "--map",
        dest="map_path",
        default=None,
        help="Fixture map JSON (default: <fixtures-dir>/url_map.json)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing fixture file if it exists",
    )
    parser.add_argument(
        "--allow-non-200",
        action="store_true",
        help="Save fixtures even if the response is not 200",
    )
    parser.add_argument(
        "--refresh-map",
        action="store_true",
        help="Refresh fixture files listed in the map using canonical URLs from existing HTML",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=3.0,
        help="Delay between live requests in seconds for --refresh-map (default: 3.0)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Request timeout in seconds (default: 30.0)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of fixtures to refresh (for smoke-testing)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned refresh actions without downloading",
    )
    args = parser.parse_args()

    if not os.environ.get("SPORTSIPY_CAPTURE_FIXTURES"):
        LOGGER.info("Set SPORTSIPY_CAPTURE_FIXTURES=1 to enable fixture capture.")
        return 2

    fixtures_dir = Path(args.fixtures_dir)
    map_path = Path(args.map_path) if args.map_path else fixtures_dir / "url_map.json"

    if args.refresh_map:
        if args.delay < 3.0:
            LOGGER.info("--delay must be at least 3.0 seconds to respect crawl-delay.")
            return 7
        return _refresh_from_map(
            fixtures_dir=fixtures_dir,
            map_path=map_path,
            delay_seconds=args.delay,
            timeout_seconds=args.timeout,
            allow_non_200=args.allow_non_200,
            limit=args.limit,
            dry_run=args.dry_run,
        )

    if not args.url or not args.path:
        LOGGER.info("Provide --url and --path, or use --refresh-map.")
        return 8

    rel_path = Path(args.path)
    session = _build_session()
    try:
        ok, message = _capture_one(
            session=session,
            urls=[args.url],
            rel_path=rel_path,
            fixtures_dir=fixtures_dir,
            overwrite=args.overwrite,
            allow_non_200=args.allow_non_200,
            timeout_seconds=args.timeout,
        )
    except requests.RequestException as exc:
        LOGGER.info(f"Request failed: {exc}")
        return 3
    if not ok:
        LOGGER.info(message)
        return 4
    LOGGER.info(message)

    mapping = _load_map(map_path)
    mapping = _upsert_map_entry(mapping, url=args.url, rel_path=rel_path)
    _save_map(map_path, mapping)

    LOGGER.info(f"Updated map at {map_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
