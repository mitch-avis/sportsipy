"""Provide utilities for test utils."""

import json
from pathlib import Path
from typing import Any, cast

import pytest
import requests
from flexmock import flexmock
from lxml.etree import ParserError

from sportsipy import utils


class SeasonStarts:
    """Represent SeasonStarts."""

    def __init__(self, league, month, expected_year):
        """Initialize the class instance."""
        self.league = league
        self.month = month
        self.expected_year = expected_year


class MockDateTime:
    """Represent MockDateTime."""

    def __init__(self, month, year):
        """Initialize the class instance."""
        self.month = month
        self.year = year


class Item:
    """Represent Item."""

    def __init__(self, input_string):
        """Initialize the class instance."""
        self.input_string = input_string

    def text(self):
        """Return text."""
        return self.input_string


class Html:
    """Represent Html."""

    def __init__(self, html_string, item_list):
        """Initialize the class instance."""
        self.html_string = html_string
        self.item_list = item_list

    def attr(self, attribute):
        """Return attr."""
        return self.html_string

    def items(self):
        """Return items."""
        items = []
        for item in self.item_list:
            items.append(Item(item))
        return items


class MockHtml:
    """Represent MockHtml."""

    def __init__(self, html_string, item_list):
        """Initialize the class instance."""
        self.html_string = html_string
        self.item_list = item_list

    def __call__(self, tag):
        """Return   call  ."""
        return Html(self.html_string, self.item_list)


def mock_pyquery(url, timeout=None, **kwargs):
    """Return mock pyquery."""

    class MockPQ:
        def __init__(self, html_contents, status_code=200):
            self.status_code = status_code
            self.html_contents = html_contents
            self.text = html_contents

    if "404" in url:
        return MockPQ("This is bad", 404)
    if "exception" in url:
        raise requests.RequestException
    return MockPQ("This is good", 200)


