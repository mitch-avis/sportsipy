"""Provide utilities for test ncaaf boxscore."""

from typing import Any
from unittest.mock import patch

from flexmock import flexmock
from pyquery import PyQuery

from sportsipy import utils
from sportsipy.constants import AWAY, HOME
from sportsipy.ncaaf.boxscore import Boxscore, Boxscores


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


class MockName:
    """Represent MockName."""

    def __init__(self, name):
        """Initialize the class instance."""
        self._name = name

    def __str__(self):
        """Return the mock name string."""
        return self._name

    def text(self):
        """Return text."""
        return self._name.replace("<a>cfb/schools</a>", "")


def mock_pyquery(url, timeout=None):
    """Return mock pyquery."""

    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 404
            self.html_contents = html_contents
            self.text = html_contents

    return MockPQ("")


class TestNCAAFBoxscore:
    """Represent TestNCAAFBoxscore."""

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

    def test_winning_name_di_is_home(self):
        """Return test winning name di is home."""
        expected_name = "Home Name"
        test_name = "<a>cfb/schools</a>Home Name"

        self.boxscore._away_points = 21
        self.boxscore._home_points = 28
        self.boxscore._home_name = MockName(test_name)

        assert self.boxscore.winning_name == expected_name

    def test_winning_name_non_di_is_home(self):
        """Return test winning name non di is home."""
        expected_name = "Home Name"
        test_name = "Home Name"

        self.boxscore._away_points = 21
        self.boxscore._home_points = 28
        self.boxscore._home_name = MockName(test_name)

        assert self.boxscore.winning_name == expected_name

    def test_winning_name_di_is_away(self):
        """Return test winning name di is away."""
        expected_name = "Away Name"
        test_name = "<a>cfb/schools</a>Away Name"

        self.boxscore._away_points = 28
        self.boxscore._home_points = 21
        self.boxscore._away_name = MockName(test_name)

        assert self.boxscore.winning_name == expected_name

    def test_winning_name_non_di_is_away(self):
        """Return test winning name non di is away."""
        expected_name = "Away Name"
        test_name = "Away Name"

        self.boxscore._away_points = 28
        self.boxscore._home_points = 21
        self.boxscore._away_name = MockName(test_name)

        assert self.boxscore.winning_name == expected_name

    def test_winning_abbr_di_is_home(self):
        """Return test winning abbr di is home."""
        expected_name = "HOME"
        test_name = "<a>cfb/schools</a>HOME"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_points = 21
        self.boxscore._home_points = 28
        self.boxscore._home_name = MockName(test_name)

        assert self.boxscore.winning_abbr == expected_name

    def test_winning_abbr_non_di_is_home(self):
        """Return test winning abbr non di is home."""
        expected_name = "HOME"
        test_name = "HOME"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_points = 21
        self.boxscore._home_points = 28
        self.boxscore._home_name = MockName(test_name)

        assert self.boxscore.winning_abbr == expected_name

    def test_winning_abbr_di_is_away(self):
        """Return test winning abbr di is away."""
        expected_name = "AWAY"
        test_name = "<a>cfb/schools</a>AWAY"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_points = 28
        self.boxscore._home_points = 21
        self.boxscore._away_name = MockName(test_name)

        assert self.boxscore.winning_abbr == expected_name

    def test_winning_abbr_non_di_is_away(self):
        """Return test winning abbr non di is away."""
        expected_name = "AWAY"
        test_name = "AWAY"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_points = 28
        self.boxscore._home_points = 21
        self.boxscore._away_name = MockName(test_name)

        assert self.boxscore.winning_abbr == expected_name

    def test_losing_name_di_is_home(self):
        """Return test losing name di is home."""
        expected_name = "Home Name"
        test_name = "<a>cfb/schools</a>Home Name"

        self.boxscore._away_points = 28
        self.boxscore._home_points = 21
        self.boxscore._home_name = MockName(test_name)

        assert self.boxscore.losing_name == expected_name

    def test_losing_name_non_di_is_home(self):
        """Return test losing name non di is home."""
        expected_name = "Home Name"
        test_name = "Home Name"

        self.boxscore._away_points = 28
        self.boxscore._home_points = 21
        self.boxscore._home_name = MockName(test_name)

        assert self.boxscore.losing_name == expected_name

    def test_losing_name_di_is_away(self):
        """Return test losing name di is away."""
        expected_name = "Away Name"
        test_name = "<a>cfb/schools</a>Away Name"

        self.boxscore._away_points = 21
        self.boxscore._home_points = 28
        self.boxscore._away_name = MockName(test_name)

        assert self.boxscore.losing_name == expected_name

    def test_losing_name_non_di_is_away(self):
        """Return test losing name non di is away."""
        expected_name = "Away Name"
        test_name = "Away Name"

        self.boxscore._away_points = 21
        self.boxscore._home_points = 28
        self.boxscore._away_name = MockName(test_name)

        assert self.boxscore.losing_name == expected_name

    def test_losing_abbr_di_is_home(self):
        """Return test losing abbr di is home."""
        expected_name = "HOME"
        test_name = "<a>cfb/schools</a>HOME"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_points = 28
        self.boxscore._home_points = 21
        self.boxscore._home_name = MockName(test_name)

        assert self.boxscore.losing_abbr == expected_name

    def test_losing_abbr_non_di_is_home(self):
        """Return test losing abbr non di is home."""
        expected_name = "HOME"
        test_name = "HOME"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_points = 28
        self.boxscore._home_points = 21
        self.boxscore._home_name = MockName(test_name)

        assert self.boxscore.losing_abbr == expected_name

    def test_losing_abbr_di_is_away(self):
        """Return test losing abbr di is away."""
        expected_name = "AWAY"
        test_name = "<a>cfb/schools</a>AWAY"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_points = 21
        self.boxscore._home_points = 28
        self.boxscore._away_name = MockName(test_name)

        assert self.boxscore.losing_abbr == expected_name

    def test_losing_abbr_non_di_is_away(self):
        """Return test losing abbr non di is away."""
        expected_name = "AWAY"
        test_name = "AWAY"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_points = 21
        self.boxscore._home_points = 28
        self.boxscore._away_name = MockName(test_name)

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
        result = Boxscore(None)._retrieve_html_page("")

        assert result is None

    def test_game_information_regular_game(self):
        """Return test game information regular game."""
        fields = ["date", "time", "stadium"]
        fields = {
            "date": "Saturday Nov 25, 2017",
            "time": "12:00 PM ET",
            "stadium": "Ross-Ade Stadium - West Lafayette, Indiana",
        }

        mock_field = """Saturday Nov 25, 2017

12:00 PM ET
Ross-Ade Stadium - West Lafayette, Indiana
Logos via Sports Logos.net / About logos
"""
        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_game_information_championship_game(self):
        """Return test game information championship game."""
        fields = ["date", "time", "stadium"]
        fields = {
            "date": "Saturday Dec 2, 2017",
            "time": "8:00 PM ET",
            "stadium": "Lucas Oil Stadium - Indianapolis, Indiana",
        }

        mock_field = """Big Ten Conference Championship

Saturday Dec 2, 2017
8:00 PM ET
Lucas Oil Stadium - Indianapolis, Indiana
Logos via Sports Logos.net / About logos
"""
        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_somewhat_limited_game_information(self):
        """Return test somewhat limited game information."""
        fields = ["date", "time", "stadium"]
        fields = {"date": "Friday Nov 24, 2017", "time": "", "stadium": ""}

        mock_field = """Friday Nov 24, 2017

Logos via Sports Logos.net / About logos
"""
        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_limited_game_information(self):
        """Return test limited game information."""
        fields = ["date", "time", "stadium"]
        fields = {"date": "Friday Nov 24, 2017", "time": "", "stadium": ""}

        mock_field = "Friday Nov 24, 2017"
        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_limited_game_information_championship(self):
        """Return test limited game information championship."""
        fields = ["date", "time", "stadium"]
        fields = {"date": "Saturday Dec 2, 2017", "time": "", "stadium": ""}

        mock_field = """Big Ten Conference Championship

Saturday Dec 2, 2017
Logos via Sports Logos.net / About logos
"""
        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_no_game_information_championship(self):
        """Return test no game information championship."""
        fields = ["date", "time", "stadium"]
        fields = {"date": "", "time": "", "stadium": ""}

        mock_field = """Big Ten Conference Championship

Logos via Sports Logos.net / About logos
"""
        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_empty_boxscore_class_returns_dataframe_of_none(self):
        """Return test empty boxscore class returns dataframe of none."""
        self.boxscore._home_points = None
        self.boxscore._away_points = None

        assert self.boxscore._home_points is None
        assert self.boxscore._away_points is None
        assert self.boxscore.dataframe is None

    def test_empty_attribute_returns_none(self):
        """Return test empty attribute returns none."""
        self.boxscore._away_rush_attempts = None

        assert self.boxscore.away_rush_attempts is None

    def test_non_int_value_returns_none(self):
        """Return test non int value returns none."""
        self.boxscore._away_rush_attempts = "bad"

        assert self.boxscore.away_rush_attempts is None


