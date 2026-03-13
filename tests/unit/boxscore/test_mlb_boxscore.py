"""Provide utilities for test mlb boxscore."""

from typing import Any
from unittest.mock import patch

from flexmock import flexmock
from pyquery import PyQuery

from sportsipy import utils
from sportsipy.constants import AWAY, HOME
from sportsipy.mlb.boxscore import Boxscore, Boxscores
from sportsipy.mlb.constants import DAY, NIGHT


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
            self.url = url
            self.reason = "404"
            self.headers = None

    return MockPQ(None)


class TestMLBBoxscore:
    """Represent TestMLBBoxscore."""

    @patch("requests.get", side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        """Return setup method."""
        flexmock(Boxscore).should_receive("_parse_game_data").and_return(None)

        self.boxscore: Any = Boxscore(None)

    def test_away_team_wins(self):
        """Return test away team wins."""
        self.boxscore._away_runs = 6
        self.boxscore._home_runs = 3

        assert self.boxscore.winner == AWAY

    def test_home_team_wins(self):
        """Return test home team wins."""
        self.boxscore._away_runs = 3
        self.boxscore._home_runs = 6

        assert self.boxscore.winner == HOME

    def test_winning_name_is_home(self):
        """Return test winning name is home."""
        expected_name = "Home Name"

        self.boxscore._away_runs = 3
        self.boxscore._home_runs = 6
        self.boxscore._home_name = MockName(expected_name)

        assert self.boxscore.winning_name == expected_name

    def test_winning_name_is_away(self):
        """Return test winning name is away."""
        expected_name = "Away Name"

        self.boxscore._away_runs = 6
        self.boxscore._home_runs = 3
        self.boxscore._away_name = MockName(expected_name)

        assert self.boxscore.winning_name == expected_name

    def test_winning_abbr_is_home(self):
        """Return test winning abbr is home."""
        expected_name = "HOME"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_runs = 3
        self.boxscore._home_runs = 6
        self.boxscore._home_name = MockName(expected_name)

        assert self.boxscore.winning_abbr == expected_name

    def test_winning_abbr_is_away(self):
        """Return test winning abbr is away."""
        expected_name = "AWAY"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_runs = 6
        self.boxscore._home_runs = 3
        self.boxscore._away_name = MockName(expected_name)

        assert self.boxscore.winning_abbr == expected_name

    def test_losing_name_is_home(self):
        """Return test losing name is home."""
        expected_name = "Home Name"

        self.boxscore._away_runs = 6
        self.boxscore._home_runs = 3
        self.boxscore._home_name = MockName(expected_name)

        assert self.boxscore.losing_name == expected_name

    def test_losing_name_is_away(self):
        """Return test losing name is away."""
        expected_name = "Away Name"

        self.boxscore._away_runs = 3
        self.boxscore._home_runs = 6
        self.boxscore._away_name = MockName(expected_name)

        assert self.boxscore.losing_name == expected_name

    def test_losing_abbr_is_home(self):
        """Return test losing abbr is home."""
        expected_name = "HOME"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_runs = 6
        self.boxscore._home_runs = 3
        self.boxscore._home_name = MockName(expected_name)

        assert self.boxscore.losing_abbr == expected_name

    def test_losing_abbr_is_away(self):
        """Return test losing abbr is away."""
        expected_name = "AWAY"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_runs = 3
        self.boxscore._home_runs = 6
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
            <td class="center"></td>
            <td class="center"></td>
        </tr>
        <tr>
            <td class="center"></td>
            <td class="center"></td>
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

    def test_mlb_game_info(self):
        """Return test mlb game info."""
        fields = {
            "attendance": 26340,
            "date": "Monday, July 9, 2018",
            "time": "4:05 p.m. ET",
            "venue": "Oriole Park at Camden Yards",
            "duration": "2:55",
            "time_of_day": "Night",
        }

        mock_field = """Monday, July 9, 2018

Start Time: 4:05 p.m. ET
Attendance: 26,340
Venue: Oriole Park at Camden Yards
Game Duration: 2:55
Night Game, on grass
"""

        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_mlb_first_game_double_header_info(self):
        """Return test mlb first game double header info."""
        fields = {
            "attendance": None,
            "date": "Monday, July 9, 2018",
            "time": "4:05 p.m. ET",
            "venue": "Oriole Park at Camden Yards",
            "duration": "2:55",
            "time_of_day": "Night",
        }

        mock_field = """Monday, July 9, 2018

Start Time: 4:05 p.m. ET
Venue: Oriole Park at Camden Yards
Game Duration: 2:55
Night Game, on grass
First game of doubleheader
"""

        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_mlb_second_game_double_header_info(self):
        """Return test mlb second game double header info."""
        fields = {
            "attendance": 26340,
            "date": "Monday, July 9, 2018",
            "duration": "3:13",
            "time_of_day": "Night",
            "venue": "Oriole Park at Camden Yards",
        }

        mock_field = """Monday, July 9, 2018

Attendance: 26,340
Venue: Oriole Park at Camden Yards
Game Duration: 3:13
Night Game, on grass
Second game of doubleheader
"""

        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_mlb_limited_game_info(self):
        """Return test mlb limited game info."""
        fields = {
            "attendance": 19043,
            "date": "Sunday, June 28, 1970",
            "time": None,
            "venue": "Robert F. Kennedy Stadium",
            "duration": "3:43",
            "time_of_day": "Day",
        }

        mock_field = """Sunday, June 28, 1970

Attendance: 19,043
Venue: Robert F. Kennedy Stadium
Game Duration: 3:43
Day Game, on grass
"""

        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_invalid_away_inherited_runners_returns_default(self):
        """Return test invalid away inherited runners returns default."""
        self.boxscore._away_inherited_runners = ""

        assert self.boxscore.away_inherited_runners is None

    def test_invalid_away_inherited_score_returns_default(self):
        """Return test invalid away inherited score returns default."""
        self.boxscore._away_inherited_score = ""

        assert self.boxscore.away_inherited_score is None

    def test_invalid_home_inherited_runners_returns_default(self):
        """Return test invalid home inherited runners returns default."""
        self.boxscore._home_inherited_runners = ""

        assert self.boxscore.home_inherited_runners is None

    def test_invalid_home_inherited_score_returns_default(self):
        """Return test invalid home inherited score returns default."""
        self.boxscore._home_inherited_score = ""

        assert self.boxscore.home_inherited_score is None

    def test_no_class_information_returns_dataframe_of_none(self):
        """Return test no class information returns dataframe of none."""
        self.boxscore._away_runs = None
        self.boxscore._home_runs = None

        assert self.boxscore.dataframe is None

    def test_attendance_with_empty_string(self):
        """Return test attendance with empty string."""
        self.boxscore._attendance = ""

        assert self.boxscore.attendance is None

    def test_night_game_returns_night(self):
        """Return test night game returns night."""
        self.boxscore._time_of_day = "night game on grass"

        assert self.boxscore.time_of_day == NIGHT

    def test_day_game_returns_night(self):
        """Return test day game returns night."""
        self.boxscore._time_of_day = "day game on grass"

        assert self.boxscore.time_of_day == DAY


class TestMLBBoxscores:
    """Represent TestMLBBoxscores."""

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
    <td class="right">1</td>
    <td class="right gamelink">
    </td>
</tr>
<tr class="winner">
    <td><a href="/teams/BAL/2017.shtml">Baltimore Orioles</a></td>
    <td class="right">3</td>
    <td class="right">
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
    <td><a href="/teams/TEX/2017.shtml">Texas Rangers</a></td>
    <td class="right">1</td>
    <td class="right gamelink">
        <a href="/boxes/BAL/BAL201707170.shtml">Final</a>
    </td>
</tr>
<tr class="winner">
    <td class="right">3</td>
    <td class="right">
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
    <td><a href="/teams/TEX/2017.shtml">Texas Rangers</a></td>
    <td class="right gamelink">
        <a href="/boxes/BAL/BAL201707170.shtml">Final</a>
    </td>
</tr>
<tr class="loser">
    <td><a href="/teams/BAL/2017.shtml">Baltimore Orioles</a></td>
    <td class="right">
    </td>
</tr>
</tbody>
</table>""")
        games = self.boxscores._extract_game_info([mock_html])

        assert games == [
            {
                "away_abbr": "TEX",
                "away_name": "Texas Rangers",
                "away_score": None,
                "boxscore": "BAL/BAL201707170",
                "home_abbr": "BAL",
                "home_name": "Baltimore Orioles",
                "home_score": None,
                "losing_abbr": None,
                "losing_name": None,
                "winning_abbr": None,
                "winning_name": None,
            }
        ]