class TestUtils:
    """Represent TestUtils."""

    def test__find_year_for_season_returns_correct_year(self):
        """Return test  find year for season returns correct year."""
        season_start_matrix = [
            # MLB Months
            SeasonStarts("mlb", 1, 2017),
            SeasonStarts("mlb", 2, 2017),
            SeasonStarts("mlb", 3, 2018),
            SeasonStarts("mlb", 4, 2018),
            SeasonStarts("mlb", 5, 2018),
            SeasonStarts("mlb", 6, 2018),
            SeasonStarts("mlb", 7, 2018),
            SeasonStarts("mlb", 8, 2018),
            SeasonStarts("mlb", 9, 2018),
            SeasonStarts("mlb", 10, 2018),
            SeasonStarts("mlb", 11, 2018),
            SeasonStarts("mlb", 12, 2018),
            # NBA Months
            SeasonStarts("nba", 1, 2018),
            SeasonStarts("nba", 2, 2018),
            SeasonStarts("nba", 3, 2018),
            SeasonStarts("nba", 4, 2018),
            SeasonStarts("nba", 5, 2018),
            SeasonStarts("nba", 6, 2018),
            SeasonStarts("nba", 7, 2018),
            SeasonStarts("nba", 8, 2018),
            SeasonStarts("nba", 9, 2019),
            SeasonStarts("nba", 10, 2019),
            SeasonStarts("nba", 11, 2019),
            SeasonStarts("nba", 12, 2019),
            # NCAAB Months
            SeasonStarts("ncaab", 1, 2018),
            SeasonStarts("ncaab", 2, 2018),
            SeasonStarts("ncaab", 3, 2018),
            SeasonStarts("ncaab", 4, 2018),
            SeasonStarts("ncaab", 5, 2018),
            SeasonStarts("ncaab", 6, 2018),
            SeasonStarts("ncaab", 7, 2018),
            SeasonStarts("ncaab", 8, 2018),
            SeasonStarts("ncaab", 9, 2018),
            SeasonStarts("ncaab", 10, 2019),
            SeasonStarts("ncaab", 11, 2019),
            SeasonStarts("ncaab", 12, 2019),
            # NCAAF Months
            SeasonStarts("ncaaf", 1, 2017),
            SeasonStarts("ncaaf", 2, 2017),
            SeasonStarts("ncaaf", 3, 2017),
            SeasonStarts("ncaaf", 4, 2017),
            SeasonStarts("ncaaf", 5, 2017),
            SeasonStarts("ncaaf", 6, 2017),
            SeasonStarts("ncaaf", 7, 2018),
            SeasonStarts("ncaaf", 8, 2018),
            SeasonStarts("ncaaf", 9, 2018),
            SeasonStarts("ncaaf", 10, 2018),
            SeasonStarts("ncaaf", 11, 2018),
            SeasonStarts("ncaaf", 12, 2018),
            # NFL Months
            SeasonStarts("nfl", 1, 2017),
            SeasonStarts("nfl", 2, 2017),
            SeasonStarts("nfl", 3, 2017),
            SeasonStarts("nfl", 4, 2017),
            SeasonStarts("nfl", 5, 2017),
            SeasonStarts("nfl", 6, 2017),
            SeasonStarts("nfl", 7, 2017),
            SeasonStarts("nfl", 8, 2018),
            SeasonStarts("nfl", 9, 2018),
            SeasonStarts("nfl", 10, 2018),
            SeasonStarts("nfl", 11, 2018),
            SeasonStarts("nfl", 12, 2018),
            # NHL Months
            SeasonStarts("nhl", 1, 2018),
            SeasonStarts("nhl", 2, 2018),
            SeasonStarts("nhl", 3, 2018),
            SeasonStarts("nhl", 4, 2018),
            SeasonStarts("nhl", 5, 2018),
            SeasonStarts("nhl", 6, 2018),
            SeasonStarts("nhl", 7, 2018),
            SeasonStarts("nhl", 8, 2018),
            SeasonStarts("nhl", 9, 2019),
            SeasonStarts("nhl", 10, 2019),
            SeasonStarts("nhl", 11, 2019),
            SeasonStarts("nhl", 12, 2019),
        ]

        for month in season_start_matrix:
            mock_datetime = MockDateTime(month.month, 2018)
            flexmock(utils).should_receive("todays_date").and_return(mock_datetime)

            result = utils.find_year_for_season(month.league)
            assert result == month.expected_year

    def test_remove_html_comment_tags_removes_comments(self):
        """Return test remove html comment tags removes comments."""
        html_string = """<html>

    <body>
        <!--<p>This should be kept.</p>-->
    </body>
</html>"""
        expected_output = """<html>

    <body>
        <p>This should be kept.</p>
    </body>
</html>"""

        result = utils.remove_html_comment_tags(html_string)

        assert result == expected_output

    def test_remove_html_comment_tags_without_comments_doesnt_change(self):
        """Return test remove html comment tags without comments doesnt change."""
        html_string = """<html>

    <body>
        <p>This should be the same.</p>
    </body>
</html>"""
        expected_output = """<html>

    <body>
        <p>This should be the same.</p>
    </body>
</html>"""

        result = utils.remove_html_comment_tags(html_string)

        assert result == expected_output

    def test_abbreviation_is_parsed_correctly(self):
        """Return test abbreviation is parsed correctly."""
        test_abbreviations = {
            "/teams/ARI/2018.shtml": "ARI",
            "/teams/nwe/2017.htm": "NWE",
            "/cfb/schools/clemson/2017.html": "CLEMSON",
            "/teams/GSW/2018.html": "GSW",
            "/cbb/schools/purdue/2018.html": "PURDUE",
            "/teams/TBL/2018.html": "TBL",
        }

        for html, abbreviation in test_abbreviations.items():
            mock_html = MockHtml(html, None)
            result = utils.parse_abbreviation(cast(Any, mock_html))
            assert result == abbreviation

    def test__parse_field_returns_abbreviation(self):
        """Return test  parse field returns abbreviation."""
        parsing_scheme = {"abbreviation": "a"}
        input_abbreviation = "/teams/ARI/2018.shtml"
        expected = "ARI"
        flexmock(utils).should_receive("parse_abbreviation").and_return("ARI").once()

        result = utils.parse_field(
            parsing_scheme,
            cast(Any, MockHtml(input_abbreviation, None)),
            "abbreviation",
        )
        assert result == expected

    def test_parse_field_returns_none_on_index_error(self):
        """Return test parse field returns none on index error."""
        parsing_scheme = {"batters_used": 'td[data-stat="batters_used"]:first'}
        html_string = """<td class="right " data-stat="batters_used">32</td>

<td class="right " data-stat="age_bat">29.1</td>
<td class="right " data-stat="runs_per_game">4.10</td>"""
        expected = None

        result = utils.parse_field(
            parsing_scheme,
            cast(Any, MockHtml(html_string, [expected])),
            "batters_used",
            index=3,
        )
        assert result == expected

    def test__parse_field_returns_value_for_non_abbreviation(self):
        """Return test  parse field returns value for non abbreviation."""
        parsing_scheme = {"batters_used": 'td[data-stat="batters_used"]:first'}
        html_string = """<td class="right " data-stat="batters_used">32</td>

<td class="right " data-stat="age_bat">29.1</td>
<td class="right " data-stat="runs_per_game">4.10</td>"""
        expected = "32"

        result = utils.parse_field(
            parsing_scheme, cast(Any, MockHtml(html_string, [expected])), "batters_used"
        )
        assert result == expected

    def test__get_stats_table_returns_correct_table(self):
        """Return test  get stats table returns correct table."""
        html_string = """<div>

    <table class="stats_table" id="all_stats">
        <tbody>
            <tr data-row="0">
                <td class="right " data-stat="column1">1</td>
            </tr>
            <tr data-row="1">
                <td class="right " data-stat="column2">2</td>
            </tr>
        </tbody>
    </table>
</div>"""
        expected = [
            '<tr data-row="0">\n<td class="right " data-stat="column1">1</td>\n</tr>',
            '<tr data-row="1">\n<td class="right " data-stat="column2">2</td>\n</tr>',
        ]
        div = "table#all_stats"
        flexmock(utils).should_receive("remove_html_comment_tags").and_return(html_string).once()

        result = utils.get_stats_table(cast(Any, MockHtml(html_string, expected)), div)
        assert result is not None

        i = 0
        for _ in result:
            i += 1

        assert i == 2

    def test_valid_url_returns_true(self, monkeypatch):
        """Return test valid url returns true."""
        monkeypatch.setattr(utils, "get_page_source", lambda _url: "<html>ok</html>")
        response = utils.url_exists("http://www.good_url.com/this/is/valid")

        assert response

    def test_404_url_returns_false(self, monkeypatch):
        """Return test 404 url returns false."""
        monkeypatch.setattr(utils, "get_page_source", lambda _url: None)
        assert not utils.url_exists("http://www.404.com/doesnt/exist")

    def test_invalid_url_exception_returns_false(self, monkeypatch):
        """Return test invalid url exception returns false."""

        def raise_runtime(_url):
            raise RuntimeError("connection error")

        monkeypatch.setattr(utils, "get_page_source", raise_runtime)
        assert not utils.url_exists("http://www.exception.com")

    def test_no_data_found_returns_safely(self, *args, **kwargs):
        """Return test no data found returns safely."""
        assert not utils.no_data_found()

    def test_pulling_data_with_no_inputs(self, *args, **kwargs):
        """Return test pulling data with no inputs."""
        with pytest.raises(ValueError):
            utils.pull_page()

    def test_pulling_local_file(self, *args, **kwargs):
        """Return test pulling local file."""
        output = utils.pull_page(local_file="VERSION")

        assert output

    def test_secondary_index_pulling_values(self):
        """Return test secondary index pulling values."""
        parsing_scheme = {"batters_used": 'td[data-stat="batters_used"]'}
        html_string = """<td class="right " data-stat="batters_used">32</td>

<td class="right " data-stat="age_bat">29.1</td>
<td class="right " data-stat="runs_per_game">4.10</td>
<td class="right " data-stat="batters_used">31</td>
<td class="right " data-stat="batters_used">34</td>"""
        items = [32, 31, 34]
        expected = 31

        result = utils.parse_field(
            parsing_scheme,
            cast(Any, MockHtml(html_string, items)),
            "batters_used",
            index=3,
            secondary_index=1,
        )
        assert result == expected

    def test_secondary_index_pulling_values_bad_secondary(self):
        """Return test secondary index pulling values bad secondary."""
        parsing_scheme = {"batters_used": 'td[data-stat="batters_used"]'}
        html_string = """<td class="right " data-stat="batters_used">32</td>

<td class="right " data-stat="age_bat">29.1</td>
<td class="right " data-stat="runs_per_game">4.10</td>
<td class="right " data-stat="batters_used">31</td>
<td class="right " data-stat="batters_used">34</td>"""
        items = [32, 31, 34]

        result = utils.parse_field(
            parsing_scheme,
            cast(Any, MockHtml(html_string, items)),
            "batters_used",
            index=3,
            secondary_index=4,
        )
        assert not result

    def test_title_matches_year_handles_ranges(self):
        """Return test title matches year handles ranges."""
        assert utils._title_matches_year("2017-18 Season Summary", "2018")
        assert utils._title_matches_year("2017–18 Season Summary", "2018")
        assert not utils._title_matches_year("2016-17 Season Summary", "2018")

    def test_extract_canonical_url_prefers_link(self):
        """Return test extract canonical url prefers link."""
        html = (
            '<link rel="canonical" href="https://example.com/teams/HOU/2017.html" />'
            '<meta property="og:url" content="https://example.com/teams/NYJ/2017.html" />'
        )
        assert utils._extract_canonical_url(html) == "https://example.com/teams/HOU/2017.html"

    def test_slug_matches_content_uses_canonical_when_present(self):
        """Return test slug matches content uses canonical when present."""
        html = (
            '<link rel="canonical" href="https://example.com/teams/NYJ/2017.html" />'
            '<a href="/teams/HOU/2017.html">Link</a>'
        )
        assert not utils._slug_matches_content(html, "HOU")

    def test_slug_matches_content_scans_body_without_canonical(self):
        """Return test slug matches content scans body without canonical."""
        html = '<a href="/teams/HOU/2017.html">Link</a>'
        assert utils._slug_matches_content(html, "HOU")

    def test_resolve_year_for_url_walks_backwards(self, monkeypatch):
        """Return test resolve year for url walks backwards."""

        def fake_exists(url: str) -> bool:
            return url.endswith("/2017")

        monkeypatch.setattr(utils, "url_exists", fake_exists)
        result = utils.resolve_year_for_url(2019, lambda y: f"https://example.com/{y}")
        assert result == "2017"

    def test_resolve_year_for_url_returns_input_when_unparseable(self, monkeypatch):
        """Return test resolve year for url returns input when unparseable."""

        def fake_exists(url: str) -> bool:
            raise AssertionError("url_exists should not be called for non-numeric years")

        monkeypatch.setattr(utils, "url_exists", fake_exists)
        assert utils.resolve_year_for_url("BAD", lambda y: f"https://example.com/{y}") == "BAD"

    def test_pq_handles_none_and_html(self):
        """Return test pq handles none and html."""
        with pytest.raises(ParserError):
            utils.pq(None)
        assert utils.pq("<div>ok</div>")

    def test_env_flag_and_offline_mode(self, monkeypatch):
        """Return test env flag and offline mode."""
        monkeypatch.setenv("SPORTSIPY_OFFLINE", "true")
        assert utils._env_flag("SPORTSIPY_OFFLINE")
        assert utils.offline_mode()
        monkeypatch.setenv("SPORTSIPY_OFFLINE", "0")
        assert not utils.offline_mode()

    def test_rate_limit_seconds_and_enabled(self, monkeypatch):
        """Return test rate limit seconds and enabled."""
        monkeypatch.setenv("SPORTSIPY_RATE_LIMIT_SECONDS", "2")
        assert utils._rate_limit_seconds() == 3.0
        monkeypatch.setenv("SPORTSIPY_RATE_LIMIT_SECONDS", "5")
        assert utils._rate_limit_seconds() == 5.0
        monkeypatch.setenv("SPORTSIPY_DISABLE_RATE_LIMIT", "1")
        assert not utils._rate_limit_enabled()
        monkeypatch.delenv("SPORTSIPY_DISABLE_RATE_LIMIT", raising=False)
        monkeypatch.setenv("SPORTSIPY_FORCE_RATE_LIMIT", "1")
        assert utils._rate_limit_enabled()

    def test_rate_limit_wait_sleeps_when_required(self, monkeypatch):
        """Return test rate limit wait sleeps when required."""
        monkeypatch.setattr(utils, "_rate_limit_enabled", lambda: True)
        monkeypatch.setattr(utils, "_rate_limit_seconds", lambda: 1.0)
        monkeypatch.setattr(utils, "_LAST_REQUEST_TIME", 10.0)
        ticks = iter([10.5, 11.0])
        sleeps = []
        monkeypatch.setattr(utils.time, "monotonic", lambda: next(ticks))
        monkeypatch.setattr(utils.time, "sleep", lambda seconds: sleeps.append(seconds))

        utils._rate_limit_wait()

        assert sleeps == [0.5]

    def test_cache_read_write_round_trip(self, monkeypatch, tmp_path):
        """Return test cache read write round trip."""
        monkeypatch.setenv("SPORTSIPY_CACHE_DIR", str(tmp_path))
        monkeypatch.setenv("SPORTSIPY_CACHE_TTL_SECONDS", "60")

        utils._cache_write("https://example.com/test", "hello")
        assert utils._cache_read("https://example.com/test") == "hello"

    def test_cache_read_handles_expired_and_bad_json(self, monkeypatch, tmp_path):
        """Return test cache read handles expired and bad json."""
        monkeypatch.setenv("SPORTSIPY_CACHE_DIR", str(tmp_path))
        monkeypatch.setenv("SPORTSIPY_CACHE_TTL_SECONDS", "1")
        key = utils._cache_key("https://example.com/test")
        cache_file = tmp_path / f"{key}.json"
        cache_file.write_text("not json", encoding="utf-8")
        assert utils._cache_read("https://example.com/test") is None

        cache_file.write_text(json.dumps({"timestamp": 0, "text": "x"}), encoding="utf-8")
        monkeypatch.setattr(utils.time, "time", lambda: 999)
        assert utils._cache_read("https://example.com/test") is None

    def test_fixture_map_and_fixture_for_url(self, monkeypatch, tmp_path):
        """Return test fixture map and fixture for url."""
        fixture_file = tmp_path / "fixture.html"
        fixture_file.write_text("<html>fixture</html>", encoding="utf-8")
        fixture_map = tmp_path / "url_map.json"
        fixture_map.write_text(
            json.dumps({"https://example.com/test": "fixture.html"}),
            encoding="utf-8",
        )
        monkeypatch.setenv("SPORTSIPY_OFFLINE", "1")
        monkeypatch.setenv("SPORTSIPY_FIXTURE_DIR", str(tmp_path))
        monkeypatch.setenv("SPORTSIPY_FIXTURE_MAP", str(fixture_map))
        monkeypatch.setattr(utils, "_FIXTURE_MAP", None)

        assert utils._fixture_map()
        assert utils._fixture_for_url("https://example.com/test") == "<html>fixture</html>"

    def test_heuristic_fixture_path_for_boxscore_query(self, monkeypatch, tmp_path):
        """Return test heuristic fixture path for boxscore query."""
        fixture_file = tmp_path / "boxscores-1-2-2020.html"
        fixture_file.write_text("<html>fixture</html>", encoding="utf-8")
        monkeypatch.setenv("SPORTSIPY_FIXTURE_DIR", str(tmp_path))

        path = utils._heuristic_fixture_path("https://site/boxscores/?month=1&day=2&year=2020")

        assert path == "boxscores-1-2-2020.html"

    def test_filter_fixture_candidates_can_drop_mismatched_sport(self, tmp_path):
        """Return test filter fixture candidates can drop mismatched sport."""
        ncaaf = tmp_path / "integration" / "roster" / "ncaaf" / "a.html"
        nba = tmp_path / "integration" / "roster" / "nba" / "a.html"
        ncaaf.parent.mkdir(parents=True, exist_ok=True)
        nba.parent.mkdir(parents=True, exist_ok=True)
        ncaaf.write_text("ok", encoding="utf-8")
        nba.write_text("ok", encoding="utf-8")

        result = utils._filter_fixture_candidates(
            [ncaaf, nba],
            "https://www.sports-reference.com/cfb/schools/purdue/2017.html",
        )
        assert result == [ncaaf]

    def test_request_with_retries_recovers_from_request_exception(self, monkeypatch):
        """Return test request with retries recovers from request exception."""

        class Response:
            def __init__(self, status_code, text="ok"):
                self.status_code = status_code
                self.text = text
                self.headers = {}

        calls = {"count": 0}

        def fake_get(url, timeout=20, **kwargs):
            calls["count"] += 1
            if calls["count"] == 1:
                raise requests.RequestException("boom")
            return Response(200)

        monkeypatch.setattr(utils.requests, "get", fake_get)
        monkeypatch.setattr(utils.time, "sleep", lambda *_args, **_kwargs: None)
        response = utils._request_with_retries("GET", "https://example.com")
        assert response is not None
        assert response.status_code == 200

    def test_request_with_retries_honors_retry_after(self, monkeypatch):
        """Return test request with retries honors retry after."""

        class Response:
            def __init__(self, status_code, retry_after=None):
                self.status_code = status_code
                self.text = "ok"
                self.headers = {}
                if retry_after is not None:
                    self.headers["Retry-After"] = retry_after

        responses = iter([Response(429, "1"), Response(200)])
        sleeps = []

        # Disable curl_cffi so the mock on utils.requests.get is actually used.
        monkeypatch.setattr(utils, "_CURL_CFFI_AVAILABLE", False)
        monkeypatch.setattr(utils.requests, "get", lambda *_args, **_kwargs: next(responses))
        monkeypatch.setattr(utils.time, "sleep", lambda seconds: sleeps.append(seconds))

        response = utils._request_with_retries("GET", "https://example.com")
        assert response is not None
        assert response.status_code == 200
        assert sleeps

    def test_url_exists_handles_301_follow_up(self, monkeypatch):
        """Return test url exists returns True when get_page_source returns HTML."""
        # url_exists() now delegates to get_page_source(); redirect handling is
        # transparent inside the HTTP client, not done by url_exists() itself.
        monkeypatch.setattr(utils, "get_page_source", lambda _url: "<html>redirected</html>")
        assert utils.url_exists("https://example.com")

    def test_get_page_source_paths(self, monkeypatch):
        """Return test get page source paths."""
        monkeypatch.setenv("SPORTSIPY_OFFLINE", "1")
        monkeypatch.setattr(utils, "_fixture_for_url", lambda _url: "offline")
        assert utils.get_page_source("https://example.com") == "offline"

        monkeypatch.setenv("SPORTSIPY_OFFLINE", "0")
        monkeypatch.setattr(utils, "_cache_read", lambda _url: "cached")
        assert utils.get_page_source("https://example.com") == "cached"

        monkeypatch.setattr(utils, "_cache_read", lambda _url: None)

        class Response:
            def __init__(self):
                self.status_code = 200
                self.text = "live"

        monkeypatch.setattr(utils, "_request_with_retries", lambda *_args, **_kwargs: Response())
        monkeypatch.setattr(utils, "_cache_write", lambda *_args, **_kwargs: None)
        assert utils.get_page_source("https://example.com") == "live"

    def test_get_page_source_returns_none_on_failure_without_playwright(self, monkeypatch):
        """Return test get page source returns none on failure without playwright."""
        monkeypatch.setenv("SPORTSIPY_OFFLINE", "0")
        monkeypatch.setattr(utils, "_cache_read", lambda _url: None)

        def raise_request(*_args, **_kwargs):
            raise requests.RequestException("boom")

        monkeypatch.setattr(utils, "_request_with_retries", raise_request)
        monkeypatch.setattr(utils, "_PLAYWRIGHT_AVAILABLE", False)
        assert utils.get_page_source("https://example.com") is None

    def test_pull_page_missing_local_file_returns_none(self):
        """Return test pull page missing local file returns none."""
        assert utils.pull_page(local_file="definitely_missing_file.txt") is None

    def test_fallback_fixture_by_context_selectors(self, tmp_path):
        """Return test fallback fixture by context selectors."""
        root = tmp_path / "integration"
        (root / "roster" / "fb").mkdir(parents=True, exist_ok=True)
        (root / "rankings" / "ncaaf").mkdir(parents=True, exist_ok=True)
        (root / "conferences" / "ncaaf").mkdir(parents=True, exist_ok=True)
        (root / "boxscore" / "nfl").mkdir(parents=True, exist_ok=True)
        (root / "schedule" / "nfl").mkdir(parents=True, exist_ok=True)
        (root / "roster" / "nfl").mkdir(parents=True, exist_ok=True)
        (root / "teams" / "nfl_stats").mkdir(parents=True, exist_ok=True)

        (root / "roster" / "fb" / "sample.html").write_text("ok", encoding="utf-8")
        (root / "rankings" / "ncaaf" / "polls.html").write_text("ok", encoding="utf-8")
        (root / "conferences" / "ncaaf" / "2017.html").write_text("ok", encoding="utf-8")
        (root / "boxscore" / "nfl" / "boxscore.html").write_text("ok", encoding="utf-8")
        (root / "schedule" / "nfl" / "schedule.html").write_text("ok", encoding="utf-8")
        (root / "roster" / "nfl" / "player.html").write_text("ok", encoding="utf-8")
        (root / "teams" / "nfl_stats" / "teams.html").write_text("ok", encoding="utf-8")

        assert (
            utils._fallback_fixture_by_context(
                tmp_path,
                "https://fbref.com/en/squads/abc123/2018-2019/matchlogs/all_comps/schedule/",
            )
            is not None
        )
        assert (
            utils._fallback_fixture_by_context(
                tmp_path,
                "https://www.sports-reference.com/cfb/years/2017-polls.html",
            )
            is not None
        )
        assert (
            utils._fallback_fixture_by_context(
                tmp_path,
                "https://www.sports-reference.com/cfb/conferences/sec/2017.html",
            )
            is not None
        )
        assert (
            utils._fallback_fixture_by_context(
                tmp_path,
                "https://www.pro-football-reference.com/boxscores/",
            )
            is not None
        )
        (root / "roster" / "nba").mkdir(parents=True, exist_ok=True)
        (root / "roster" / "nba" / "2023.html").write_text("ok", encoding="utf-8")
        assert (
            utils._fallback_fixture_by_context(
                tmp_path,
                "https://www.basketball-reference.com/teams/LAL/2023.html",
            )
            is not None
        )
        assert (
            utils._fallback_fixture_by_context(
                tmp_path,
                "https://www.pro-football-reference.com/players/B/BradTo00.htm",
            )
            is not None
        )
        assert (
            utils._fallback_fixture_by_context(
                tmp_path,
                "https://www.pro-football-reference.com/years/2023/",
            )
            is not None
        )

    def test_fallback_fixture_by_context_returns_none_without_match(self, tmp_path):
        """Return test fallback fixture by context returns none without match."""
        assert (
            utils._fallback_fixture_by_context(
                tmp_path,
                "https://example.com/not-a-sports-reference-url",
            )
            is None
        )

    def test_fixture_for_url_list_mapping_and_content_guards(self, monkeypatch, tmp_path):
        """Return test fixture for url list mapping and content guards."""
        target = tmp_path / "ncaaf-roster.html"
        target.write_text(
            "<title>Purdue 2017 Team Page</title><a href='/schools/purdue/2017.html'>Purdue</a>",
            encoding="utf-8",
        )

        mapping = [
            {"path": "__pycache__/ignored.html", "contains": "purdue"},
            {"path": "ncaaf-roster.html", "regex": "[invalid"},
        ]
        monkeypatch.setenv("SPORTSIPY_OFFLINE", "1")
        monkeypatch.setenv("SPORTSIPY_FIXTURE_DIR", str(tmp_path))
        monkeypatch.setattr(utils, "_FIXTURE_MAP", mapping)
        monkeypatch.setattr(utils, "_heuristic_fixture_path", lambda _url: "ncaaf-roster.html")

        url = "https://www.sports-reference.com/cfb/schools/purdue/2017.html"
        assert utils._fixture_for_url(url) is not None

        target.write_text(
            "<title>Notre Dame 2016 Team Page</title><a href='/schools/nd/2016.html'>ND</a>",
            encoding="utf-8",
        )
        assert utils._fixture_for_url(url) is None

    def test_heuristic_fixture_path_conference_and_gamelog(self, monkeypatch, tmp_path):
        """Return test heuristic fixture path conference and gamelog."""
        conf = tmp_path / "conferences" / "ncaaf" / "2017-sec.html"
        gamelog = tmp_path / "gamelog"
        conf.parent.mkdir(parents=True, exist_ok=True)
        conf.write_text("ok", encoding="utf-8")
        gamelog.write_text("ok", encoding="utf-8")

        monkeypatch.setenv("SPORTSIPY_FIXTURE_DIR", str(tmp_path))
        path1 = utils._heuristic_fixture_path(
            "https://www.sports-reference.com/cfb/conferences/sec/2017.html"
        )
        path2 = utils._heuristic_fixture_path("https://example.com/players/x/gamelog/")

        assert path1 == "conferences/ncaaf/2017-sec.html"
        assert path2 == "gamelog"

    def test_parse_abbreviation_and_parse_field_error_paths(self):
        """Return test parse abbreviation and parse field error paths."""
        assert utils.parse_abbreviation("<td>No link</td>") == ""

        class BadHtml:
            def __call__(self, _scheme):
                raise TypeError("bad html")

        scheme = {"wins": 'td[data-stat="wins"]'}
        assert utils.parse_field(scheme, cast(Any, BadHtml()), "wins") is None
        assert utils.parse_field(scheme, "<tr></tr>", "missing") is None

    def test_get_stats_table_footer_and_none_paths(self):
        """Return test get stats table footer and none paths."""
        html = utils.pq(
            "<table id='sample'><tfoot><tr><td>footer</td></tr></tfoot>"
            "<tbody><tr><td>body</td></tr></tbody></table>"
        )
        footer_rows = utils.get_stats_table(html, "table#sample", footer=True)
        body_rows = utils.get_stats_table(html, "table#sample", footer=False)
        missing = utils.get_stats_table(html, "table#missing", footer=False)

        assert footer_rows is not None
        assert body_rows is not None
        assert missing is None
        assert "footer" in str(next(footer_rows))
        assert "body" in str(next(body_rows))

    def test_no_data_found_returns_false_and_warns(self):
        """Return test no data found returns false and warns."""
        with pytest.warns(UserWarning, match="no data"):
            assert not utils.no_data_found()

    def test_get_page_source_playwright_fallback_success(self, monkeypatch):
        """Return test get page source playwright fallback success."""

        class Page:
            def add_init_script(self, *_args, **_kwargs):
                return None

            def goto(self, *_args, **_kwargs):
                return None

            def content(self):
                return "<html>playwright</html>"

        class BrowserContext:
            def new_page(self):
                return Page()

        class Browser:
            def new_context(self, **_kwargs):
                return BrowserContext()

            def close(self):
                return None

        class Chromium:
            def launch(self, **_kwargs):
                return Browser()

        class PlaywrightSession:
            chromium = Chromium()

        class Context:
            def __enter__(self):
                return PlaywrightSession()

            def __exit__(self, exc_type, exc, tb):
                return False

        monkeypatch.setenv("SPORTSIPY_OFFLINE", "0")
        monkeypatch.setenv("SPORTSIPY_ENABLE_PLAYWRIGHT", "1")
        monkeypatch.setattr(utils, "_cache_read", lambda _url: None)
        monkeypatch.setattr(utils, "_PLAYWRIGHT_AVAILABLE", True)
        monkeypatch.setattr(utils, "sync_playwright", lambda: Context())

        assert utils.get_page_source("https://example.com") == "<html>playwright</html>"

    def test_get_page_source_playwright_fallback_failure(self, monkeypatch):
        """Return test get page source playwright fallback failure."""

        class Context:
            def __enter__(self):
                raise RuntimeError("playwright failed")

            def __exit__(self, exc_type, exc, tb):
                return False

        monkeypatch.setenv("SPORTSIPY_OFFLINE", "0")
        monkeypatch.setenv("SPORTSIPY_ENABLE_PLAYWRIGHT", "1")
        monkeypatch.setattr(utils, "_cache_read", lambda _url: None)
        monkeypatch.setattr(utils, "_request_with_retries", lambda *_args, **_kwargs: None)
        monkeypatch.setattr(utils, "_PLAYWRIGHT_AVAILABLE", True)
        monkeypatch.setattr(utils, "sync_playwright", lambda: Context())

        assert utils.get_page_source("https://example.com") is None

    def test_rate_limit_and_cache_error_branches(self, monkeypatch, tmp_path):
        """Return test rate limit and cache error branches."""
        monkeypatch.setenv("SPORTSIPY_RATE_LIMIT_SECONDS", "BAD")
        assert utils._rate_limit_seconds() == 3.0

        monkeypatch.setenv("SPORTSIPY_OFFLINE", "1")
        assert not utils._rate_limit_enabled()
        monkeypatch.setenv("SPORTSIPY_OFFLINE", "0")
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        assert utils._rate_limit_enabled()

        monkeypatch.setenv("SPORTSIPY_CACHE_DIR", str(tmp_path))
        monkeypatch.setenv("SPORTSIPY_CACHE_TTL_SECONDS", "BAD")
        assert utils._cache_ttl_seconds() is None

        monkeypatch.setenv("SPORTSIPY_CACHE_TTL_SECONDS", "60")
        monkeypatch.setattr(
            Path, "write_text", lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError)
        )
        utils._cache_write("https://example.com/fail", "x")

    def test_fixture_for_url_fallback_and_missing_paths(self, monkeypatch, tmp_path):
        """Return test fixture for url fallback and missing paths."""
        monkeypatch.setenv("SPORTSIPY_OFFLINE", "1")
        monkeypatch.setenv("SPORTSIPY_FIXTURE_DIR", str(tmp_path))
        monkeypatch.setattr(utils, "_FIXTURE_MAP", {"https://example.com/a": "missing.html"})
        monkeypatch.setattr(utils, "_heuristic_fixture_path", lambda _url: None)
        assert utils._fixture_for_url("https://example.com/a") is None

        target = tmp_path / "fixture.html"
        target.write_text(
            "<title>Valid 2017</title><a href='/teams/hou/2017.html'>x</a>", encoding="utf-8"
        )
        monkeypatch.setattr(utils, "_FIXTURE_MAP", {})
        monkeypatch.setattr(utils, "_heuristic_fixture_path", lambda _url: "fixture.html")
        assert utils._fixture_for_url("https://example.com/teams/hou/2017.html") is not None

        target.write_text(
            "<title>Wrong 2016</title><a href='/teams/nyj/2016.html'>x</a>", encoding="utf-8"
        )
        assert utils._fixture_for_url("https://example.com/teams/hou/2017.html") is None

    def test_filter_fixture_candidates_additional_contexts(self, tmp_path):
        """Return test filter fixture candidates additional contexts."""
        rankings = tmp_path / "integration" / "rankings" / "ncaaf" / "polls.html"
        roster = tmp_path / "integration" / "roster" / "ncaaf" / "player.html"
        schedule = tmp_path / "integration" / "schedule" / "ncaaf" / "gamelog.html"
        teams = tmp_path / "integration" / "teams" / "nfl_stats" / "teams.html"
        for path in [rankings, roster, schedule, teams]:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("ok", encoding="utf-8")

        assert utils._filter_fixture_candidates(
            [rankings, roster],
            "https://www.sports-reference.com/cfb/years/2017-polls.html",
        ) == [rankings]
        assert utils._filter_fixture_candidates(
            [rankings, roster],
            "https://www.sports-reference.com/cfb/players/a/player-one-1.html",
        ) == [roster]
        assert utils._filter_fixture_candidates(
            [schedule, roster],
            "https://www.sports-reference.com/cfb/schools/purdue/2017-schedule.html",
        ) == [schedule]
        assert utils._filter_fixture_candidates(
            [teams, roster],
            "https://www.pro-football-reference.com/years/2023/",
        ) == [teams]

    def test_parse_abbreviation_parser_error_and_pull_page_url_none(self, monkeypatch):
        """Return test parse abbreviation parser error and pull page url none."""

        class BadUri:
            def __call__(self, _selector):
                raise ParserError("bad")

        assert utils.parse_abbreviation(cast(Any, BadUri())) == ""

        monkeypatch.setattr(utils, "get_page_source", lambda _url: None)
        assert utils.pull_page(url="https://example.com") is None

    def test_get_stats_table_type_error_path(self):
        """Return test get stats table type error path."""

        class BadPage:
            def __call__(self, _selector):
                raise TypeError("bad page")

        assert utils.get_stats_table(cast(Any, BadPage()), "table#x") is None

    def test_slug_year_title_helper_branches(self):
        """Return test slug year title helper branches."""
        assert utils._clean_slug("") is None
        assert utils._clean_slug("20") is None
        assert utils._clean_slug("2017") is None
        assert utils._clean_slug("team.htm") == "team"

        assert utils._slug_from_url("https://x/schools/purdue/2017.html") == "purdue"
        assert utils._slug_from_url("https://x/players/a/allenjo01.html") == "allenjo01"
        assert utils._slug_from_url("https://x/no/slug/here") is None

        assert utils._year_from_url("https://x/path?season=2018") == "2018"
        assert utils._year_from_url("https://x/path/no/year") is None

        assert utils._extract_title("<h1>Header Title</h1>") == "Header Title"
        assert utils._extract_title("<div>No title</div>") is None
        assert not utils._title_matches_year("No Year", "BAD")

    def test_fixture_map_and_list_edge_branches(self, monkeypatch, tmp_path):
        """Return test fixture map and list edge branches."""
        bad_map = tmp_path / "url_map.json"
        bad_map.write_text("{invalid json", encoding="utf-8")
        monkeypatch.setenv("SPORTSIPY_FIXTURE_MAP", str(bad_map))
        monkeypatch.setattr(utils, "_FIXTURE_MAP", None)
        assert utils._fixture_map() == {}

        fixture = tmp_path / "target.html"
        fixture.write_text(
            "<title>2017</title><a href='/teams/hou/2017.html'>x</a>", encoding="utf-8"
        )
        mapping = [
            "bad-entry",
            {"path": 123},
            {"path": "target.html", "regex": "teams/hou"},
        ]
        monkeypatch.setenv("SPORTSIPY_OFFLINE", "1")
        monkeypatch.setenv("SPORTSIPY_FIXTURE_DIR", str(tmp_path))
        monkeypatch.setattr(utils, "_FIXTURE_MAP", mapping)

        assert utils._fixture_for_url("https://example.com/teams/hou/2017.html") is not None

        monkeypatch.setattr(
            utils,
            "_FIXTURE_MAP",
            [{"path": "missing.html", "contains": "teams/hou"}],
        )
        monkeypatch.setattr(utils, "_heuristic_fixture_path", lambda _url: "missing2.html")
        assert utils._fixture_for_url("https://example.com/teams/hou/2017.html") is None

    def test_request_with_retries_and_url_exists_additional_paths(self, monkeypatch):
        """Return test request with retries and url exists additional paths."""

        class Response:
            def __init__(self, status_code):
                self.status_code = status_code
                self.headers = {}
                self.text = "ok"

        monkeypatch.setattr(utils.time, "sleep", lambda *_args, **_kwargs: None)
        monkeypatch.setattr(utils.requests, "head", lambda *_args, **_kwargs: Response(200))
        assert utils._request_with_retries("HEAD", "https://example.com") is not None

        responses = iter([Response(500), Response(500), Response(500)])
        monkeypatch.setenv("SPORTSIPY_MAX_RETRIES", "2")
        monkeypatch.setattr(utils.requests, "request", lambda *_args, **_kwargs: next(responses))
        response = utils._request_with_retries("POST", "https://example.com")
        assert response is not None
        assert response.status_code == 500

        # Disable Playwright so the None response from _request_with_retries
        # is not silently masked by a fallback browser attempt.
        monkeypatch.setattr(utils, "_PLAYWRIGHT_AVAILABLE", False)
        monkeypatch.setattr(utils, "_request_with_retries", lambda *_args, **_kwargs: None)
        assert not utils.url_exists("https://example.com")

        def raise_exc(*_args, **_kwargs):
            raise RuntimeError("boom")

        monkeypatch.setattr(utils, "_request_with_retries", raise_exc)
        assert not utils.url_exists("https://example.com")


