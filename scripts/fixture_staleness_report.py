#!/usr/bin/env python3
"""Report which local fixtures appear stale compared with live site HTML.

This script is intended for manual maintenance, not CI. It walks the fixture
URL map, fetches the corresponding live pages at a safe pace, and compares the
current HTML against the checked-in fixture file for each mapped page.

Because sports-reference pages often change cosmetically without breaking the
parser, the report distinguishes between structural staleness and lighter
cosmetic drift:

- ``fresh``: fixture and live page are highly similar.
- ``cosmetic-drift``: HTML changed, but the structural fingerprint is still
  close enough that parser selectors are likely fine.
- ``stale``: tables, ``data-stat`` fields, or overall content changed enough
  that the fixture should be reviewed or refreshed.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, cast

import capture_fixtures as fixture_tools
import requests
from lxml import html
from lxml.etree import ParserError, strip_elements

VOLATILE_TEXT_PATTERNS = (
    re.compile(r"nonce=\"[^\"]+\"", re.IGNORECASE),
    re.compile(r"integrity=\"[^\"]+\"", re.IGNORECASE),
    re.compile(r"crossorigin=\"[^\"]+\"", re.IGNORECASE),
    re.compile(r"data-uid=\"[^\"]+\"", re.IGNORECASE),
    re.compile(r"data-reactid=\"[^\"]+\"", re.IGNORECASE),
    re.compile(r"data-append-csv=\"[^\"]+\"", re.IGNORECASE),
)
WHITESPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class FixtureTarget:
    """Describe one unique fixture file and its candidate live URLs."""

    path: Path
    urls: tuple[str, ...]


@dataclass
class FixtureReport:
    """Capture live-vs-fixture comparison results for one fixture."""

    status: str
    path: str
    url: str
    sport: str
    html_ratio: float
    text_ratio: float
    table_jaccard: float
    data_stat_jaccard: float
    fixture_tables: int
    live_tables: int
    fixture_data_stats: int
    live_data_stats: int
    title_changed: bool
    canonical_changed: bool
    summary: str


@dataclass(frozen=True)
class LiveFetchFailure:
    """Describe why all candidate live URLs failed to fetch."""

    url: str
    reason: str


@dataclass
class RefreshSummary:
    """Capture the result of refreshing stale fixtures in place."""

    refreshed: int
    failed: int


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixtures-dir",
        type=Path,
        default=Path("tests/integration"),
        help="Fixture root directory. Defaults to tests/integration.",
    )
    parser.add_argument(
        "--map-path",
        type=Path,
        default=Path("tests/integration/url_map.json"),
        help="Fixture URL map path. Defaults to tests/integration/url_map.json.",
    )
    parser.add_argument("--sport", action="append", help="Limit results to one or more sports.")
    parser.add_argument(
        "--path-contains",
        help="Only compare fixtures whose relative path contains this substring.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Only compare the first N matching fixtures after filtering.",
    )
    parser.add_argument(
        "--delay-seconds",
        type=float,
        default=3.2,
        help="Delay between live requests. Defaults to 3.2 seconds.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=20.0,
        help="HTTP timeout per live request. Defaults to 20 seconds.",
    )
    parser.add_argument(
        "--html-threshold",
        type=float,
        default=0.985,
        help="Minimum normalized HTML similarity to count as fresh.",
    )
    parser.add_argument(
        "--text-threshold",
        type=float,
        default=0.990,
        help="Minimum normalized text similarity to count as fresh.",
    )
    parser.add_argument(
        "--table-threshold",
        type=float,
        default=0.92,
        help="Minimum table-id Jaccard similarity to avoid stale status.",
    )
    parser.add_argument(
        "--data-stat-threshold",
        type=float,
        default=0.94,
        help="Minimum data-stat Jaccard similarity to avoid stale status.",
    )
    parser.add_argument(
        "--only",
        choices=["fresh", "cosmetic-drift", "stale", "fetch-failed"],
        help="Only print fixtures in the requested classification.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        help="Write a machine-readable report to the given JSON path.",
    )
    parser.add_argument(
        "--refresh-stale",
        action="store_true",
        help="Re-capture fixtures classified as stale, overwriting them in place.",
    )
    return parser.parse_args()


def _sport_from_path(path: Path) -> str:
    path_text = path.as_posix().lower()
    sport_tokens = ("mlb", "nba", "nfl", "nhl", "ncaab", "ncaaf", "fb")
    for token in sport_tokens:
        if f"/{token}" in path_text or f"{token}_" in path_text:
            return token
    return "unknown"


def _unique_targets(fixtures_dir: Path, map_path: Path) -> list[FixtureTarget]:
    mapping = fixture_tools._load_map(map_path)
    entries = fixture_tools._iter_map_entries(mapping)
    targets: dict[str, list[str]] = {}
    for entry in entries:
        rel_path = fixture_tools._entry_path(entry)
        if rel_path is None:
            continue
        urls = fixture_tools._entry_urls(entry, fixtures_dir)
        if not urls:
            continue
        key = rel_path.as_posix()
        bucket = targets.setdefault(key, [])
        for url in urls:
            if url not in bucket:
                bucket.append(url)
    return [
        FixtureTarget(path=Path(path_text), urls=tuple(urls))
        for path_text, urls in sorted(targets.items())
    ]


def _normalize_html(raw_html: str) -> str:
    cleaned = raw_html
    for pattern in VOLATILE_TEXT_PATTERNS:
        cleaned = pattern.sub("", cleaned)
    cleaned = cleaned.replace("<!--", "").replace("-->", "")
    try:
        root = html.fromstring(cleaned)
    except (ParserError, ValueError):
        return WHITESPACE_RE.sub(" ", cleaned).strip()

    strip_elements(root, "script", "style", "noscript", with_tail=False)
    for element in root.iter():
        removable_attrs = []
        for attr_name in element.attrib:
            if attr_name in {"nonce", "integrity", "crossorigin", "referrerpolicy"}:
                removable_attrs.append(attr_name)
                continue
            if attr_name.startswith("data-react") or attr_name.startswith("data-google"):
                removable_attrs.append(attr_name)
        for attr_name in removable_attrs:
            element.attrib.pop(attr_name, None)

    normalized = cast(str, html.tostring(root, encoding="unicode", method="html"))
    return WHITESPACE_RE.sub(" ", normalized).strip()


def _normalize_text(raw_html: str) -> str:
    cleaned = raw_html.replace("<!--", "").replace("-->", "")
    try:
        root = html.fromstring(cleaned)
    except (ParserError, ValueError):
        return WHITESPACE_RE.sub(" ", cleaned).strip()
    strip_elements(root, "script", "style", "noscript", with_tail=False)
    return WHITESPACE_RE.sub(" ", root.text_content()).strip()


def _jaccard(first: set[str], second: set[str]) -> float:
    if not first and not second:
        return 1.0
    union = first | second
    if not union:
        return 1.0
    return len(first & second) / len(union)


def _table_ids(raw_html: str) -> set[str]:
    cleaned = raw_html.replace("<!--", "").replace("-->", "")
    try:
        root = html.fromstring(cleaned)
    except (ParserError, ValueError):
        return set()
    return {
        table.attrib["id"].strip()
        for table in root.xpath("//table[@id]")
        if table.attrib.get("id", "").strip()
    }


def _data_stats(raw_html: str) -> set[str]:
    cleaned = raw_html.replace("<!--", "").replace("-->", "")
    try:
        root = html.fromstring(cleaned)
    except (ParserError, ValueError):
        return set()
    return {
        element.attrib["data-stat"].strip()
        for element in root.xpath("//*[@data-stat]")
        if element.attrib.get("data-stat", "").strip()
    }


def _extract_title(raw_html: str) -> str:
    try:
        root = html.fromstring(raw_html)
    except (ParserError, ValueError):
        return ""
    titles = root.xpath("//title")
    if not titles:
        return ""
    return WHITESPACE_RE.sub(" ", titles[0].text_content()).strip()


def _extract_canonical(raw_html: str) -> str:
    match = fixture_tools.CANONICAL_URL_RE.search(raw_html)
    if match:
        return match.group(1).strip()
    match = fixture_tools.OG_URL_RE.search(raw_html)
    if match:
        return match.group(1).strip()
    return ""


def _compare_fixture(
    fixture_html: str,
    live_html: str,
    *,
    html_threshold: float,
    text_threshold: float,
    table_threshold: float,
    data_stat_threshold: float,
    path: Path,
    url: str,
) -> FixtureReport:
    fixture_html_normalized = _normalize_html(fixture_html)
    live_html_normalized = _normalize_html(live_html)
    fixture_text = _normalize_text(fixture_html)
    live_text = _normalize_text(live_html)
    html_ratio = difflib.SequenceMatcher(
        None, fixture_html_normalized, live_html_normalized
    ).ratio()
    text_ratio = difflib.SequenceMatcher(None, fixture_text, live_text).ratio()

    fixture_tables = _table_ids(fixture_html)
    live_tables = _table_ids(live_html)
    fixture_data_stats = _data_stats(fixture_html)
    live_data_stats = _data_stats(live_html)
    table_jaccard = _jaccard(fixture_tables, live_tables)
    data_stat_jaccard = _jaccard(fixture_data_stats, live_data_stats)
    title_changed = _extract_title(fixture_html) != _extract_title(live_html)
    canonical_changed = _extract_canonical(fixture_html) != _extract_canonical(live_html)

    if (
        table_jaccard < table_threshold
        or data_stat_jaccard < data_stat_threshold
        or (html_ratio < html_threshold and text_ratio < text_threshold)
    ):
        status = "stale"
        summary = "Structure or content drift exceeds thresholds"
    elif (
        html_ratio < html_threshold
        or text_ratio < text_threshold
        or title_changed
        or canonical_changed
    ):
        status = "cosmetic-drift"
        summary = "Live page differs, but structure is still broadly similar"
    else:
        status = "fresh"
        summary = "Fixture closely matches live page"

    return FixtureReport(
        status=status,
        path=path.as_posix(),
        url=url,
        sport=_sport_from_path(path),
        html_ratio=html_ratio,
        text_ratio=text_ratio,
        table_jaccard=table_jaccard,
        data_stat_jaccard=data_stat_jaccard,
        fixture_tables=len(fixture_tables),
        live_tables=len(live_tables),
        fixture_data_stats=len(fixture_data_stats),
        live_data_stats=len(live_data_stats),
        title_changed=title_changed,
        canonical_changed=canonical_changed,
        summary=summary,
    )


def _fetch_first_live(
    session: Any,
    urls: tuple[str, ...],
    timeout_seconds: float,
) -> tuple[str, str] | LiveFetchFailure:
    last_failure = LiveFetchFailure(
        url=urls[0] if urls else "",
        reason="No candidate URLs were available",
    )
    for url in urls:
        try:
            response = fixture_tools._http_get(session, url, timeout_seconds)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exc:
            print(f"  network error fetching {url}: {exc}")
            last_failure = LiveFetchFailure(url=url, reason=f"Network error: {exc}")
            continue
        if response.status_code < 400:
            return url, response.text
        last_failure = LiveFetchFailure(
            url=url,
            reason=f"Request failed ({response.status_code}) for {url}",
        )
    return last_failure


def _select_targets(args: argparse.Namespace) -> list[FixtureTarget]:
    targets = _unique_targets(args.fixtures_dir, args.map_path)
    selected = []
    requested_sports = set(args.sport or [])
    for target in targets:
        sport = _sport_from_path(target.path)
        if requested_sports and sport not in requested_sports:
            continue
        if args.path_contains and args.path_contains not in target.path.as_posix():
            continue
        selected.append(target)
    if args.limit is not None:
        return selected[: args.limit]
    return selected


def _refresh_stale_fixtures(
    *,
    reports: list[FixtureReport],
    target_lookup: dict[str, FixtureTarget],
    fixtures_dir: Path,
    timeout_seconds: float,
    delay_seconds: float,
) -> RefreshSummary:
    session = fixture_tools._build_session()
    refreshed = 0
    failed = 0
    stale_reports = [report for report in reports if report.status == "stale"]
    for index, report in enumerate(stale_reports):
        target = target_lookup.get(report.path)
        if target is None:
            failed += 1
            print(f"REFRESH-FAIL {report.path}: no matching target metadata found")
            continue
        try:
            ok, message = fixture_tools._capture_one(
                session=session,
                urls=target.urls,
                rel_path=target.path,
                fixtures_dir=fixtures_dir,
                overwrite=True,
                allow_non_200=False,
                timeout_seconds=timeout_seconds,
            )
        except Exception as exc:
            failed += 1
            print(f"REFRESH-FAIL {report.path}: {exc}")
            continue

        if ok:
            refreshed += 1
            print(f"REFRESH {report.path} <- {target.urls[0]}")
        else:
            failed += 1
            print(f"REFRESH-FAIL {report.path}: {message}")

        if index + 1 < len(stale_reports):
            time.sleep(max(delay_seconds, 0.0))
    return RefreshSummary(refreshed=refreshed, failed=failed)


def _print_report(report: FixtureReport) -> None:
    print(
        f"[{report.status.upper():14}] {report.path} | "
        f"html={report.html_ratio:.4f} text={report.text_ratio:.4f} "
        f"tables={report.table_jaccard:.4f} data-stat={report.data_stat_jaccard:.4f}"
    )


def main() -> int:
    """Compare live pages against mapped fixtures and print a staleness report."""
    args = _parse_args()
    session = fixture_tools._build_session()
    targets = _select_targets(args)
    target_lookup = {target.path.as_posix(): target for target in targets}
    if not targets:
        print("No fixtures matched the requested filters.")
        return 1

    reports: list[FixtureReport] = []
    for index, target in enumerate(targets):
        fixture_path = args.fixtures_dir / target.path
        try:
            fixture_html = fixture_path.read_text(encoding="utf-8")
        except OSError as exc:
            reports.append(
                FixtureReport(
                    status="stale",
                    path=target.path.as_posix(),
                    url=target.urls[0],
                    sport=_sport_from_path(target.path),
                    html_ratio=0.0,
                    text_ratio=0.0,
                    table_jaccard=0.0,
                    data_stat_jaccard=0.0,
                    fixture_tables=0,
                    live_tables=0,
                    fixture_data_stats=0,
                    live_data_stats=0,
                    title_changed=False,
                    canonical_changed=False,
                    summary=f"Fixture read failed: {exc}",
                )
            )
            continue

        live_payload = _fetch_first_live(session, target.urls, args.timeout_seconds)
        if isinstance(live_payload, LiveFetchFailure):
            reports.append(
                FixtureReport(
                    status="fetch-failed",
                    path=target.path.as_posix(),
                    url=live_payload.url,
                    sport=_sport_from_path(target.path),
                    html_ratio=0.0,
                    text_ratio=0.0,
                    table_jaccard=0.0,
                    data_stat_jaccard=0.0,
                    fixture_tables=len(_table_ids(fixture_html)),
                    live_tables=0,
                    fixture_data_stats=len(_data_stats(fixture_html)),
                    live_data_stats=0,
                    title_changed=False,
                    canonical_changed=False,
                    summary=live_payload.reason,
                )
            )
        else:
            url, live_html = live_payload
            reports.append(
                _compare_fixture(
                    fixture_html,
                    live_html,
                    html_threshold=args.html_threshold,
                    text_threshold=args.text_threshold,
                    table_threshold=args.table_threshold,
                    data_stat_threshold=args.data_stat_threshold,
                    path=target.path,
                    url=url,
                )
            )

        if index + 1 < len(targets):
            time_to_wait = max(args.delay_seconds, 0.0)
            if time_to_wait:
                time.sleep(time_to_wait)

    reports.sort(
        key=lambda item: (
            {"stale": 0, "fetch-failed": 1, "cosmetic-drift": 2, "fresh": 3}[item.status],
            item.table_jaccard,
            item.data_stat_jaccard,
            item.html_ratio,
        )
    )

    filtered_reports = [
        report for report in reports if args.only is None or report.status == args.only
    ]
    for report in filtered_reports:
        _print_report(report)

    summary = {
        "fresh": sum(1 for report in reports if report.status == "fresh"),
        "cosmetic-drift": sum(1 for report in reports if report.status == "cosmetic-drift"),
        "stale": sum(1 for report in reports if report.status == "stale"),
        "fetch-failed": sum(1 for report in reports if report.status == "fetch-failed"),
    }
    print()
    print(
        f"Compared {len(reports)} fixtures: {summary['fresh']} fresh, "
        f"{summary['cosmetic-drift']} cosmetic-drift, {summary['stale']} stale, "
        f"{summary['fetch-failed']} fetch-failed"
    )

    if args.json_out:
        payload = {
            "summary": summary,
            "reports": [asdict(report) for report in reports],
        }
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.refresh_stale and summary["stale"]:
        print()
        refresh_summary = _refresh_stale_fixtures(
            reports=reports,
            target_lookup=target_lookup,
            fixtures_dir=args.fixtures_dir,
            timeout_seconds=args.timeout_seconds,
            delay_seconds=args.delay_seconds,
        )
        print()
        print(
            "Refresh summary: "
            f"refreshed={refresh_summary.refreshed}, failed={refresh_summary.failed}"
        )
        return 0 if refresh_summary.failed == 0 else 1

    return 1 if summary["stale"] or summary["fetch-failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
