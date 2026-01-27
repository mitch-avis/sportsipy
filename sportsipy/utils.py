from __future__ import annotations

import hashlib
import json
import os
import re
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Generator, Optional

import requests
from lxml.etree import ParserError, XMLSyntaxError
from pyquery import PyQuery

from .constants import RATE_LIMIT_INTERVAL

_RATE_LIMIT_LOCK = threading.Lock()
_LAST_REQUEST_TIME = 0.0
_FIXTURE_MAP = None


# Backward-compatible callable matching prior usage: utils.pq(...)
def pq(*args, **kwargs):  # pylint: disable=invalid-name
    if len(args) == 1 and args[0] is None:
        return PyQuery("")
    return PyQuery(*args, **kwargs)


# Try optional Playwright (only used if explicitly falling back for dynamic pages)
try:
    from playwright.sync_api import sync_playwright  # type: ignore

    _PLAYWRIGHT_AVAILABLE = True
except ImportError:
    _PLAYWRIGHT_AVAILABLE = False

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
    """
    Get today's date.

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


def _rate_limit_seconds() -> float:
    value = os.environ.get("SPORTSIPY_RATE_LIMIT_SECONDS")
    if value:
        try:
            return max(float(value), 3.0)
        except ValueError:
            return max(float(RATE_LIMIT_INTERVAL), 3.0)
    return max(float(RATE_LIMIT_INTERVAL), 3.0)


def _rate_limit_enabled() -> bool:
    if _env_flag("SPORTSIPY_DISABLE_RATE_LIMIT") or _env_flag("SPORTSIPY_OFFLINE"):
        return False
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return False
    return True


def _rate_limit_wait() -> None:
    if not _rate_limit_enabled():
        return
    interval = _rate_limit_seconds()
    global _LAST_REQUEST_TIME  # pylint: disable=global-statement
    with _RATE_LIMIT_LOCK:
        now = time.monotonic()
        wait = _LAST_REQUEST_TIME + interval - now
        if wait > 0:
            time.sleep(wait)
        _LAST_REQUEST_TIME = time.monotonic()


def _cache_dir() -> Optional[Path]:
    value = os.environ.get("SPORTSIPY_CACHE_DIR")
    if not value:
        return None
    return Path(value)


def _cache_ttl_seconds() -> Optional[float]:
    value = os.environ.get("SPORTSIPY_CACHE_TTL_SECONDS")
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _cache_key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def _cache_read(url: str) -> Optional[str]:
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


def _fixture_map() -> dict:
    global _FIXTURE_MAP  # pylint: disable=global-statement
    if _FIXTURE_MAP is not None:
        return _FIXTURE_MAP
    fixture_map = os.environ.get("SPORTSIPY_FIXTURE_MAP")
    fixture_dir = os.environ.get("SPORTSIPY_FIXTURE_DIR")
    if not fixture_map and fixture_dir:
        fixture_map = os.path.join(fixture_dir, "url_map.json")
    if fixture_map and os.path.exists(fixture_map):
        try:
            with open(fixture_map, "r", encoding="utf-8") as handle:
                _FIXTURE_MAP = json.load(handle)
        except (OSError, json.JSONDecodeError):
            _FIXTURE_MAP = {}
    else:
        _FIXTURE_MAP = {}
    return _FIXTURE_MAP


def _fixture_for_url(url: str) -> Optional[str]:
    if not _env_flag("SPORTSIPY_OFFLINE"):
        return None
    mapping = _fixture_map()
    rel_path = mapping.get(url)
    if not rel_path:
        return None
    fixture_dir = os.environ.get("SPORTSIPY_FIXTURE_DIR", "")
    path = Path(fixture_dir) / rel_path
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def _request_with_retries(method: str, url: str, **kwargs):
    max_retries_value = os.environ.get("SPORTSIPY_MAX_RETRIES", "2")
    try:
        max_retries = max(int(max_retries_value), 0)
    except ValueError:
        max_retries = 2
    for attempt in range(max_retries + 1):
        _rate_limit_wait()
        try:
            if method.upper() == "HEAD":
                response = requests.head(url, **kwargs)
            elif method.upper() == "GET":
                response = requests.get(url, **kwargs)
            else:
                response = requests.request(method, url, **kwargs)
        except requests.RequestException as exc:
            if attempt >= max_retries:
                raise exc
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
    """
    Determine if a URL is valid and exists.

    Not every URL that is provided is valid and exists, such as requesting
    stats for a season that hasn't yet begun. In this case, the URL needs to be
    validated prior to continuing any code to ensure no unhandled exceptions
    occur.

    Parameters
    ----------
    url : string
        A string representation of the url to check.

    Returns
    -------
    bool
        Evaluates to True when the URL exists and is valid, otherwise returns
        False.
    """
    try:
        if _env_flag("SPORTSIPY_OFFLINE"):
            return _fixture_for_url(url) is not None
        response = _request_with_retries("HEAD", url, timeout=10)
        if response is None:
            return False
        if response.status_code == 301:
            new_response = _request_with_retries("GET", url, timeout=10)
            return bool(new_response and new_response.status_code < 400)
        return bool(response.status_code < 400)
    except Exception:
        return False


def find_year_for_season(league: str) -> int:
    """
    Return the necessary seaons's year based on the current date.

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