# ---------------------------------------------------------------------------
# Tests for the bot-detection layer (1.6.1–1.6.6)
# ---------------------------------------------------------------------------

_CLEAN_HTML = "<html><head><title>Stats</title></head><body><table></table></body></html>"

# Minimal Cloudflare challenge snippets — enough to trigger each signal.
_CHALLENGE_BODIES = {
    "just_a_moment": "<html><head><title>Just a moment...</title></head></html>",
    "challenges_src": (
        '<script src="https://challenges.cloudflare.com/turnstile/v0/api.js"></script>'
    ),
    "enable_js": "<html><body>Enable JavaScript and cookies to continue</body></html>",
    "cf_browser": '<div id="cf-browser-verification">verification</div>',
    "checking_connection": "<p>Checking if the site connection is secure</p>",
    "please_wait": "<p>Please wait while we verify your browser access to the site.</p>",
    "ddos_guard": "<meta name='ddos-guard' content='1'>",
}


class TestBotDetectionLayer:
    """Tests for _is_bot_challenge(), BotChallengeError, _http_get(), and url_exists()."""

    # ------------------------------------------------------------------
    # _is_bot_challenge() — positive cases (one per signal keyword)
    # ------------------------------------------------------------------

    def test_is_bot_challenge_just_a_moment(self):
        """Return True for a 'Just a moment...' Cloudflare challenge page."""
        assert utils._is_bot_challenge(_CHALLENGE_BODIES["just_a_moment"])

    def test_is_bot_challenge_challenges_src(self):
        """Return True when html contains challenges.cloudflare.com script src."""
        assert utils._is_bot_challenge(_CHALLENGE_BODIES["challenges_src"])

    def test_is_bot_challenge_enable_js(self):
        """Return True for 'Enable JavaScript and cookies to continue' body."""
        assert utils._is_bot_challenge(_CHALLENGE_BODIES["enable_js"])

    def test_is_bot_challenge_cf_browser(self):
        """Return True for pages containing cf-browser-verification attribute."""
        assert utils._is_bot_challenge(_CHALLENGE_BODIES["cf_browser"])

    def test_is_bot_challenge_checking_connection(self):
        """Return True for 'Checking if the site connection is secure' text."""
        assert utils._is_bot_challenge(_CHALLENGE_BODIES["checking_connection"])

    def test_is_bot_challenge_please_wait(self):
        """Return True for 'please wait while we verify' text."""
        assert utils._is_bot_challenge(_CHALLENGE_BODIES["please_wait"])

    def test_is_bot_challenge_ddos_guard(self):
        """Return True for DDoS-Guard challenge pages."""
        assert utils._is_bot_challenge(_CHALLENGE_BODIES["ddos_guard"])

    def test_is_bot_challenge_case_insensitive(self):
        """Return True regardless of signal capitalisation."""
        assert utils._is_bot_challenge("JUST A MOMENT...")
        assert utils._is_bot_challenge("DDOS-GUARD")

    # ------------------------------------------------------------------
    # _is_bot_challenge() — negative cases
    # ------------------------------------------------------------------

    def test_is_bot_challenge_normal_html_returns_false(self):
        """Return False for ordinary stats HTML."""
        assert not utils._is_bot_challenge(_CLEAN_HTML)

    def test_is_bot_challenge_empty_string_returns_false(self):
        """Return False for an empty string."""
        assert not utils._is_bot_challenge("")

    # ------------------------------------------------------------------
    # BotChallengeError
    # ------------------------------------------------------------------

    def test_bot_challenge_error_carries_url(self):
        """BotChallengeError.url attribute equals the URL passed to the constructor."""
        err = utils.BotChallengeError("https://example.com/test")
        assert err.url == "https://example.com/test"

    def test_bot_challenge_error_message_contains_url(self):
        """BotChallengeError message string includes the offending URL."""
        url = "https://example.com/test"
        err = utils.BotChallengeError(url)
        assert url in str(err)

    def test_bot_challenge_error_is_runtime_error(self):
        """BotChallengeError is a RuntimeError subclass."""
        assert isinstance(utils.BotChallengeError("https://x.com"), RuntimeError)

    def test_bot_challenge_error_is_importable(self):
        """BotChallengeError is publicly importable from sportsipy.utils."""
        from sportsipy.utils import BotChallengeError

        assert BotChallengeError is utils.BotChallengeError

    # ------------------------------------------------------------------
    # _http_get() routing — curl_cffi vs. requests fallback
    # ------------------------------------------------------------------

    def test_http_get_uses_requests_when_curl_cffi_unavailable(self, monkeypatch):
        """_http_get() calls requests.get when _CURL_CFFI_AVAILABLE is False."""

        class FakeResponse:
            status_code = 200
            text = "ok"

        calls = []

        def fake_get(url, **kwargs):
            calls.append(url)
            return FakeResponse()

        monkeypatch.setattr(utils, "_CURL_CFFI_AVAILABLE", False)
        monkeypatch.setattr(utils.requests, "get", fake_get)

        result = utils._http_get("https://example.com/test")

        assert result is not None
        assert result.status_code == 200
        assert calls == ["https://example.com/test"]

    def test_http_get_uses_curl_cffi_when_available(self, monkeypatch):
        """_http_get() calls _cffi_requests.get when _CURL_CFFI_AVAILABLE is True."""

        class FakeCffiResponse:
            status_code = 200
            text = "cffi"

        cffi_calls = []
        requests_calls = []
        expected_target = utils._best_impersonate_target()

        class FakeCffiRequests:
            @staticmethod
            def get(url, **kwargs):
                cffi_calls.append(url)
                assert kwargs.get("impersonate") == expected_target
                return FakeCffiResponse()

        monkeypatch.setattr(utils, "_CURL_CFFI_AVAILABLE", True)
        monkeypatch.setattr(utils, "_cffi_requests", FakeCffiRequests())
        monkeypatch.setattr(utils.requests, "get", lambda *_a, **_kw: requests_calls.append(1))

        result = utils._http_get("https://example.com/test")

        assert result is not None
        assert result.status_code == 200
        assert cffi_calls == ["https://example.com/test"]
        assert requests_calls == []  # requests.get should NOT be called

    def test_http_get_falls_back_to_requests_on_curl_cffi_exception(self, monkeypatch):
        """_http_get() falls back to requests.get when curl_cffi raises."""

        class FakeResponse:
            status_code = 200
            text = "fallback"

        class FakeCffiRequests:
            @staticmethod
            def get(url, **kwargs):
                raise OSError("curl_cffi failure")

        monkeypatch.setattr(utils, "_CURL_CFFI_AVAILABLE", True)
        monkeypatch.setattr(utils, "_cffi_requests", FakeCffiRequests())
        monkeypatch.setattr(utils.requests, "get", lambda *_a, **_kw: FakeResponse())

        result = utils._http_get("https://example.com/test")

        assert result is not None
        assert result.status_code == 200
        assert result.text == "fallback"

    def test_http_get_merges_browser_headers(self, monkeypatch):
        """_http_get() merges _BROWSER_HEADERS into the outbound request."""
        captured = {}

        def fake_get(url, headers=None, **kwargs):
            captured["headers"] = headers
            return type("R", (), {"status_code": 200, "text": "ok"})()

        monkeypatch.setattr(utils, "_CURL_CFFI_AVAILABLE", False)
        monkeypatch.setattr(utils.requests, "get", fake_get)

        utils._http_get("https://example.com/test")

        assert "User-Agent" in captured["headers"]
        assert "Chrome" in captured["headers"]["User-Agent"]

    # ------------------------------------------------------------------
    # get_page_source() — challenge-detection pipeline
    # ------------------------------------------------------------------

    def test_get_page_source_returns_none_on_challenge_without_playwright(self, monkeypatch):
        """get_page_source() returns None when the response is a bot challenge."""

        class Response:
            status_code = 200
            text = _CHALLENGE_BODIES["just_a_moment"]

        monkeypatch.setenv("SPORTSIPY_OFFLINE", "0")
        monkeypatch.setattr(utils, "_cache_read", lambda _url: None)
        monkeypatch.setattr(utils, "_request_with_retries", lambda *_a, **_kw: Response())
        monkeypatch.setattr(utils, "_PLAYWRIGHT_AVAILABLE", False)

        assert utils.get_page_source("https://example.com") is None

    def test_get_page_source_challenge_triggers_playwright_fallback(self, monkeypatch):
        """When curl_cffi returns a challenge body, Playwright is tried automatically."""

        class ChallengeResponse:
            status_code = 200
            text = _CHALLENGE_BODIES["just_a_moment"]

        class Page:
            def add_init_script(self, *_a, **_kw):
                return None

            def goto(self, *_a, **_kw):
                return None

            def content(self):
                return _CLEAN_HTML

        class BrowserContext:
            def new_page(self):
                return Page()

        class Browser:
            def new_context(self, **_kw):
                return BrowserContext()

            def close(self):
                return None

        class Chromium:
            def launch(self, **_kwargs):
                return Browser()

        class PlaywrightSession:
            chromium = Chromium()

        class Context:
            def __enter__(self):
                return PlaywrightSession()

            def __exit__(self, *_a):
                return False

        monkeypatch.setenv("SPORTSIPY_OFFLINE", "0")
        monkeypatch.setenv("SPORTSIPY_DISABLE_PLAYWRIGHT", "")
        monkeypatch.setattr(utils, "_cache_read", lambda _url: None)
        monkeypatch.setattr(utils, "_cache_write", lambda *_a, **_kw: None)
        monkeypatch.setattr(utils, "_request_with_retries", lambda *_a, **_kw: ChallengeResponse())
        monkeypatch.setattr(utils, "_PLAYWRIGHT_AVAILABLE", True)
        monkeypatch.setattr(utils, "sync_playwright", lambda: Context())

        result = utils.get_page_source("https://example.com")

        assert result == _CLEAN_HTML

    def test_get_page_source_disable_playwright_suppresses_fallback(self, monkeypatch):
        """SPORTSIPY_DISABLE_PLAYWRIGHT=1 prevents Playwright auto-fallback on challenge."""
        playwright_called = []

        class ChallengeResponse:
            status_code = 200
            text = _CHALLENGE_BODIES["just_a_moment"]

        monkeypatch.setenv("SPORTSIPY_OFFLINE", "0")
        monkeypatch.setenv("SPORTSIPY_DISABLE_PLAYWRIGHT", "1")
        monkeypatch.setattr(utils, "_cache_read", lambda _url: None)
        monkeypatch.setattr(utils, "_request_with_retries", lambda *_a, **_kw: ChallengeResponse())
        monkeypatch.setattr(utils, "_PLAYWRIGHT_AVAILABLE", True)
        monkeypatch.setattr(
            utils, "_fetch_with_playwright", lambda _url: playwright_called.append(1) or _CLEAN_HTML
        )

        result = utils.get_page_source("https://example.com")

        assert result is None  # challenge, no bypass
        assert playwright_called == []  # Playwright was never called

    def test_get_page_source_clean_html_not_treated_as_challenge(self, monkeypatch):
        """Normal HTML is returned as-is; _is_bot_challenge() must not fire."""

        class Response:
            status_code = 200
            text = _CLEAN_HTML

        monkeypatch.setenv("SPORTSIPY_OFFLINE", "0")
        monkeypatch.setattr(utils, "_cache_read", lambda _url: None)
        monkeypatch.setattr(utils, "_cache_write", lambda *_a, **_kw: None)
        monkeypatch.setattr(utils, "_request_with_retries", lambda *_a, **_kw: Response())
        monkeypatch.setattr(utils, "_PLAYWRIGHT_AVAILABLE", False)

        assert utils.get_page_source("https://example.com") == _CLEAN_HTML

    # ------------------------------------------------------------------
    # url_exists() — GET-based behaviour
    # ------------------------------------------------------------------

    def test_url_exists_returns_true_when_page_source_returns_html(self, monkeypatch):
        """url_exists() returns True when get_page_source() returns non-None HTML."""
        monkeypatch.setattr(utils, "get_page_source", lambda _url: _CLEAN_HTML)
        assert utils.url_exists("https://example.com/page")

    def test_url_exists_returns_false_when_page_source_returns_none(self, monkeypatch):
        """url_exists() returns False when get_page_source() returns None."""
        monkeypatch.setattr(utils, "get_page_source", lambda _url: None)
        assert not utils.url_exists("https://example.com/missing")

    def test_url_exists_returns_false_on_runtime_error(self, monkeypatch):
        """url_exists() catches RuntimeError from get_page_source() and returns False."""

        def raise_runtime(_url):
            raise RuntimeError("fetch failed")

        monkeypatch.setattr(utils, "get_page_source", raise_runtime)
        assert not utils.url_exists("https://example.com/error")

    # ------------------------------------------------------------------
    # Camoufox tier — get_page_source() pipeline
    # ------------------------------------------------------------------

    def test_get_page_source_challenge_triggers_camoufox_fallback(self, monkeypatch):
        """When curl_cffi returns a challenge and camoufox is available, camoufox is tried."""
        camoufox_called = []

        class ChallengeResponse:
            status_code = 200
            text = _CHALLENGE_BODIES["just_a_moment"]

        def fake_camoufox(_url):
            camoufox_called.append(_url)
            return _CLEAN_HTML

        monkeypatch.setenv("SPORTSIPY_OFFLINE", "0")
        monkeypatch.setattr(utils, "_cache_read", lambda _url: None)
        monkeypatch.setattr(utils, "_cache_write", lambda *_a, **_kw: None)
        monkeypatch.setattr(utils, "_request_with_retries", lambda *_a, **_kw: ChallengeResponse())
        monkeypatch.setattr(utils, "_CAMOUFOX_AVAILABLE", True)
        monkeypatch.setattr(utils, "_fetch_with_camoufox", fake_camoufox)

        result = utils.get_page_source("https://example.com")

        assert result == _CLEAN_HTML
        assert camoufox_called == ["https://example.com"]

    def test_get_page_source_camoufox_success_skips_playwright(self, monkeypatch):
        """When camoufox succeeds, Playwright is not tried."""
        playwright_called = []

        class ChallengeResponse:
            status_code = 200
            text = _CHALLENGE_BODIES["just_a_moment"]

        monkeypatch.setenv("SPORTSIPY_OFFLINE", "0")
        monkeypatch.setattr(utils, "_cache_read", lambda _url: None)
        monkeypatch.setattr(utils, "_cache_write", lambda *_a, **_kw: None)
        monkeypatch.setattr(utils, "_request_with_retries", lambda *_a, **_kw: ChallengeResponse())
        monkeypatch.setattr(utils, "_CAMOUFOX_AVAILABLE", True)
        monkeypatch.setattr(utils, "_fetch_with_camoufox", lambda _url: _CLEAN_HTML)
        monkeypatch.setattr(utils, "_PLAYWRIGHT_AVAILABLE", True)
        monkeypatch.setattr(
            utils,
            "_fetch_with_playwright",
            lambda _url: playwright_called.append(1) or _CLEAN_HTML,
        )

        result = utils.get_page_source("https://example.com")

        assert result == _CLEAN_HTML
        assert playwright_called == []

    def test_get_page_source_camoufox_challenge_falls_through_to_playwright(self, monkeypatch):
        """When camoufox returns a challenge, Playwright is tried next."""
        playwright_called = []

        class ChallengeResponse:
            status_code = 200
            text = _CHALLENGE_BODIES["just_a_moment"]

        def fake_playwright(_url):
            playwright_called.append(_url)
            return _CLEAN_HTML

        monkeypatch.setenv("SPORTSIPY_OFFLINE", "0")
        monkeypatch.setenv("SPORTSIPY_DISABLE_PLAYWRIGHT", "")
        monkeypatch.setattr(utils, "_cache_read", lambda _url: None)
        monkeypatch.setattr(utils, "_cache_write", lambda *_a, **_kw: None)
        monkeypatch.setattr(utils, "_request_with_retries", lambda *_a, **_kw: ChallengeResponse())
        monkeypatch.setattr(utils, "_CAMOUFOX_AVAILABLE", True)
        # Camoufox returns a challenge body — cannot bypass
        monkeypatch.setattr(
            utils,
            "_fetch_with_camoufox",
            lambda _url: _CHALLENGE_BODIES["just_a_moment"],
        )
        monkeypatch.setattr(utils, "_PLAYWRIGHT_AVAILABLE", True)
        monkeypatch.setattr(utils, "sync_playwright", lambda: None)  # truthy
        monkeypatch.setattr(utils, "_fetch_with_playwright", fake_playwright)

        result = utils.get_page_source("https://example.com")

        assert result == _CLEAN_HTML
        assert playwright_called == ["https://example.com"]

    def test_get_page_source_disable_camoufox_suppresses_tier2(self, monkeypatch):
        """SPORTSIPY_DISABLE_CAMOUFOX=1 prevents the camoufox tier."""
        camoufox_called = []

        class ChallengeResponse:
            status_code = 200
            text = _CHALLENGE_BODIES["just_a_moment"]

        monkeypatch.setenv("SPORTSIPY_OFFLINE", "0")
        monkeypatch.setenv("SPORTSIPY_DISABLE_CAMOUFOX", "1")
        monkeypatch.setattr(utils, "_cache_read", lambda _url: None)
        monkeypatch.setattr(utils, "_request_with_retries", lambda *_a, **_kw: ChallengeResponse())
        monkeypatch.setattr(utils, "_CAMOUFOX_AVAILABLE", True)
        monkeypatch.setattr(
            utils,
            "_fetch_with_camoufox",
            lambda _url: camoufox_called.append(1) or _CLEAN_HTML,
        )
        monkeypatch.setattr(utils, "_PLAYWRIGHT_AVAILABLE", False)

        result = utils.get_page_source("https://example.com")

        assert result is None
        assert camoufox_called == []

    def test_get_page_source_camoufox_not_tried_when_clean_html(self, monkeypatch):
        """Camoufox is not triggered when Tier 1 returns clean HTML."""
        camoufox_called = []

        class Response:
            status_code = 200
            text = _CLEAN_HTML

        monkeypatch.setenv("SPORTSIPY_OFFLINE", "0")
        monkeypatch.setattr(utils, "_cache_read", lambda _url: None)
        monkeypatch.setattr(utils, "_cache_write", lambda *_a, **_kw: None)
        monkeypatch.setattr(utils, "_request_with_retries", lambda *_a, **_kw: Response())
        monkeypatch.setattr(utils, "_CAMOUFOX_AVAILABLE", True)
        monkeypatch.setattr(
            utils,
            "_fetch_with_camoufox",
            lambda _url: camoufox_called.append(1) or _CLEAN_HTML,
        )

        result = utils.get_page_source("https://example.com")

        assert result == _CLEAN_HTML
        assert camoufox_called == []

    def test_get_page_source_enable_playwright_skips_camoufox(self, monkeypatch):
        """SPORTSIPY_ENABLE_PLAYWRIGHT=1 skips both Tier 1 and Tier 2 (camoufox)."""
        camoufox_called = []

        monkeypatch.setenv("SPORTSIPY_OFFLINE", "0")
        monkeypatch.setenv("SPORTSIPY_ENABLE_PLAYWRIGHT", "1")
        monkeypatch.setattr(utils, "_cache_read", lambda _url: None)
        monkeypatch.setattr(utils, "_cache_write", lambda *_a, **_kw: None)
        monkeypatch.setattr(utils, "_CAMOUFOX_AVAILABLE", True)
        monkeypatch.setattr(
            utils,
            "_fetch_with_camoufox",
            lambda _url: camoufox_called.append(1) or _CLEAN_HTML,
        )
        monkeypatch.setattr(utils, "_PLAYWRIGHT_AVAILABLE", True)
        monkeypatch.setattr(utils, "sync_playwright", lambda: None)
        monkeypatch.setattr(utils, "_fetch_with_playwright", lambda _url: _CLEAN_HTML)

        result = utils.get_page_source("https://example.com")

        assert result == _CLEAN_HTML
        assert camoufox_called == []

    def test_fetch_with_camoufox_returns_none_when_not_installed(self, monkeypatch):
        """_fetch_with_camoufox() returns None when _CamoufoxContext is None."""
        monkeypatch.setattr(utils, "_CamoufoxContext", None)
        assert utils._fetch_with_camoufox("https://example.com") is None

    def test_get_page_source_skips_browser_fallback_when_sync_browser_disabled(self, monkeypatch):
        """When sync browser fallback is disabled, camoufox/playwright tiers are skipped."""
        camoufox_called = []
        playwright_called = []

        class ChallengeResponse:
            status_code = 200
            text = _CHALLENGE_BODIES["just_a_moment"]

        monkeypatch.setenv("SPORTSIPY_OFFLINE", "0")
        monkeypatch.setattr(utils, "_SYNC_BROWSER_FALLBACK_DISABLED", True)
        monkeypatch.setattr(utils, "_cache_read", lambda _url: None)
        monkeypatch.setattr(utils, "_request_with_retries", lambda *_a, **_kw: ChallengeResponse())
        monkeypatch.setattr(utils, "_CAMOUFOX_AVAILABLE", True)
        monkeypatch.setattr(utils, "_PLAYWRIGHT_AVAILABLE", True)
        monkeypatch.setattr(utils, "sync_playwright", lambda: None)
        monkeypatch.setattr(
            utils,
            "_fetch_with_camoufox",
            lambda _url: camoufox_called.append(_url) or _CLEAN_HTML,
        )
        monkeypatch.setattr(
            utils,
            "_fetch_with_playwright",
            lambda _url: playwright_called.append(_url) or _CLEAN_HTML,
        )

        result = utils.get_page_source("https://example.com")

        assert result is None
        assert camoufox_called == []
        assert playwright_called == []

    def test_disable_sync_browser_fallback_if_loop_error_sets_global_flag(self, monkeypatch):
        """Loop-incompat sync API errors disable future sync browser fallbacks."""
        monkeypatch.setattr(utils, "_SYNC_BROWSER_FALLBACK_DISABLED", False)

        loop_error = RuntimeError(
            "It looks like you are using Playwright Sync API inside the asyncio loop."
        )
        disabled = utils._disable_sync_browser_fallback_if_loop_error(loop_error)

        assert disabled
        assert utils._SYNC_BROWSER_FALLBACK_DISABLED

    def test_fetch_with_camoufox_geoip_default_is_disabled(self, monkeypatch):
        """Camoufox launch defaults geoip to False unless explicitly enabled."""
        captured_kwargs = {}

        class _Page:
            url = "https://example.com"

            def goto(self, *_a, **_kw):
                return None

            def content(self):
                return _CLEAN_HTML

            def wait_for_timeout(self, *_a, **_kw):
                return None

        class _Context:
            def __init__(self, **kwargs):
                captured_kwargs.update(kwargs)

            def __enter__(self):
                return self

            def __exit__(self, *_a):
                return False

            @property
            def pages(self):
                return []

            def new_page(self):
                return _Page()

        monkeypatch.delenv("SPORTSIPY_CAMOUFOX_GEOIP", raising=False)
        monkeypatch.setenv("SPORTSIPY_PLAYWRIGHT_SETTLE_MS", "0")
        monkeypatch.setattr(utils, "_CamoufoxContext", _Context)
        monkeypatch.setattr(utils, "_resolve_cookies", lambda _url: {})

        html = utils._fetch_with_camoufox("https://example.com")

        assert html == _CLEAN_HTML
        assert captured_kwargs.get("geoip") is False
