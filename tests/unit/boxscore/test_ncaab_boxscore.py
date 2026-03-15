"""Provide utilities for test ncaab boxscore."""

from typing import Any
from unittest.mock import patch

from flexmock import flexmock
from pyquery import PyQuery

from sportsipy import utils
from sportsipy.constants import AWAY, HOME
from sportsipy.ncaab.boxscore import Boxscore, Boxscores


class MockBoxscore:
    """Represent MockBoxscore."""

    def __init__(self, name):
        """Initialize the class instance."""
        self._name = name

    def __call__(self, scheme):
        """Return   call  ."""
        return self._name


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
        return self._name.replace("<a>cbb/schools</a>", "")


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


def mock_pyquery(url, timeout=None, **kwargs):
    """Return mock pyquery."""

    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 404
            self.html_contents = html_contents
            self.text = html_contents

    return MockPQ("")


class TestNCAABBoxscore:
    """Represent TestNCAABBoxscore."""

    @patch("requests.get", side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        """Return setup method."""
        flexmock(Boxscore).should_receive("_parse_game_data").and_return(None)

        self.boxscore: Any = Boxscore(None)

    def test_away_team_wins(self):
        """Return test away team wins."""
        self.boxscore._away_points = 75
        self.boxscore._home_points = 70

        assert self.boxscore.winner == AWAY

    def test_home_team_wins(self):
        """Return test home team wins."""
        self.boxscore._away_points = 70
        self.boxscore._home_points = 75

        assert self.boxscore.winner == HOME

    def test_winning_name_di_is_home(self):
        """Return test winning name di is home."""
        expected_name = "Home Name"
        test_name = "<a>cbb/schools</a>Home Name"

        self.boxscore._away_points = 70
        self.boxscore._home_points = 75
        self.boxscore._home_name = MockName(test_name)

        assert self.boxscore.winning_name == expected_name

    def test_winning_name_non_di_is_home(self):
        """Return test winning name non di is home."""
        expected_name = "Home Name"
        test_name = "Home Name"

        self.boxscore._away_points = 70
        self.boxscore._home_points = 75
        self.boxscore._home_name = MockName(test_name)

        assert self.boxscore.winning_name == expected_name

    def test_winning_name_di_is_away(self):
        """Return test winning name di is away."""
        expected_name = "Away Name"
        test_name = "<a>cbb/schools</a>Away Name"

        self.boxscore._away_points = 75
        self.boxscore._home_points = 70
        self.boxscore._away_name = MockName(test_name)

        assert self.boxscore.winning_name == expected_name

    def test_winning_name_non_di_is_away(self):
        """Return test winning name non di is away."""
        expected_name = "Away Name"
        test_name = "Away Name"

        self.boxscore._away_points = 75
        self.boxscore._home_points = 70
        self.boxscore._away_name = MockName(test_name)

        assert self.boxscore.winning_name == expected_name

    def test_winning_abbr_di_is_home(self):
        """Return test winning abbr di is home."""
        expected_name = "Home"
        test_name = "<a>cbb/schools</a>HOME"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_points = 70
        self.boxscore._home_points = 75
        self.boxscore._home_name = MockName(test_name)

        assert self.boxscore.winning_abbr == expected_name

    def test_winning_abbr_non_di_is_home(self):
        """Return test winning abbr non di is home."""
        expected_name = "HOME"
        test_name = "HOME"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_points = 70
        self.boxscore._home_points = 75
        self.boxscore._home_name = MockName(test_name)

        assert self.boxscore.winning_abbr == expected_name

    def test_winning_abbr_di_is_away(self):
        """Return test winning abbr di is away."""
        expected_name = "AWAY"
        test_name = "<a>cbb/schools</a>AWAY"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_points = 75
        self.boxscore._home_points = 70
        self.boxscore._away_name = MockName(test_name)

        assert self.boxscore.winning_abbr == expected_name

    def test_winning_abbr_non_di_is_away(self):
        """Return test winning abbr non di is away."""
        expected_name = "AWAY"
        test_name = "AWAY"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_points = 75
        self.boxscore._home_points = 70
        self.boxscore._away_name = MockName(test_name)

        assert self.boxscore.winning_abbr == expected_name

    def test_losing_name_di_is_home(self):
        """Return test losing name di is home."""
        expected_name = "Home Name"
        test_name = "<a>cbb/schools</a>Home Name"

        self.boxscore._away_points = 75
        self.boxscore._home_points = 70
        self.boxscore._home_name = MockName(test_name)

        assert self.boxscore.losing_name == expected_name

    def test_losing_name_non_di_is_home(self):
        """Return test losing name non di is home."""
        expected_name = "Home Name"
        test_name = "Home Name"

        self.boxscore._away_points = 75
        self.boxscore._home_points = 70
        self.boxscore._home_name = MockName(test_name)

        assert self.boxscore.losing_name == expected_name

    def test_losing_name_di_is_away(self):
        """Return test losing name di is away."""
        expected_name = "Away Name"
        test_name = "<a>cbb/schools</a>Away Name"

        self.boxscore._away_points = 70
        self.boxscore._home_points = 75
        self.boxscore._away_name = MockName(test_name)

        assert self.boxscore.losing_name == expected_name

    def test_losing_name_non_di_is_away(self):
        """Return test losing name non di is away."""
        expected_name = "Away Name"
        test_name = "Away Name"

        self.boxscore._away_points = 70
        self.boxscore._home_points = 75
        self.boxscore._away_name = MockName(test_name)

        assert self.boxscore.losing_name == expected_name

    def test_losing_abbr_di_is_home(self):
        """Return test losing abbr di is home."""
        expected_name = "HOME"
        test_name = "<a>cbb/schools</a>HOME"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_points = 75
        self.boxscore._home_points = 70
        self.boxscore._home_name = MockName(test_name)

        assert self.boxscore.losing_abbr == expected_name

    def test_losing_abbr_non_di_is_home(self):
        """Return test losing abbr non di is home."""
        expected_name = "HOME"
        test_name = "HOME"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_points = 75
        self.boxscore._home_points = 70
        self.boxscore._home_name = MockName(test_name)

        assert self.boxscore.losing_abbr == expected_name

    def test_losing_abbr_di_is_away(self):
        """Return test losing abbr di is away."""
        expected_name = "AWAY"
        test_name = "<a>cbb/schools</a>AWAY"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_points = 70
        self.boxscore._home_points = 75
        self.boxscore._away_name = MockName(test_name)

        assert self.boxscore.losing_abbr == expected_name

    def test_losing_abbr_non_di_is_away(self):
        """Return test losing abbr non di is away."""
        expected_name = "AWAY"
        test_name = "AWAY"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_points = 70
        self.boxscore._home_points = 75
        self.boxscore._away_name = MockName(test_name)

        assert self.boxscore.losing_abbr == expected_name

    def test_invalid_away_record_returns_default_wins(self):
        """Return test invalid away record returns default wins."""
        self.boxscore._away_record = "Purdue (1)"

        assert self.boxscore.away_wins == 0

    def test_invalid_away_record_returns_default_losses(self):
        """Return test invalid away record returns default losses."""
        self.boxscore._away_record = "Purdue (1)"

        assert self.boxscore.away_losses == 0

    def test_invalid_home_record_returns_default_wins(self):
        """Return test invalid home record returns default wins."""
        self.boxscore._home_record = "Purdue (1)"

        assert self.boxscore.home_wins == 0

    def test_invalid_home_record_returns_default_losses(self):
        """Return test invalid home record returns default losses."""
        self.boxscore._home_record = "Purdue (1)"

        assert self.boxscore.home_losses == 0

    def test_game_summary_with_no_scores_returns_none(self):
        """Return test game summary with no scores returns none."""
        result = Boxscore(None)._parse_summary(
            PyQuery("""<table id="line-score">

    <tbody>
        <tr>
            <td class="right"></td>
            <td class="right"></td>
        </tr>
        <tr>
            <td class="right"></td>
            <td class="right"></td>
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

    def test_parsing_name_for_non_di_school(self):
        """Return test parsing name for non di school."""
        name = "Away name"
        boxscore = MockBoxscore(name)

        result = self.boxscore._parse_name("away_name", boxscore)

        assert result == name

    def test_no_home_free_throw_percentage_returns_default(self):
        """Return test no home free throw percentage returns default."""
        self.boxscore._home_free_throw_percentage = ""

        assert self.boxscore.home_free_throw_percentage is None

    def test_no_away_free_throw_percentage_returns_default(self):
        """Return test no away free throw percentage returns default."""
        self.boxscore._away_free_throw_percentage = ""

        assert self.boxscore.away_free_throw_percentage is None

    def test_empty_boxscore_class_returns_dataframe_of_none(self):
        """Return test empty boxscore class returns dataframe of none."""
        self.boxscore._home_points = None
        self.boxscore._away_points = None

        assert self.boxscore._home_points is None
        assert self.boxscore._away_points is None
        assert self.boxscore.dataframe is None

    def test_away_win_percentage_no_games_played_returns_default(self):
        """Return test away win percentage no games played returns default."""
        self.boxscore._away_record = "0-0"

        assert self.boxscore.away_wins == 0
        assert self.boxscore.away_losses == 0
        assert self.boxscore.away_win_percentage == 0.0

    def test_home_win_percentage_no_games_played_returns_default(self):
        """Return test home win percentage no games played returns default."""
        self.boxscore._home_record = "0-0"

        assert self.boxscore.home_wins == 0
        assert self.boxscore.home_losses == 0
        assert self.boxscore.home_win_percentage == 0.0

    def test_ranking_with_no_boxscores(self):
        """Return test ranking with no boxscores."""
        ranking = self.boxscore._parse_ranking("home_ranking", MockBoxscore(""))

        assert ranking is None

    def test_ncaab_game_info(self):
        """Return test ncaab game info."""
        fields = {
            "date": "November 9, 2018",
            "location": "WVU Coliseum, Morgantown, West Virginia",
        }

        mock_field = """November 9, 2018

WVU Coliseum, Morgantown, West Virginia
Logos via Sports Logos.net / About logos
"""

        m = MockBoxscoreData(MockField(mock_field))

        for field, value in fields.items():
            result = self.boxscore._parse_game_date_and_location(field, m)
            assert value == result

    def test_ncaab_partial_game_info(self):
        """Return test ncaab partial game info."""
        fields = {"date": "November 9, 2018", "location": None}

        mock_field = """November 9, 2018

Logos via Sports Logos.net / About logos"""

        m = MockBoxscoreData(MockField(mock_field))

        for field, value in fields.items():
            result = self.boxscore._parse_game_date_and_location(field, m)
            assert value == result


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
<tr class="loser">
    <td><a href="/cbb/schools/south-dakota/2019.html">South Dakota</a></td>
    <td class="right"></td>
    <td class="right gamelink">
    </td>
</tr>
<tr class="loser">
    <td><a href="/cbb/schools/kansas/2019.html">Kansas</a>\
<span class='pollrank'>&nbsp;(1)&nbsp;</span></td>
    <td class="right"></td>
    <td class="right">&nbsp;
    </td>
</tr>
</tbody>
</table>""")
        games = self.boxscores._extract_game_info([mock_html])

        assert games == [
            {
                "home_name": "Kansas",
                "home_abbr": "kansas",
                "away_name": "South Dakota",
                "away_abbr": "south-dakota",
                "boxscore": "",
                "non_di": False,
                "top_25": True,
                "home_score": None,
                "home_rank": 1,
                "away_score": None,
                "away_rank": None,
                "winning_name": None,
                "winning_abbr": None,
                "losing_name": None,
                "losing_abbr": None,
            }
        ]
