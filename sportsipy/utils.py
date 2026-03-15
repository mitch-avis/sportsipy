"""Utility functions for HTTP fetching, HTML parsing, caching, and fixture loading."""

from __future__ import annotations

import hashlib
import html
import json
import logging
import os
import re
import threading
import time
import warnings
from collections.abc import Callable, Generator
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs, urlparse

import requests
from lxml.etree import ParserError, XMLSyntaxError
from pyquery import PyQuery

from sportsipy.constants import RATE_LIMIT_INTERVAL

if TYPE_CHECKING:
    from curl_cffi.requests.models import Response as CurlResponse
    from playwright.sync_api import Page

_LOGGER = logging.getLogger(__name__)
_RATE_LIMIT_LOCK = threading.Lock()
_LAST_REQUEST_TIME = 0.0
_FIXTURE_MAP: dict | list | None = None

# ---------------------------------------------------------------------------
# Optional curl_cffi import — provides TLS fingerprint spoofing to bypass
# Cloudflare bot detection.  Falls back to plain requests when not installed.
# ---------------------------------------------------------------------------
try:
    from curl_cffi import requests as _cffi_requests

    _CURL_CFFI_AVAILABLE = True
except ImportError:
    _cffi_requests = None
    _CURL_CFFI_AVAILABLE = False

# ---------------------------------------------------------------------------
# Optional Playwright import — used as a final fallback when bot-challenge
# detection fires and curl_cffi alone is insufficient.
# ---------------------------------------------------------------------------
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

_PLAYWRIGHT_AVAILABLE = sync_playwright is not None

# ---------------------------------------------------------------------------
# Browser-like request headers used for all outbound HTTP requests.
# These reduce false-positive bot flags from simple user-agent checks.
# ---------------------------------------------------------------------------
_BROWSER_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Sec-CH-UA": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    "Sec-CH-UA-Mobile": "?0",
    "Sec-CH-UA-Platform": '"Linux"',
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
}

