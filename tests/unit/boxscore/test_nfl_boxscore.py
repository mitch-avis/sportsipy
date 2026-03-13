"""Provide utilities for test nfl boxscore."""

from datetime import datetime
from os.path import dirname, join
from typing import Any
from unittest.mock import patch

from flexmock import flexmock
from pyquery import PyQuery

from sportsipy import utils
from sportsipy.constants import AWAY, HOME
from sportsipy.nfl.boxscore import Boxscore, Boxscores


class MockName:
    """Represent MockName."""

    def __init__(self, name):
        """Initialize the class instance."""
        self._name = name

    def text(self):
        """Return text."""
        return self._name


class MockField:
    """Represent MockField."""

    def __init__(self, field):
        """Initialize the class instance."""
        self._field = field

    def text(self):
        """Return text."""
        return self._field


class MockBoxscoreData:
    """Represent MockBoxscoreData."""

    def __init__(self, fields):
        """Initialize the class instance."""
        self._fields = fields

    def __call__(self, field):
        """Return   call  ."""
        return self

    def items(self):
        """Return items."""
        return [self._fields]


def read_file(filename):
    """Return read file."""
    filepath = join(dirname(__file__), "nfl", filename)
    return open(filepath, encoding="utf-8").read()


def mock_pyquery(url, timeout=None, status_code=404):
    """Return mock pyquery."""

    class MockPQ:
        def __init__(self, html_contents, status_code=404):
            self.url = url
            self.reason = "Bad URL"  # Used when throwing HTTPErrors
            self.headers = {}  # Used when throwing HTTPErrors
            self.status_code = status_code
            self.html_contents = html_contents
            self.text = html_contents

    if "404" in url:
        return MockPQ("404 error", 200)
    if "bad" in url:
        return MockPQ(None)
    return MockPQ(read_file(f"{url}.htm"))