def parse_abbreviation(uri_link) -> str:
    """
    Returns a team's abbreviation. Accepts either a PyQuery object or raw HTML
    string for a single <tr> row.

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
        if not href:
            return ""
        abbr = re.sub(r"/[0-9]+\..*htm.*", "", href)
        abbr = re.sub(r"/.*/schools/", "", abbr)
        abbr = re.sub(r"/teams/", "", abbr)
        return abbr.upper()
    except (ParserError, XMLSyntaxError):
        return ""


def parse_field(
    parsing_scheme: dict,
    html_data,
    field: str,
    index: int = 0,
    strip: bool = False,
    secondary_index: Optional[int] = None,
) -> Optional[str]:
    """
    Parse an HTML table to find the requested field's value.

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
        selection = html_data(scheme) if callable(html_data) else pq(html_data)(scheme)
        items: list[str] = []
        for item in selection.items():
            txt = item.text()
            if strip and not txt:
                continue
            items.append(txt)
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


def remove_html_comment_tags(html: str) -> str:
    """
    Returns the passed HTML contents with all comment tags removed while
    keeping the contents within the tags.

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
) -> Optional[Generator[PyQuery, None, None]]:
    """
    Return a generator of PyQuery rows (<tr>...</tr>) for the requested table.

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
    """
    Pull data from a local file if exists, or download data from the website.

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
        if not os.path.exists(local_file):
            return None
        with open(local_file, "r", encoding="utf-8") as file_handle:
            return pq(file_handle.read())
    if url:
        html = get_page_source(url)
        if not html:
            return None
        return pq(html)
    raise ValueError("Expected either a URL or a local data file!")


def no_data_found() -> bool:
    """
    Print a message that no data could be found on the page.

    Occasionally, such as right before the beginning of a season, a page will
    return a valid response but will have no data outside of the default
    HTML and CSS template. With no data present on the page, sportsipy
    can't parse any information and should indicate the lack of data and return
    safely.
    """
    print(
        "The requested page returned a valid response, but no data could be "
        "found. Has the season begun, and is the data available on "
        "www.sports-reference.com?"
    )
    # Tests only assert falsy behavior
    return False


def get_page_source(url: str) -> Optional[str]:
    """
    Basic HTML fetch; Playwright fallback only if available and requests fails.
    """
    if _env_flag("SPORTSIPY_OFFLINE"):
        return _fixture_for_url(url)

    cached = _cache_read(url)
    if cached is not None:
        return cached

    try:
        resp = _request_with_retries("GET", url, timeout=20)
        if resp is not None and resp.status_code == 200:
            _cache_write(url, resp.text)
            return resp.text
    except requests.RequestException:
        pass

    # Optional dynamic fallback (rarely needed for test fixtures)
    if _PLAYWRIGHT_AVAILABLE and _env_flag("SPORTSIPY_ENABLE_PLAYWRIGHT"):
        try:
            with sync_playwright() as playwright_session:
                browser = playwright_session.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=60000)
                html = page.content()
                browser.close()
                return html
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Playwright fetch failed: {exc}")
            return None
    return None