# ---------------------------------------------------------------------------
# Playwright stealth init-script — injected before every page navigation to
# suppress the most common headless-browser detection signals.
# ---------------------------------------------------------------------------
_PLAYWRIGHT_STEALTH_SCRIPT = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
window.chrome = { runtime: {} };
Object.defineProperty(Notification, 'permission', { get: () => 'default' });
"""


class BotChallengeError(RuntimeError):
    """Raised when a URL responds with a bot-challenge page (e.g. Cloudflare).

    Parameters
    ----------
    url : str
        The URL that returned a bot-challenge response.

    """

    def __init__(self, url: str) -> None:
        """Initialize BotChallengeError with the offending URL.

        Parameters
        ----------
        url : str
            The URL that returned a bot-challenge response.

        """
        self.url = url
        super().__init__(
            f"Bot challenge detected for URL: {url}. "
            "Install curl_cffi (`pip install curl_cffi`) and/or ensure "
            "Playwright browser binaries are installed "
            "(`playwright install chromium`) to bypass Cloudflare protection."
        )


def _is_bot_challenge(html_text: str) -> bool:
    """Return True when the HTML body appears to be a Cloudflare bot challenge.

    Checks for several well-known Cloudflare challenge fingerprints without
    relying on any external dependency.

    Parameters
    ----------
    html_text : str
        Raw HTML string from an HTTP response.

    Returns
    -------
    bool
        ``True`` when the response looks like a bot-challenge page.

    """
    if not html_text:
        return False
    lower = html_text.lower()
    cloudflare_signals = (
        "just a moment",
        "challenges.cloudflare.com",
        "enable javascript and cookies to continue",
        "cf-browser-verification",
        "checking if the site connection is secure",
        "please wait while we verify",
        "ddos-guard",
    )
    return any(signal in lower for signal in cloudflare_signals)


def _apply_playwright_stealth(page: Page) -> None:
    """Inject anti-detection init scripts into a Playwright page.

    Parameters
    ----------
    page : playwright.sync_api.Page
        A Playwright synchronous page object.

    """
    try:
        page.add_init_script(_PLAYWRIGHT_STEALTH_SCRIPT)
    except Exception as exc:
        _LOGGER.debug("Playwright stealth injection failed: %s", exc)


# Backward-compatible callable matching prior usage: utils.pq(...)
def pq(*args: object, **kwargs: object) -> PyQuery:
    """Wrap the PyQuery constructor with a None-safe guard.

    Provides backward compatibility for call sites that previously imported
    and called ``pq`` directly.  A single ``None`` argument is silently
    converted to an empty HTML string rather than raising a ``TypeError``.

    Parameters
    ----------
    *args : object
        Positional arguments forwarded to :class:`pyquery.PyQuery`.
    **kwargs : object
        Keyword arguments forwarded to :class:`pyquery.PyQuery`.

    Returns
    -------
    PyQuery
        A :class:`pyquery.PyQuery` instance wrapping the given input.

    """
    if len(args) == 1 and args[0] is None:
        return PyQuery("")
    return PyQuery(*args, **kwargs)


# {
#   league name: {
#     start month - integer referring to the month that a season typically
#                   begins. Months are 1-based, so January would be 1.
#     wrap - boolean is True when a season spans multiple calendar years, such
#            as the NBA. False when a season is contained in a single calendar
#            year, such as the MLB.
#   }
# }
SEASON_START_MONTH = {
    "mlb": {"start": 4, "wrap": False},
    "nba": {"start": 10, "wrap": True},
    "ncaab": {"start": 11, "wrap": True},
    "ncaaf": {"start": 8, "wrap": False},
    "nfl": {"start": 9, "wrap": False},
    "nhl": {"start": 10, "wrap": True},
}


def todays_date() -> datetime:
    """Get today's date.

    Returns the current date and time. In a standalone function to easily be
    mocked in unit tests.

    Returns
    -------
    datetime.datetime
        The current date and time as a datetime object.

    """
    return datetime.now()


def _env_flag(name: str) -> bool:
    value = os.environ.get(name, "")
    return value.lower() in {"1", "true", "yes", "on"}


def offline_mode() -> bool:
    """Return True when offline fixtures mode is enabled.

    This is a simple helper intended to provide a readable way for other
    modules to detect that network requests are being redirected to offline
    fixtures.
    """
    return _env_flag("SPORTSIPY_OFFLINE")


def _rate_limit_seconds() -> float:
    value = os.environ.get("SPORTSIPY_RATE_LIMIT_SECONDS")
    if value:
        try:
            return max(float(value), 3.0)
        except ValueError:
            return max(float(RATE_LIMIT_INTERVAL), 3.0)
    return max(float(RATE_LIMIT_INTERVAL), 3.0)


def _rate_limit_enabled() -> bool:
    if _env_flag("SPORTSIPY_DISABLE_RATE_LIMIT"):
        return False
    if _env_flag("SPORTSIPY_FORCE_RATE_LIMIT"):
        return True
    if _env_flag("SPORTSIPY_OFFLINE"):
        return False
    return not os.environ.get("PYTEST_CURRENT_TEST")


def _rate_limit_wait() -> None:
    if not _rate_limit_enabled():
        return
    interval = _rate_limit_seconds()
    global _LAST_REQUEST_TIME
    with _RATE_LIMIT_LOCK:
        now = time.monotonic()
        wait = _LAST_REQUEST_TIME + interval - now
        if wait > 0:
            time.sleep(wait)
        _LAST_REQUEST_TIME = time.monotonic()


def _cache_dir() -> Path | None:
    value = os.environ.get("SPORTSIPY_CACHE_DIR")
    if not value:
        return None
    return Path(value)


def _cache_ttl_seconds() -> float | None:
    value = os.environ.get("SPORTSIPY_CACHE_TTL_SECONDS")
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _cache_key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def _cache_read(url: str) -> str | None:
    cache_dir = _cache_dir()
    ttl = _cache_ttl_seconds()
    if not cache_dir or ttl is None:
        return None
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{_cache_key(url)}.json"
    if not cache_file.exists():
        return None
    try:
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        if time.time() - data.get("timestamp", 0) > ttl:
            return None
        return data.get("text")
    except (OSError, json.JSONDecodeError):
        return None


def _cache_write(url: str, text: str) -> None:
    cache_dir = _cache_dir()
    ttl = _cache_ttl_seconds()
    if not cache_dir or ttl is None:
        return
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{_cache_key(url)}.json"
    payload = {"url": url, "timestamp": time.time(), "text": text}
    try:
        cache_file.write_text(json.dumps(payload), encoding="utf-8")
    except OSError:
        return


def _fixture_map() -> dict | list:
    global _FIXTURE_MAP
    if _FIXTURE_MAP is not None:
        return _FIXTURE_MAP
    fixture_map = os.environ.get("SPORTSIPY_FIXTURE_MAP")
    fixture_dir = os.environ.get("SPORTSIPY_FIXTURE_DIR")
    if not fixture_map and fixture_dir:
        fixture_map = os.path.join(fixture_dir, "url_map.json")
    if fixture_map and os.path.exists(fixture_map):
        try:
            with open(fixture_map, encoding="utf-8") as handle:
                _FIXTURE_MAP = json.load(handle)
        except (OSError, json.JSONDecodeError):
            _FIXTURE_MAP = {}
    else:
        _FIXTURE_MAP = {}
    if _FIXTURE_MAP is None:
        _FIXTURE_MAP = {}
    return _FIXTURE_MAP


def _fixture_for_url(url: str) -> str | None:
    if not _env_flag("SPORTSIPY_OFFLINE"):
        return None
    mapping = _fixture_map()
    url_sport_hint = _sport_hint_from_url(url)
    rel_path: str | None = None
    matched_from_mapping = False
    if isinstance(mapping, dict):
        rel_path = mapping.get(url)
        matched_from_mapping = rel_path is not None
    elif isinstance(mapping, list):
        matches: list[tuple[int, str]] = []
        for entry in mapping:
            if not isinstance(entry, dict):
                continue
            path = entry.get("path")
            if not path or not isinstance(path, str):
                continue
            path_lower = path.lower()
            if "__pycache__" in path_lower:
                continue
            entry_sport_hint = _sport_hint_from_path(path_lower)
            if url_sport_hint and entry_sport_hint and url_sport_hint != entry_sport_hint:
                continue
            entry_url = entry.get("url")
            if entry_url and entry_url == url:
                rel_path = path
                matched_from_mapping = True
                break
            contains = entry.get("contains")
            if contains and contains in url:
                matches.append((len(contains), path))
                continue
            pattern = entry.get("regex")
            if pattern:
                try:
                    if re.search(pattern, url):
                        matches.append((len(pattern) + 1, path))
                except re.error:
                    continue
        if rel_path is None and matches:
            matches.sort(key=lambda item: item[0], reverse=True)
            rel_path = matches[0][1]
            matched_from_mapping = True
    if not rel_path:
        rel_path = _heuristic_fixture_path(url)
    if not rel_path:
        return None
    fixture_dir = os.environ.get("SPORTSIPY_FIXTURE_DIR", "")
    path = Path(fixture_dir) / rel_path
    if not path.exists():
        rel_path = _heuristic_fixture_path(url)
        if not rel_path:
            return None
        path = Path(fixture_dir) / rel_path
        if not path.exists():
            return None
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not matched_from_mapping:
        slug = _slug_from_url(url)
        if slug and not _slug_matches_content(content, slug):
            return None
        year = _year_from_url(url)
        if year:
            title = _extract_title(content)
            if title and not _title_matches_year(title, year):
                return None
    return content


def _heuristic_fixture_path(url: str) -> str | None:
    fixture_dir = os.environ.get("SPORTSIPY_FIXTURE_DIR", "")
    if not fixture_dir:
        return None
    root = Path(fixture_dir)
    if not root.exists():
        return None

    parsed = urlparse(url)
    path = parsed.path or ""
    query = parse_qs(parsed.query or "")

    candidates: list[str] = []
    conference_specific = False
    if "/conferences/" in path:
        segments = [segment for segment in path.strip("/").split("/") if segment]
        try:
            index = segments.index("conferences")
            conf = segments[index + 1]
            year_match = (
                re.search(r"\d{4}", segments[index + 2]) if len(segments) > index + 2 else None
            )
            if year_match:
                year = year_match.group(0)
                for ext in (".html", ".htm", ".shtml"):
                    candidates.append(f"{year}-{conf}{ext}")
                conference_specific = True
        except (ValueError, IndexError):
            pass
    base = path.rstrip("/").split("/")[-1] if path else ""
    if base and not conference_specific:
        candidates.append(base)
        base_name, base_ext = os.path.splitext(base)
        if base_ext in {".html", ".htm", ".shtml"}:
            for ext in {".html", ".htm", ".shtml", ""}:
                candidate = f"{base_name}{ext}"
                if candidate not in candidates:
                    candidates.append(candidate)
        elif base_ext == "":
            for ext in (".html", ".htm", ".shtml"):
                candidates.append(f"{base}{ext}")

    # Handle boxscore index pages (query-string URLs)
    if "boxscores" in path and query:
        month = query.get("month", [None])[0]
        day = query.get("day", [None])[0]
        year = query.get("year", [None])[0]
        if month and day and year:
            candidates.append(f"boxscores-{month}-{day}-{year}.html")
    if "/boxes/" in path and query:
        month = query.get("month", [None])[0]
        day = query.get("day", [None])[0]
        year = query.get("year", [None])[0]
        if month and day and year:
            candidates.append(f"boxscore-{month}-{day}-{year}.html")

    if path.rstrip("/").endswith("gamelog"):
        candidates.append("gamelog")

    if not candidates:
        return None

    for candidate in candidates:
        matches = list(root.rglob(candidate))
        if not matches:
            continue
        filtered = _filter_fixture_candidates(matches, url)
        if not filtered:
            continue
        if len(filtered) == 1:
            return filtered[0].relative_to(root).as_posix()
        return filtered[0].relative_to(root).as_posix()
    return None


def _filter_fixture_candidates(paths: list[Path], url: str) -> list[Path]:
    url_lower = url.lower()
    candidates = paths

    sport_hint = _sport_hint_from_url(url)

    if sport_hint:
        filtered = [p for p in candidates if sport_hint in p.as_posix().lower()]
        if not filtered:
            return []
        candidates = filtered

    if "boxscores" in url_lower or "/boxes/" in url_lower:
        filtered = [p for p in candidates if "boxscore" in p.as_posix().lower()]
        if filtered:
            candidates = filtered

    if "polls" in url_lower:
        filtered = [p for p in candidates if "rankings" in p.as_posix().lower()]
        if filtered:
            candidates = filtered

    if "/conferences/" in url_lower or "/seasons/" in url_lower:
        filtered = [p for p in candidates if "conferences" in p.as_posix().lower()]
        if filtered:
            candidates = filtered

    if "/players/" in url_lower:
        filtered = [p for p in candidates if "roster" in p.as_posix().lower()]
        if filtered:
            candidates = filtered

    if "gamelog" in url_lower or "_games" in url_lower or "schedule" in url_lower:
        filtered = [p for p in candidates if "schedule" in p.as_posix().lower()]
        if filtered:
            candidates = filtered

    if "/leagues/" in url_lower or "/years/" in url_lower:
        filtered = [p for p in candidates if "teams" in p.as_posix().lower()]
        if filtered:
            candidates = filtered

    return candidates


def _clean_slug(slug: str) -> str | None:
    slug = slug.strip("/")
    if not slug:
        return None
    slug = re.sub(r"\.(?:html|htm|shtml)$", "", slug, flags=re.IGNORECASE)
    if not slug:
        return None
    if re.fullmatch(r"\d{4}", slug):
        return None
    if len(slug) < 3:
        return None
    return slug


def _extract_canonical_url(content: str) -> str | None:
    match = re.search(
        r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']',
        content,
        flags=re.IGNORECASE,
    )
    if match:
        return match.group(1)
    match = re.search(
        r'<meta[^>]+property=["\']og:url["\'][^>]+content=["\']([^"\']+)["\']',
        content,
        flags=re.IGNORECASE,
    )
    if match:
        return match.group(1)
    return None


def _url_path_has_slug(url: str, slug: str) -> bool:
    parsed = urlparse(url)
    segments = [segment for segment in parsed.path.split("/") if segment]
    for segment in segments:
        cleaned = re.sub(r"\.(?:html|htm|shtml)$", "", segment, flags=re.IGNORECASE)
        if cleaned.lower() == slug.lower():
            return True
    return False


def _slug_matches_content(content: str, slug: str) -> bool:
    canonical = _extract_canonical_url(content)
    if canonical:
        return _url_path_has_slug(canonical, slug)
    content_lower = content.lower()
    slug_lower = slug.lower()
    for pattern in (
        rf"/{re.escape(slug_lower)}/",
        rf"/{re.escape(slug_lower)}\.(?:html|htm|shtml)",
        rf"/{re.escape(slug_lower)}-",
    ):
        if re.search(pattern, content_lower):
            return True
    return False


def _slug_from_url(url: str) -> str | None:
    parsed = urlparse(url)
    path = parsed.path or ""
    for pattern in (
        r"/schools/([^/]+)/",
        r"/teams/([^/]+)/",
        r"/squads/([^/]+)/",
        r"/conferences/([^/]+)/",
    ):
        match = re.search(pattern, path, flags=re.IGNORECASE)
        if match:
            slug = _clean_slug(match.group(1))
            if slug:
                return slug
    match = re.search(r"/players/(?:[a-z]/)?([^/]+)", path, flags=re.IGNORECASE)
    if match:
        return _clean_slug(match.group(1))
    return None


def _year_from_url(url: str) -> str | None:
    parsed = urlparse(url)
    query = parse_qs(parsed.query or "")
    for key in ("year", "season"):
        if key in query and query[key]:
            value = query[key][0]
            if re.fullmatch(r"\d{4}", value):
                return value
    path = parsed.path or ""
    match = re.search(r"(?<!\d)(\d{4})(?!\d)", path)
    if match:
        return match.group(1)
    return None


def _extract_title(content: str) -> str | None:
    title_match = re.search(r"<title[^>]*>(.*?)</title>", content, flags=re.IGNORECASE | re.DOTALL)
    if not title_match:
        title_match = re.search(r"<h1[^>]*>(.*?)</h1>", content, flags=re.IGNORECASE | re.DOTALL)
    if not title_match:
        return None
    title = re.sub(r"<[^>]+>", "", title_match.group(1))
    title = html.unescape(title)
    return " ".join(title.split())


def _title_matches_year(title: str, year: str) -> bool:
    normalized = title.replace("\u2013", "-").replace("\u2014", "-")
    if year in normalized:
        return True
    try:
        year_int = int(year)
    except (TypeError, ValueError):
        return False
    prev = year_int - 1
    short = str(year_int)[-2:]
    return any(pattern in normalized for pattern in (f"{prev}-{short}", f"{prev}-{year}"))


def _sport_hint_from_url(url: str) -> str | None:
    url_lower = url.lower()
    if "basketball-reference.com" in url_lower:
        return "nba"
    if "/cbb/" in url_lower:
        return "ncaab"
    if "/cfb/" in url_lower:
        return "ncaaf"
    if "pro-football-reference.com" in url_lower:
        return "nfl"
    if "baseball-reference.com" in url_lower:
        return "mlb"
    if "hockey-reference.com" in url_lower:
        return "nhl"
    if "fbref.com" in url_lower:
        return "fb"
    return None


def _sport_hint_from_path(path: str) -> str | None:
    path_lower = path.lower()
    if "ncaab" in path_lower:
        return "ncaab"
    if "ncaaf" in path_lower:
        return "ncaaf"
    if "nba" in path_lower:
        return "nba"
    if "nfl" in path_lower:
        return "nfl"
    if "mlb" in path_lower:
        return "mlb"
    if "nhl" in path_lower:
        return "nhl"
    if "/fb/" in path_lower:
        return "fb"
    return None


def _fallback_fixture_by_context(root: Path, url: str) -> Path | None:
    url_lower = url.lower()

    def _pick_first(paths: list[Path]) -> Path | None:
        return sorted(paths)[0] if paths else None

    fixture_root = root / "integration" if (root / "integration").exists() else root

    sport_hint = None
    if "basketball-reference.com" in url_lower:
        sport_hint = "nba"
    elif "/cbb/" in url_lower:
        sport_hint = "ncaab"
    elif "/cfb/" in url_lower:
        sport_hint = "ncaaf"
    elif "pro-football-reference.com" in url_lower:
        sport_hint = "nfl"
    elif "baseball-reference.com" in url_lower:
        sport_hint = "mlb"
    elif "hockey-reference.com" in url_lower:
        sport_hint = "nhl"
    elif "fbref.com" in url_lower:
        sport_hint = "fb"

    if sport_hint == "fb" and "squads" in url_lower:
        return _pick_first(list(fixture_root.rglob("roster/fb/*")))

    if "polls" in url_lower and sport_hint:
        return _pick_first(list(fixture_root.rglob(f"rankings/{sport_hint}/*")))

    if ("/conferences/" in url_lower or "/seasons/" in url_lower) and sport_hint in {
        "ncaab",
        "ncaaf",
    }:
        season_pages = [
            p
            for p in fixture_root.rglob(f"conferences/{sport_hint}/*")
            if re.fullmatch(r"\d{4}\.html", p.name)
        ]
        return _pick_first(season_pages)

    if ("boxscores" in url_lower or "/boxes/" in url_lower) and sport_hint:
        return _pick_first(list(fixture_root.rglob(f"boxscore/{sport_hint}/*")))

    if ("gamelog" in url_lower or "_games" in url_lower or "schedule" in url_lower) and sport_hint:
        return _pick_first(list(fixture_root.rglob(f"schedule/{sport_hint}/*")))

    if "/players/" in url_lower and sport_hint:
        return _pick_first(list(fixture_root.rglob(f"roster/{sport_hint}/*")))

    if "/teams/" in url_lower and sport_hint in {"nba", "nhl", "mlb"}:
        team_pages = [
            p for p in fixture_root.rglob(f"roster/{sport_hint}/*") if re.search(r"\d{4}", p.name)
        ]
        return _pick_first(team_pages)

    if (
        "/leagues/" in url_lower or (sport_hint == "nfl" and "/years/" in url_lower)
    ) and sport_hint:
        return _pick_first(list(fixture_root.rglob(f"teams/{sport_hint}_stats/*")))

    return None


def _http_get(
    url: str,
    timeout: float = 20,
    **kwargs: Any,
) -> requests.Response | CurlResponse | None:
    """Perform a GET request using curl_cffi when available, else plain requests.

    curl_cffi spoofs a real Chrome TLS fingerprint (JA3/JA4), which bypasses
    Cloudflare's common bot detection layer.  If curl_cffi is not installed
    the function transparently falls back to the standard requests library.

    Parameters
    ----------
    url : str
        The URL to fetch.
    timeout : float, optional
        Request timeout in seconds (default 20).
    **kwargs : Any
        Additional keyword arguments forwarded to the underlying HTTP client.

    Returns
    -------
    requests.Response | curl_cffi.requests.models.Response | None
        The HTTP response, or ``None`` on fatal error.

    """
    merged_headers = dict(_BROWSER_HEADERS)
    if "headers" in kwargs:
        merged_headers.update(kwargs.pop("headers"))

    if _CURL_CFFI_AVAILABLE and _cffi_requests is not None:
        try:
            return _cffi_requests.get(
                url,
                headers=merged_headers,
                timeout=timeout,
                impersonate="chrome124",
                **kwargs,
            )
        except Exception as exc:
            _LOGGER.debug("curl_cffi GET failed for %s (%s), falling back to requests", url, exc)

    return requests.get(url, headers=merged_headers, timeout=timeout, **kwargs)


def _request_with_retries(method: str, url: str, **kwargs):
    max_retries_value = os.environ.get("SPORTSIPY_MAX_RETRIES", "2")
    try:
        max_retries = max(int(max_retries_value), 0)
    except ValueError:
        max_retries = 2
    request_kwargs = dict(kwargs)
    timeout_value = request_kwargs.pop("timeout", 20)
    for attempt in range(max_retries + 1):
        _rate_limit_wait()
        try:
            if method.upper() == "GET":
                response = _http_get(url, timeout=timeout_value, **request_kwargs)
            elif method.upper() == "HEAD":
                # Prefer GET over HEAD — HEAD requests are blocked more aggressively
                # by Cloudflare; the response body is discarded by callers anyway.
                merged_headers = dict(_BROWSER_HEADERS)
                if "headers" in request_kwargs:
                    merged_headers.update(request_kwargs.pop("headers"))
                response = requests.head(
                    url,
                    headers=merged_headers,
                    timeout=timeout_value,
                    **request_kwargs,
                )
            else:
                response = requests.request(
                    method,
                    url,
                    timeout=timeout_value,
                    **request_kwargs,
                )
        except requests.RequestException as exc:
            if attempt >= max_retries:
                raise exc
            time.sleep(min(2**attempt, 10))
            continue
        if response is None:
            if attempt >= max_retries:
                return None
            time.sleep(min(2**attempt, 10))
            continue
        if response.status_code in {429} or response.status_code >= 500:
            if attempt >= max_retries:
                return response
            headers = response.headers or {}
            retry_after = headers.get("Retry-After")
            if retry_after:
                try:
                    time.sleep(min(float(retry_after), 30.0))
                except ValueError:
                    time.sleep(min(2**attempt, 10))
            else:
                time.sleep(min(2**attempt, 10))
            continue
        return response
    return None


def url_exists(url: str) -> bool:
    """Determine if a URL is valid and exists.

    Not every URL that is provided is valid and exists, such as requesting
    stats for a season that hasn't yet begun. In this case, the URL needs to be
    validated prior to continuing any code to ensure no unhandled exceptions
    occur.

    Uses GET rather than HEAD so that:

    - The response content is cached for the subsequent ``pull_page()`` call,
      avoiding a redundant round-trip.
    - Cloudflare and similar protections that block bare HEAD requests are not
      triggered.

    Parameters
    ----------
    url : string
        A string representation of the url to check.

    Returns
    -------
    bool
        Evaluates to True when the URL exists and returns usable content,
        otherwise returns False.

    """
    try:
        if _env_flag("SPORTSIPY_OFFLINE"):
            return _fixture_for_url(url) is not None
        html_text = get_page_source(url)
        return html_text is not None
    except (RuntimeError, ValueError, TypeError):
        return False


def resolve_year_for_url(
    year: int | str | None,
    url_builder: Callable[[str], str],
    max_lookback: int = 10,
) -> str | None:
    """Find the most recent year that has data for the supplied URL builder.

    When data is missing for the current season (common early in a season),
    step backward until a valid year is found or the lookback limit is hit.
    """
    if not year:
        return None
    try:
        year_int = int(year)
    except (TypeError, ValueError):
        return str(year)

    for candidate in range(year_int, year_int - max_lookback - 1, -1):
        if url_exists(url_builder(str(candidate))):
            return str(candidate)
    return str(year)


def find_year_for_season(league: str) -> int:
    """Return the necessary seaons's year based on the current date.

    Since all sports start and end at different times throughout the year,
    simply using the current year is not sufficient to describe a season. For
    example, the NCAA Men's Basketball season begins in November every year.
    However, for the November and December months, the following year is used
    to denote the season (ie. November 2017 marks the start of the '2018'
    season) on sports-reference.com. This rule does not apply to all sports.
    Baseball begins and ends in one single calendar year, so the year never
    needs to be incremented.

    Additionally, since information for future seasons is generally not
    finalized until a month before the season begins, the year will default to
    the most recent season until the month prior to the season start date. For
    example, the 2018 MLB season begins in April. In January 2018, however, not
    all of the season's information is present in the system, so the default
    year will be '2017'.

    Parameters
    ----------
    league : string
        A string pertaining to the league start information as listed in
        SEASON_START_MONTH (ie. 'mlb', 'nba', 'nfl', etc.). League must be
        present in SEASON_START_MONTH.

    Returns
    -------
    int
        The respective season's year.

    Raises
    ------
    ValueError
        If the passed 'league' is not a key in SEASON_START_MONTH.

    """
    if league not in SEASON_START_MONTH:
        raise ValueError(f"Unsupported league '{league}'")

    today = todays_date()
    start = SEASON_START_MONTH[league]["start"]
    wrap = SEASON_START_MONTH[league]["wrap"]

    # Wrapped seasons (NBA, NHL, NCAAB): if current month >= start-1 treat as next year season
    if wrap and (start - 1) <= today.month <= 12:
        return today.year + 1

    # Non-wrapping seasons: consider the season "current" starting one month prior
    if not wrap and today.month < (start - 1):
        return today.year - 1

    return today.year


def parse_abbreviation(uri_link: PyQuery | str) -> str:
    """Return a team's abbreviation from a PyQuery object or raw HTML row.

    A school or team's abbreviation is generally embedded in a URI link which
    contains other relative link information. For example, the URI for the
    New England Patriots for the 2017 season is "/teams/nwe/2017.htm". This
    function strips all of the contents before and after "nwe" and converts it
    to uppercase and returns "NWE".

    Parameters
    ----------
    uri_link : string
        A URI link which contains a team's abbreviation within other link
        contents.

    Returns
    -------
    string
        The shortened uppercase abbreviation for a given team.

    """
    # Make sure we have a callable PyQuery selection object
    if isinstance(uri_link, str):
        uri_link = pq(uri_link)
    try:
        anchor = uri_link("a")
        href = anchor.attr("href") if anchor else None
        if not isinstance(href, str) or not href:
            return ""
        abbr = re.sub(r"/[0-9]+\..*htm.*", "", href)
        abbr = re.sub(r"/.*/schools/", "", abbr)
        abbr = re.sub(r"/teams/", "", abbr)
        abbr = re.sub(r"/.*", "", abbr)
        return abbr.upper()
    except (ParserError, XMLSyntaxError):
        return ""


def parse_field(
    parsing_scheme: dict,
    html_data: str | PyQuery,
    field: str,
    index: int = 0,
    strip: bool = False,
    secondary_index: int | None = None,
) -> str | int | None:
    """Parse an HTML table to find the requested field's value.

    All of the values are passed in an HTML table row instead of as individual
    items. The values need to be parsed by matching the requested attribute
    with a parsing scheme that sports-reference uses to differentiate stats.
    This function returns a single value for the given attribute.

    Parameters
    ----------
    parsing_scheme : dict
        A dictionary of the parsing scheme to be used to find the desired
        field. The key corresponds to the attribute name to parse, and the
        value is a PyQuery-readable parsing scheme as a string (such as
        'td[data-stat="wins"]').
    html_data : string
        A string containing all of the rows of stats for a given team. If
        multiple tables are being referenced, this will be comprised of
        multiple rows in a single string.
    field : string
        The name of the attribute to match. Field must be a key in
        parsing_scheme.
    index : int (optional)
        An optional index if multiple fields have the same attribute name. For
        example, 'HR' may stand for the number of home runs a baseball team has
        hit, or the number of home runs a pitcher has given up. The index
        aligns with the order in which the attributes are recevied in the
        html_data parameter.
    strip : boolean (optional)
        An optional boolean value which will remove any empty or invalid
        elements which might show up during list comprehensions. Specify True
        if the invalid elements should be removed from lists, which can help
        with reverse indexing.
    secondary_index : int (optional)
        An optional index if multiple fields have the same attribute, but the
        original index specified above doesn't work. This happens if a page
        doesn't have all of the intended information, and the requested index
        isn't valid, causing the value to be None. Instead, a secondary index
        could be checked prior to returning None.

    Returns
    -------
    string
        The value at the specified index for the requested field. If no value
        could be found, returns None.

    """
    if field == "abbreviation":
        return parse_abbreviation(html_data)

    try:
        scheme = parsing_scheme[field]
    except KeyError:
        return None

    try:
        if isinstance(html_data, PyQuery) or callable(html_data):
            selection = html_data(scheme)
        else:
            selection = pq(html_data)(scheme)
        items: list[str | int] = []
        for item in selection.items():
            txt = item.text()
            if txt is None:
                txt = ""
            if isinstance(txt, int):
                normalized: str | int = txt
            elif isinstance(txt, str):
                normalized = txt
            else:
                normalized = str(txt)
            if strip and isinstance(normalized, str) and not normalized:
                continue
            items.append(normalized)
    except (ParserError, XMLSyntaxError, TypeError, AttributeError):
        items = []

    result = None
    if items:
        try:
            result = items[index]
        except IndexError:
            if secondary_index is not None:
                try:
                    result = items[secondary_index]
                except IndexError:
                    result = None
    return result


def remove_html_comment_tags(html: str | PyQuery) -> str:
    """Return HTML contents with all comment tags removed.

    Some pages embed the HTML contents in comments. Since the HTML contents are
    valid, removing the content tags (but not the actual code within the
    comments) will return the desired contents.

    Parameters
    ----------
    html : PyQuery object
        A PyQuery object which contains the requested HTML page contents.

    Returns
    -------
    string
        The passed HTML contents with all comment tags removed.

    """
    return str(html).replace("<!--", "").replace("-->", "")


def get_stats_table(
    html_page, div: str, footer: bool = False
) -> Generator[PyQuery, None, None] | None:
    """Return a generator of PyQuery rows (<tr>...</tr>) for the requested table.

    When given a PyQuery HTML object and a requested div, this function creates
    a generator where every item is a PyQuery object pertaining to every row in
    the table. Generally, each row will contain multiple stats for a given
    player or team.

    Parameters
    ----------
    html_page : PyQuery object
        A PyQuery object which contains the requested HTML page contents.
    div : string
        The requested tag type and id string in the format "<tag>#<id name>"
        which aligns to the desired table in the passed HTML page. For example,
        "div#all_stats_table" or "table#conference_standings".
    footer : boolean (optional)
        Optionally return the table footer rows instead of the table header.

    Returns
    -------
    generator
        A generator of all row items in a given table.

    """
    try:
        raw = html_page(div)
    except (ParserError, XMLSyntaxError, TypeError):
        return None
    if not raw:
        return None
    try:
        cleaned = remove_html_comment_tags(raw)
        doc = pq(cleaned)
    except (ParserError, XMLSyntaxError):
        return None

    selector = "tfoot tr" if footer else "tbody tr"
    rows = doc(selector)
    if not rows:
        rows = doc("tr")
    row_html = [str(r) for r in rows.items() if str(r).strip()]
    if not row_html:
        return None

    def _gen():
        for row_fragment in row_html:
            yield pq(row_fragment)

    return _gen()


def pull_page(url: str | None = None, local_file: str | None = None):
    """Pull data from a local file if exists, or download data from the website.

    If local_file is passed, users can pull data directly from a local file
    which has already been downloaded instead of downloading from
    sports-reference.com using the package. This reduces server load on their
    end, and allows package users to work offline.

    Parameters
    ----------
    url : string (optional)
        A ``string`` of the URL to pull data from.
    local_file : string (optional)
        A link to a local file which has been pre-downloaded from the website.

    Returns
    -------
    PyQuery object
        Returns a ``PyQuery`` object representing the file that was either
        downloaded or read.

    Raises
    ------
    ValueError
        Raises a ``ValueError`` if neither the URL nor the local_file
        parameters were specified.

    """
    if local_file:
        candidate = Path(local_file)
        if not candidate.exists():
            candidate = Path(__file__).resolve().parents[1] / local_file
        if not candidate.exists():
            return None
        with open(candidate, encoding="utf-8") as file_handle:
            return pq(file_handle.read())
    if url:
        html = get_page_source(url)
        if not html:
            return None
        return pq(html)
    raise ValueError("Expected either a URL or a local data file!")


def no_data_found() -> bool:
    """Emit a warning message when no data could be found on the page.

    Occasionally, such as right before the beginning of a season, a page will
    return a valid response but will have no data outside of the default
    HTML and CSS template. With no data present on the page, sportsipy
    can't parse any information and should indicate the lack of data and return
    safely.
    """
    warnings.warn(
        "The requested page returned a valid response, but no data could be "
        "found. Has the season begun, and is the data available on "
        "www.sports-reference.com?",
        stacklevel=2,
    )
    # Tests only assert falsy behavior
    return False


def get_page_source(url: str) -> str | None:
    """Fetch and return a page's HTML source.

    Fetch pipeline (each tier only runs if the previous one fails or returns a
    bot-challenge body):

    1. **Offline fixture** — if ``SPORTSIPY_OFFLINE`` is set, return the
       matching fixture file immediately.
    2. **Disk cache** — return cached content when a valid cached copy exists.
    3. **curl_cffi GET** (primary) — sends a Chrome-impersonated TLS request
       which bypasses Cloudflare TLS-fingerprint detection.  Falls back to
       plain requests when ``curl_cffi`` is not installed.
    4. **Playwright** (auto-fallback) — launched automatically when step 3
       returns a bot-challenge body.  Suppressed by setting
       ``SPORTSIPY_DISABLE_PLAYWRIGHT=1``.  Can also be forced on for every
       request via ``SPORTSIPY_ENABLE_PLAYWRIGHT=1``.

    Parameters
    ----------
    url : str
        The URL to fetch.

    Returns
    -------
    str | None
        Raw HTML string, or ``None`` if the page could not be retrieved or
        returned a bot-challenge response that could not be bypassed.

    """
    if _env_flag("SPORTSIPY_OFFLINE"):
        return _fixture_for_url(url)

    cached = _cache_read(url)
    if cached is not None:
        return cached

    html_text: str | None = None

    # ------------------------------------------------------------------
    # Tier 1: curl_cffi / requests fetch
    # ------------------------------------------------------------------
    if not _env_flag("SPORTSIPY_ENABLE_PLAYWRIGHT"):
        try:
            resp = _request_with_retries("GET", url, timeout=20)
            if resp is not None and resp.status_code == 200:
                html_text = resp.text
        except requests.RequestException:
            pass

    # ------------------------------------------------------------------
    # Tier 2: Playwright (auto-triggered on challenge, or forced via env)
    # ------------------------------------------------------------------
    use_playwright = (
        _PLAYWRIGHT_AVAILABLE
        and sync_playwright is not None
        and not _env_flag("SPORTSIPY_DISABLE_PLAYWRIGHT")
        and (
            _env_flag("SPORTSIPY_ENABLE_PLAYWRIGHT")
            or html_text is None
            or _is_bot_challenge(html_text)
        )
    )
    if use_playwright:
        if html_text is not None and _is_bot_challenge(html_text):
            _LOGGER.info(
                "Bot challenge detected for %s; retrying with Playwright headless browser", url
            )
        playwright_html = _fetch_with_playwright(url)
        if playwright_html is not None:
            html_text = playwright_html

    if html_text is not None and not _is_bot_challenge(html_text):
        _cache_write(url, html_text)
        return html_text

    if html_text is not None:
        _LOGGER.warning(
            "Bot challenge could not be bypassed for %s. "
            "Install curl_cffi and ensure Playwright browser binaries are available.",
            url,
        )
    return None


def _fetch_with_playwright(url: str) -> str | None:
    """Fetch a URL using a stealth Playwright headless browser session.

    Parameters
    ----------
    url : str
        The URL to fetch.

    Returns
    -------
    str | None
        Raw HTML string, or ``None`` on any failure.

    """
    if sync_playwright is None:
        return None
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            try:
                context = browser.new_context(
                    viewport={"width": 1280, "height": 800},
                    user_agent=_BROWSER_HEADERS["User-Agent"],
                    locale="en-US",
                )
                page = context.new_page()
                _apply_playwright_stealth(page)
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
                content = page.content()
                return content
            finally:
                browser.close()
    except Exception as exc:
        _LOGGER.warning("Playwright fetch failed for %s: %s", url, exc)
        return None