class TestNFLBoxscore:
    """Represent TestNFLBoxscore."""

    @patch("requests.get", side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        """Return setup method."""
        flexmock(Boxscore).should_receive("_parse_game_data").and_return(None)

        self.boxscore: Any = Boxscore(None)

    def test_away_team_wins(self):
        """Return test away team wins."""
        self.boxscore._away_points = 28
        self.boxscore._home_points = 21

        assert self.boxscore.winner == AWAY

    def test_home_team_wins(self):
        """Return test home team wins."""
        self.boxscore._away_points = 21
        self.boxscore._home_points = 28

        assert self.boxscore.winner == HOME

    def test_winning_name_is_home(self):
        """Return test winning name is home."""
        expected_name = "Home Name"

        self.boxscore._away_points = 21
        self.boxscore._home_points = 28
        self.boxscore._home_name = MockName(expected_name)

        assert self.boxscore.winning_name == expected_name

    def test_winning_name_is_away(self):
        """Return test winning name is away."""
        expected_name = "Away Name"

        self.boxscore._away_points = 28
        self.boxscore._home_points = 21
        self.boxscore._away_name = MockName(expected_name)

        assert self.boxscore.winning_name == expected_name

    def test_winning_abbr_is_home(self):
        """Return test winning abbr is home."""
        expected_name = "HOME"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_points = 21
        self.boxscore._home_points = 28
        self.boxscore._home_name = MockName(expected_name)

        assert self.boxscore.winning_abbr == expected_name

    def test_winning_abbr_is_away(self):
        """Return test winning abbr is away."""
        expected_name = "AWAY"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_points = 28
        self.boxscore._home_points = 21
        self.boxscore._away_name = MockName(expected_name)

        assert self.boxscore.winning_abbr == expected_name

    def test_losing_name_is_home(self):
        """Return test losing name is home."""
        expected_name = "Home Name"

        self.boxscore._away_points = 28
        self.boxscore._home_points = 21
        self.boxscore._home_name = MockName(expected_name)

        assert self.boxscore.losing_name == expected_name

    def test_losing_name_is_away(self):
        """Return test losing name is away."""
        expected_name = "Away Name"

        self.boxscore._away_points = 21
        self.boxscore._home_points = 28
        self.boxscore._away_name = MockName(expected_name)

        assert self.boxscore.losing_name == expected_name

    def test_losing_abbr_is_home(self):
        """Return test losing abbr is home."""
        expected_name = "HOME"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_points = 28
        self.boxscore._home_points = 21
        self.boxscore._home_name = MockName(expected_name)

        assert self.boxscore.losing_abbr == expected_name

    def test_losing_abbr_is_away(self):
        """Return test losing abbr is away."""
        expected_name = "AWAY"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_points = 21
        self.boxscore._home_points = 28
        self.boxscore._away_name = MockName(expected_name)

        assert self.boxscore.losing_abbr == expected_name

    def test_game_summary_with_no_scores_returns_none(self):
        """Return test game summary with no scores returns none."""
        result = Boxscore(None)._parse_summary(
            PyQuery("""<table class="linescore nohover stats_table no_freeze">

    <tbody>
        <tr>
            <td class="center"></td>
            <td class="center"></td>
        </tr>
        <tr>
            <td class="center"></td>
            <td class="center"></td>
        </tr>
    </tbody>
</table>""")
        )

        assert result == {"away": [None], "home": [None]}

    @patch("requests.get", side_effect=mock_pyquery)
    def test_invalid_url_returns_none(self, *args, **kwargs):
        """Return test invalid url returns none."""
        result = Boxscore(None)._retrieve_html_page("bad")

        assert result is None

    @patch("requests.get", side_effect=mock_pyquery)
    def test_url_404_page_returns_none(self, *args, **kwargs):
        """Return test url 404 page returns none."""
        result = Boxscore(None)._retrieve_html_page("404")

        assert result is None

    def test_no_class_information_returns_dataframe_of_none(self):
        """Return test no class information returns dataframe of none."""
        self.boxscore._home_points = None
        self.boxscore._away_points = None

        assert self.boxscore.dataframe is None

    def test_empty_attribute_returns_none(self):
        """Return test empty attribute returns none."""
        self.boxscore._away_rush_attempts = None

        assert self.boxscore.away_rush_attempts is None

    def test_non_int_value_returns_none(self):
        """Return test non int value returns none."""
        self.boxscore._away_rush_attempts = "bad"

        assert self.boxscore.away_rush_attempts is None

    def test_nfl_game_information(self):
        """Return test nfl game information."""
        fields = {
            "attendance": 62881,
            "date": "Thursday Nov 8, 2018",
            "duration": "2:49",
            "stadium": "Heinz Field",
            "time": "8:20pm",
        }

        mock_field = """Thursday Nov 8, 2018

Start Time: 8:20pm
Stadium: Heinz Field
Attendance: 62,881
Time of Game: 2:49
Logos via Sports Logos.net / About logos
"""

        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_nfl_game_limited_information(self):
        """Return test nfl game limited information."""
        fields = {
            "attendance": 22000,
            "date": "Sunday Sep 8, 1940",
            "duration": None,
            "stadium": "Forbes Field",
            "time": None,
        }

        mock_field = """Sunday Sep 8, 1940

Stadium: Forbes Field
Attendance: 22,000
Logos via Sports Logos.net / About logos
"""

        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_nfl_away_abbreviation(self):
        """Return test nfl away abbreviation."""
        self.boxscore._away_name = (
            '<a href="/teams/kan/2018.htm" itemprop="name">Kansas City Chiefs</a>'
        )

        assert self.boxscore.away_abbreviation == "kan"

    def test_nfl_home_abbreviation(self):
        """Return test nfl home abbreviation."""
        self.boxscore._home_name = (
            '<a href="/teams/nwe/2018.htm" itemprop="name">New England Patriots</a>'
        )

        assert self.boxscore.home_abbreviation == "nwe"

    def test_nfl_datetime_missing_time(self):
        """Return test nfl datetime missing time."""
        self.boxscore._date = "Sunday Oct 7, 2018"
        self.boxscore._time = None

        assert self.boxscore.datetime == datetime(2018, 10, 7)

    def test_nfl_game_details(self):
        """Return test nfl game details."""
        fields = {
            "won_toss": "Dolphins",
            "roof": "Outdoors",
            "surface": "Fieldturf",
            "weather": "87 degrees, wind 4 mph",
            "vegas_line": "Cincinnati Bengals -6.5",
            "over_under": "47.5 (under)",
        }

        mock_field = """<table id="game_info">

<tr><th data-stat="info">Won Toss</th><td data-stat="stat">Dolphins</td></tr>
<tr><th data-stat="info">Roof</th><td data-stat="stat">outdoors</td></tr>
<tr><th data-stat="info">Surface</th><td data-stat="stat">fieldturf </td></tr>
<tr><th data-stat="info">Duration</th><td data-stat="stat">3:02</td></tr>
<tr><th data-stat="info">Attendance</th><td data-stat="stat">52,708</td></tr>
<tr><th data-stat="info">Weather</th>
    <td data-stat="stat">87 degrees, wind 4 mph</td></tr>
<tr><th data-stat="info">Vegas Line</th>
    <td data-stat="stat">Cincinnati Bengals -6.5</td></tr>
<tr><th data-stat="info">Over/Under</th>
    <td data-stat="stat">47.5 <b>(under)</b></td></tr>
</table>
"""

        self.boxscore._parse_game_details(PyQuery(mock_field))

        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_finding_home_team_with_no_abbrs(self):
        """Return test finding home team with no abbrs."""
        mock_html = PyQuery('<td data-stat="team">KAN</td>')
        self.boxscore._home_abbr = None
        self.boxscore._away_abbr = None
        self.boxscore._home_name = '<a href="/teams/kan/2018.htm">Kansas City Chiefs</a>'
        team = self.boxscore._find_home_or_away(mock_html)

        assert team == HOME

    def test_finding_away_team_with_no_abbrs(self):
        """Return test finding away team with no abbrs."""
        mock_html = PyQuery('<td data-stat="team">HTX</td>')
        self.boxscore._home_abbr = None
        self.boxscore._away_abbr = None
        self.boxscore._home_name = '<a href="/teams/kan/2018.htm">Kansas City Chiefs</a>'
        team = self.boxscore._find_home_or_away(mock_html)

        assert team == AWAY

    def test_missing_abbreviations(self):
        """Return test missing abbreviations."""
        table = '<table id="team_stats"><thead></thead></table>'
        output = self.boxscore._alt_abbreviations(PyQuery(table))

        assert output == (None, None)


class TestNFLBoxscores:
    """Represent TestNFLBoxscores."""

    @patch("requests.get", side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        """Return setup method."""
        flexmock(Boxscores).should_receive("_find_games").and_return(None)
        self.boxscores = Boxscores(None, None)

    def test_improper_loser_boxscore_format_skips_game(self):
        """Return test improper loser boxscore format skips game."""
        flexmock(Boxscores).should_receive("_get_team_details").and_return(
            (None, None, None, None, None, None)
        )
        mock_html = PyQuery("""<table class="teams">

<tbody>
<tr class="date"><td colspan=3>Dec 9, 2018</td></tr>

<tr class="winner">
    <td><a href="/teams/nyj/2018.htm">New York Jets</a></td>
    <td class="right">27</td>
    <td class="right gamelink">
        <a href="/boxscores/201812090buf.htm">Final</a>
    </td>
</tr>
<tr class="loser">
    <td class="right">23</td>
    <td class="right">&nbsp;
    </td>
</tr>
</tbody>
</table>""")
        games = self.boxscores._extract_game_info([mock_html])

        assert len(games) == 0

    def test_improper_winner_boxscore_format_skips_game(self):
        """Return test improper winner boxscore format skips game."""
        flexmock(Boxscores).should_receive("_get_team_details").and_return(
            (None, None, None, None, None, None)
        )
        mock_html = PyQuery("""<table class="teams">

<tbody>
<tr class="date"><td colspan=3>Dec 9, 2018</td></tr>

<tr class="winner">
    <td class="right">27</td>
    <td class="right gamelink">
    </td>
</tr>
<tr class="loser">
    <td><a href="/teams/buf/2018.htm">Buffalo Bills</a></td>
    <td class="right">23</td>
    <td class="right">&nbsp;
    </td>
</tr>
</tbody>
</table>""")
        games = self.boxscores._extract_game_info([mock_html])

        assert len(games) == 0

    def test_boxscore_with_no_score_returns_none(self):
        """Return test boxscore with no score returns none."""
        mock_html = PyQuery("""<table class="teams">

<tbody>
<tr class="date"><td colspan=3>Dec 9, 2018</td></tr>

<tr class="loser">
    <td><a href="/teams/nyj/2018.htm">New York Jets</a></td>
    <td class="right gamelink">
        <a href="/boxscores/201812090buf.htm">Final</a>
    </td>
</tr>
<tr class="loser">
    <td><a href="/teams/buf/2018.htm">Buffalo Bills</a></td>
    <td class="right">&nbsp;
    </td>
</tr>
</tbody>
</table>""")
        games = self.boxscores._extract_game_info([mock_html])

        assert games == [
            {
                "home_name": "Buffalo Bills",
                "home_abbr": "buf",
                "away_name": "New York Jets",
                "away_abbr": "nyj",
                "boxscore": "201812090buf",
                "winning_name": None,
                "winning_abbr": None,
                "losing_name": None,
                "losing_abbr": None,
                "home_score": None,
                "away_score": None,
            }
        ]
