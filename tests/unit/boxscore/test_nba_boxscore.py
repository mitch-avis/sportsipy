"""Provide utilities for test nba boxscore."""

from typing import Any
from unittest.mock import patch

from flexmock import flexmock
from pyquery import PyQuery

from sportsipy import utils
from sportsipy.constants import AWAY, HOME
from sportsipy.nba.boxscore import Boxscore, Boxscores


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


def mock_pyquery(url, timeout=None):
    """Return mock pyquery."""

    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 404
            self.html_contents = html_contents
            self.text = html_contents

    return MockPQ("")


class TestNBABoxscore:
    """Represent TestNBABoxscore."""

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

    def test_winning_name_is_home(self):
        """Return test winning name is home."""
        expected_name = "Home Name"

        self.boxscore._away_points = 70
        self.boxscore._home_points = 75
        self.boxscore._home_name = MockName(expected_name)

        assert self.boxscore.winning_name == expected_name

    def test_winning_name_is_away(self):
        """Return test winning name is away."""
        expected_name = "Away Name"

        self.boxscore._away_points = 75
        self.boxscore._home_points = 70
        self.boxscore._away_name = MockName(expected_name)

        assert self.boxscore.winning_name == expected_name

    def test_winning_abbr_is_home(self):
        """Return test winning abbr is home."""
        expected_name = "HOME"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_points = 70
        self.boxscore._home_points = 75
        self.boxscore._home_name = MockName(expected_name)

        assert self.boxscore.winning_abbr == expected_name

    def test_winning_abbr_is_away(self):
        """Return test winning abbr is away."""
        expected_name = "AWAY"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_points = 75
        self.boxscore._home_points = 70
        self.boxscore._away_name = MockName(expected_name)

        assert self.boxscore.winning_abbr == expected_name

    def test_losing_name_is_home(self):
        """Return test losing name is home."""
        expected_name = "Home Name"

        self.boxscore._away_points = 75
        self.boxscore._home_points = 70
        self.boxscore._home_name = MockName(expected_name)

        assert self.boxscore.losing_name == expected_name

    def test_losing_name_is_away(self):
        """Return test losing name is away."""
        expected_name = "Away Name"

        self.boxscore._away_points = 70
        self.boxscore._home_points = 75
        self.boxscore._away_name = MockName(expected_name)

        assert self.boxscore.losing_name == expected_name

    def test_losing_abbr_is_home(self):
        """Return test losing abbr is home."""
        expected_name = "HOME"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_points = 75
        self.boxscore._home_points = 70
        self.boxscore._home_name = MockName(expected_name)

        assert self.boxscore.losing_abbr == expected_name

    def test_losing_abbr_is_away(self):
        """Return test losing abbr is away."""
        expected_name = "AWAY"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_points = 70
        self.boxscore._home_points = 75
        self.boxscore._away_name = MockName(expected_name)

        assert self.boxscore.losing_abbr == expected_name

    def test_invalid_away_record_returns_default_wins(self):
        """Return test invalid away record returns default wins."""
        self.boxscore._away_record = "Golden State Warriors 1"

        assert self.boxscore.away_wins == 0

    def test_invalid_away_record_returns_default_losses(self):
        """Return test invalid away record returns default losses."""
        self.boxscore._away_record = "Golden State Warriors 1"

        assert self.boxscore.away_losses == 0

    def test_invalid_home_record_returns_default_wins(self):
        """Return test invalid home record returns default wins."""
        self.boxscore._home_record = "Golden State Warriors 1"

        assert self.boxscore.home_wins == 0

    def test_invalid_home_record_returns_default_losses(self):
        """Return test invalid home record returns default losses."""
        self.boxscore._home_record = "Golden State Warriors 1"

        assert self.boxscore.home_losses == 0

    def test_away_two_point_field_goals_calc(self):
        """Return test away two point field goals calc."""
        self.boxscore._away_field_goals = None
        self.boxscore._away_three_point_field_goals = None

        assert self.boxscore.away_two_point_field_goals is None

        self.boxscore._away_three_point_field_goals = 5
        assert self.boxscore.away_two_point_field_goals is None

        self.boxscore._away_field_goals = 5
        self.boxscore._away_three_point_field_goals = None

        assert self.boxscore.away_two_point_field_goals is None

        self.boxscore._away_field_goals = 5
        self.boxscore._away_three_point_field_goals = 5

        assert isinstance(self.boxscore.away_two_point_field_goals, int)

    def test_away_two_point_field_goal_attempts_calc(self):
        """Return test away two point field goal attempts calc."""
        self.boxscore._away_field_goal_attempts = None
        self.boxscore._away_three_point_field_goal_attempts = None

        assert self.boxscore.away_two_point_field_goal_attempts is None

        self.boxscore._away_three_point_field_goal_attempts = 5
        assert self.boxscore.away_two_point_field_goal_attempts is None

        self.boxscore._away_field_goal_attempts = 5
        self.boxscore._away_three_point_field_goal_attempts = None

        assert self.boxscore.away_two_point_field_goal_attempts is None

        self.boxscore._away_field_goal_attempts = 5
        self.boxscore._away_three_point_field_goal_attempts = 5

        assert isinstance(self.boxscore.away_two_point_field_goal_attempts, int)

    def test_away_two_point_field_goal_percentage_calc(self):
        """Return test away two point field goal percentage calc."""
        self.boxscore._away_field_goals = None
        self.boxscore._away_three_point_field_goals = None
        self.boxscore._away_field_goal_attempts = None
        self.boxscore._away_three_point_field_goal_attempts = None

        assert self.boxscore.away_two_point_field_goal_percentage is None

        self.boxscore._away_field_goal_attempts = 5
        self.boxscore._away_three_point_field_goal_attempts = None
        assert self.boxscore.away_two_point_field_goal_percentage is None

        self.boxscore._away_field_goals = 5
        self.boxscore._away_three_point_field_goals = None
        self.boxscore._away_field_goal_attempts = None
        self.boxscore._away_three_point_field_goal_attempts = None

        assert self.boxscore.away_two_point_field_goal_percentage is None

        self.boxscore._away_field_goals = 7
        self.boxscore._away_three_point_field_goals = 3
        self.boxscore._away_field_goal_attempts = 10
        self.boxscore._away_three_point_field_goal_attempts = 4

        assert isinstance(self.boxscore.away_two_point_field_goal_percentage, float)

    def test_home_to_point_field_goals_calc(self):
        """Return test home to point field goals calc."""
        self.boxscore._home_field_goals = None
        self.boxscore._home_three_point_field_goals = None

        assert self.boxscore.home_two_point_field_goals is None

        self.boxscore._home_three_point_field_goals = 5
        assert self.boxscore.home_two_point_field_goals is None

        self.boxscore._home_field_goals = 5
        self.boxscore._home_three_point_field_goals = None

        assert self.boxscore.home_two_point_field_goals is None

        self.boxscore._home_field_goals = 5
        self.boxscore._home_three_point_field_goals = 5

        assert isinstance(self.boxscore.home_two_point_field_goals, int)

    def test_home_two_point_field_goal_attempts_calc(self):
        """Return test home two point field goal attempts calc."""
        self.boxscore._home_field_goal_attempts = None
        self.boxscore._home_three_point_field_goal_attempts = None

        assert self.boxscore.home_two_point_field_goal_attempts is None

        self.boxscore._home_three_point_field_goal_attempts = 5
        assert self.boxscore.home_two_point_field_goal_attempts is None

        self.boxscore._home_field_goal_attempts = 5
        self.boxscore._home_three_point_field_goal_attempts = None

        assert self.boxscore.home_two_point_field_goal_attempts is None

        self.boxscore._home_field_goal_attempts = 5
        self.boxscore._home_three_point_field_goal_attempts = 5

        assert isinstance(self.boxscore.home_two_point_field_goal_attempts, int)

    def test_home_two_point_field_goal_percentage_calc(self):
        """Return test home two point field goal percentage calc."""
        self.boxscore._home_field_goals = None
        self.boxscore._home_three_point_field_goals = None
        self.boxscore._home_field_goal_attempts = None
        self.boxscore._home_three_point_field_goal_attempts = None

        assert self.boxscore.home_two_point_field_goal_percentage is None

        self.boxscore._home_field_goal_attempts = 5
        self.boxscore._home_three_point_field_goal_attempts = None
        assert self.boxscore.home_two_point_field_goal_percentage is None

        self.boxscore._home_field_goals = 5
        self.boxscore._home_three_point_field_goals = None
        self.boxscore._home_field_goal_attempts = None
        self.boxscore._home_three_point_field_goal_attempts = None

        assert self.boxscore.home_two_point_field_goal_percentage is None

        self.boxscore._home_field_goals = 7
        self.boxscore._home_three_point_field_goals = 3
        self.boxscore._home_field_goal_attempts = 10
        self.boxscore._home_three_point_field_goal_attempts = 4

        assert isinstance(self.boxscore.home_two_point_field_goal_percentage, float)

    def test_game_summary_with_no_scores_returns_none(self):
        """Return test game summary with no scores returns none."""
        result = Boxscore(None)._parse_summary(
            PyQuery("""<table id="line_score">

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

    def test_no_class_information_returns_dataframe_of_none(self):
        """Return test no class information returns dataframe of none."""
        self.boxscore._away_points = None
        self.boxscore._home_points = None

        assert self.boxscore.dataframe is None

    def test_nba_game_info(self):
        """Return test nba game info."""
        fields = {
            "date": "7:30 PM, November 9, 2018",
            "location": "State Farm Arena, Atlanta, Georgia",
        }

        mock_field = """7:30 PM, November 9, 2018

State Farm Arena, Atlanta, Georgia
Logos via Sports Logos.net / About logos
"""

        m = MockBoxscoreData(MockField(mock_field))

        for field, value in fields.items():
            result = self.boxscore._parse_game_date_and_location(field, m)
            assert value == result

    def test_nba_partial_game_info(self):
        """Return test nba partial game info."""
        fields = {"date": "7:30 PM, November 9, 2018", "location": None}

        mock_field = """7:30 PM, November 9, 2018

Logos via Sports Logos.net / About logos"""

        m = MockBoxscoreData(MockField(mock_field))

        for field, value in fields.items():
            result = self.boxscore._parse_game_date_and_location(field, m)
            assert value == result


class TestNBABoxscores:
    """Represent TestNBABoxscores."""

    @patch("requests.get", side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        """Return setup method."""
        flexmock(Boxscores).should_receive("_find_games").and_return(None)
        self.boxscores = Boxscores(None)

    def test_improper_loser_boxscore_format_skips_game(self):
        """Return test improper loser boxscore format skips game."""
        flexmock(Boxscores).should_receive("_get_team_details").and_return(
            (None, None, None, None, None, None)
        )
        mock_html = PyQuery("""<table class="teams">

<tbody>
    <tr class="loser">
            <td class="right">84</td>
            <td class="right gamelink">
            </td>
    </tr>
    <tr class="winner">
            <td><a href="/teams/IND/2017.html">Indiana</a></td>
            <td class="right">105</td>
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
    <tr class="loser">
            <td><a href="/teams/DET/2017.html">Detroit</a></td>
            <td class="right">84</td>
            <td class="right gamelink">
                    <a href="/boxscores/201702040IND.html">Final</a>
            </td>
    </tr>
    <tr class="winner">
            <td class="right">105</td>
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
    <tr class="loser">
            <td><a href="/teams/DET/2017.html">Detroit</a></td>
            <td class="right gamelink">
                    <a href="/boxscores/201702040IND.html">Final</a>
            </td>
    </tr>
    <tr class="loser">
            <td><a href="/teams/IND/2017.html">Indiana</a></td>
            <td class="right">&nbsp;
            </td>
    </tr>
    </tbody>
</table>""")
        games = self.boxscores._extract_game_info([mock_html])

        assert games == [
            {
                "home_name": "Indiana",
                "home_abbr": "IND",
                "away_name": "Detroit",
                "away_abbr": "DET",
                "boxscore": "201702040IND",
                "winning_name": None,
                "winning_abbr": None,
                "losing_name": None,
                "losing_abbr": None,
                "home_score": None,
                "away_score": None,
            }
        ]