class TestNCAABBoxscores:
    """Represent TestNCAABBoxscores."""

    @patch("requests.get", side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        """Return setup method."""
        flexmock(Boxscores).should_receive("_find_games").and_return(None)
        self.boxscores = Boxscores(None)

    def test_boxscore_with_no_score_returns_none(self):
        """Return test boxscore with no score returns none."""
        mock_html = PyQuery("""<table class="teams">

<tbody>
<tr class="date"><td colspan=3>Armed Forces Bowl</td></tr>

<tr class="">
    <td><a href="/cfb/schools/army/2018.html">Army</a>\
<span class='pollrank'>&nbsp;(22)&nbsp;</span></td>
    <td class="right"></td>
    <td class="right gamelink">
        <a href="/cfb/boxscores/2018-12-22-army.html">Preview</a>
    </td>
</tr>
<tr class="">
    <td><a href="/cfb/schools/houston/2018.html">Houston</a></td>
    <td class="right"></td>
    <td class="right">&nbsp;
    </td>
</tr>
</tbody>
</table>""")
        games = self.boxscores._extract_game_info([mock_html])

        assert games == [
            {
                "home_name": "Houston",
                "home_abbr": "houston",
                "away_name": "Army",
                "away_abbr": "army",
                "boxscore": "2018-12-22-army",
                "non_di": False,
                "top_25": True,
                "home_score": None,
                "home_rank": None,
                "away_score": None,
                "away_rank": 22,
                "winning_name": None,
                "winning_abbr": None,
                "losing_name": None,
                "losing_abbr": None,
            }
        ]
