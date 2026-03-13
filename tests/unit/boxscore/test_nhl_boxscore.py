"""Provide utilities for test nhl boxscore."""

from typing import Any
from unittest.mock import patch

from flexmock import flexmock
from pyquery import PyQuery

from sportsipy import utils
from sportsipy.constants import AWAY, HOME
from sportsipy.nhl.boxscore import Boxscore, Boxscores


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

    def text(self):
        """Return text."""
        return self._name


def mock_pyquery(url, timeout=None):
    """Return mock pyquery."""

    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 404
            self.html_contents = html_contents
            self.text = html_contents

    return MockPQ("")


class TestNHLBoxscore:
    """Represent TestNHLBoxscore."""

    @patch("requests.get", side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        """Return setup method."""
        flexmock(Boxscore).should_receive("_parse_game_data").and_return(None)

        self.boxscore: Any = Boxscore(None)

    def test_away_team_wins(self):
        """Return test away team wins."""
        self.boxscore._away_goals = 4
        self.boxscore._home_goals = 3

        assert self.boxscore.winner == AWAY

    def test_home_team_wins(self):
        """Return test home team wins."""
        self.boxscore._away_goals = 3
        self.boxscore._home_goals = 4

        assert self.boxscore.winner == HOME

    def test_winning_name_is_home(self):
        """Return test winning name is home."""
        expected_name = "Home Name"

        self.boxscore._away_goals = 3
        self.boxscore._home_goals = 4
        self.boxscore._home_name = MockName(expected_name)

        assert self.boxscore.winning_name == expected_name

    def test_winning_name_is_away(self):
        """Return test winning name is away."""
        expected_name = "Away Name"

        self.boxscore._away_goals = 4
        self.boxscore._home_goals = 3
        self.boxscore._away_name = MockName(expected_name)

        assert self.boxscore.winning_name == expected_name

    def test_winning_abbr_is_home(self):
        """Return test winning abbr is home."""
        expected_name = "HOME"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_goals = 3
        self.boxscore._home_goals = 4
        self.boxscore._home_name = MockName(expected_name)

        assert self.boxscore.winning_abbr == expected_name

    def test_winning_abbr_is_away(self):
        """Return test winning abbr is away."""
        expected_name = "AWAY"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_goals = 4
        self.boxscore._home_goals = 3
        self.boxscore._away_name = MockName(expected_name)

        assert self.boxscore.winning_abbr == expected_name

    def test_losing_name_is_home(self):
        """Return test losing name is home."""
        expected_name = "Home Name"

        self.boxscore._away_goals = 4
        self.boxscore._home_goals = 3
        self.boxscore._home_name = MockName(expected_name)

        assert self.boxscore.losing_name == expected_name

    def test_losing_name_is_away(self):
        """Return test losing name is away."""
        expected_name = "Away Name"

        self.boxscore._away_goals = 3
        self.boxscore._home_goals = 4
        self.boxscore._away_name = MockName(expected_name)

        assert self.boxscore.losing_name == expected_name

    def test_losing_abbr_is_home(self):
        """Return test losing abbr is home."""
        expected_name = "HOME"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_goals = 4
        self.boxscore._home_goals = 3
        self.boxscore._home_name = MockName(expected_name)

        assert self.boxscore.losing_abbr == expected_name

    def test_losing_abbr_is_away(self):
        """Return test losing abbr is away."""
        expected_name = "AWAY"

        flexmock(utils).should_receive("parse_abbreviation").and_return(expected_name)

        self.boxscore._away_goals = 3
        self.boxscore._home_goals = 4
        self.boxscore._away_name = MockName(expected_name)

        assert self.boxscore.losing_abbr == expected_name

    def test_invalid_away_game_winning_goals_returns_default(self):
        """Return test invalid away game winning goals returns default."""
        goals = ["0", "1", "bad"]

        self.boxscore._away_game_winning_goals = goals
        self.boxscore._away_skaters = 3
        self.boxscore._away_goalies = 0

        assert self.boxscore.away_game_winning_goals == 1

    def test_invalid_away_even_strength_assists_returns_default(self):
        """Return test invalid away even strength assists returns default."""
        assists = ["0", "1", "bad"]

        self.boxscore._away_even_strength_assists = assists
        self.boxscore._away_skaters = 3
        self.boxscore._away_goalies = 0

        assert self.boxscore.away_even_strength_assists == 1

    def test_invalid_home_even_strength_assists_returns_default(self):
        """Return test invalid home even strength assists returns default."""
        assists = ["0", "1", "bad"]

        self.boxscore._home_even_strength_assists = assists
        self.boxscore._away_skaters = 0
        self.boxscore._away_goalies = 0

        assert self.boxscore.home_even_strength_assists == 1

    def test_invalid_away_power_play_assists_returns_default(self):
        """Return test invalid away power play assists returns default."""
        assists = ["0", "1", "bad"]

        self.boxscore._away_power_play_assists = assists
        self.boxscore._away_skaters = 3
        self.boxscore._away_goalies = 0

        assert self.boxscore.away_power_play_assists == 1

    def test_invalid_home_power_play_assits_returns_default(self):
        """Return test invalid home power play assits returns default."""
        assists = ["0", "1", "bad"]

        self.boxscore._home_power_play_assists = assists
        self.boxscore._away_skaters = 0
        self.boxscore._away_goalies = 0

        assert self.boxscore.home_power_play_assists == 1

    def test_invalid_away_short_handed_assists_returns_default(self):
        """Return test invalid away short handed assists returns default."""
        assists = ["0", "1", "bad"]

        self.boxscore._away_short_handed_assists = assists
        self.boxscore._away_skaters = 3
        self.boxscore._away_goalies = 0

        assert self.boxscore.away_short_handed_assists == 1

    def test_invalid_home_short_handed_assits_returns_default(self):
        """Return test invalid home short handed assits returns default."""
        assists = ["0", "1", "bad"]

        self.boxscore._home_short_handed_assists = assists
        self.boxscore._away_skaters = 0
        self.boxscore._away_goalies = 0

        assert self.boxscore.home_short_handed_assists == 1

    @patch("requests.get", side_effect=mock_pyquery)
    def test_invalid_url_returns_none(self, *args, **kwargs):
        """Return test invalid url returns none."""
        result = Boxscore(None)._retrieve_html_page("")

        assert result is None

    def test_regular_season_information(self):
        """Return test regular season information."""
        fields = {
            "date": "October 5, 2017",
            "playoff_round": None,
            "time": "7:00 PM",
            "attendance": 17565,
            "arena": "TD Garden",
            "duration": "2:39",
        }

        mock_field = """October 5, 2017, 7:00 PM

Attendance: 17,565
Arena: TD Garden
Game Duration: 2:39
Logos via Sports Logos.net / About logos
"""

        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_playoffs_information(self):
        """Return test playoffs information."""
        fields = {
            "date": "June 7, 2018",
            "playoff_round": "Stanley Cup Final",
            "time": "8:00 PM",
            "attendance": 18529,
            "arena": "T-Mobile Arena",
            "duration": "2:45",
        }

        mock_field = """June 7, 2018, 8:00 PM

Stanley Cup Final
Attendance: 18,529
Arena: T-Mobile Arena
Game Duration: 2:45
Logos via Sports Logos.net / About logos
"""

        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_no_game_information(self):
        """Return test no game information."""
        fields = {
            "date": "",
            "playoff_round": None,
            "time": None,
            "attendance": None,
            "arena": None,
            "duration": None,
        }

        mock_field = "\n"

        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_limited_game_information(self):
        """Return test limited game information."""
        fields = {
            "date": "June 7, 2018",
            "playoff_round": "Stanley Cup Final",
            "time": None,
            "attendance": None,
            "arena": "T-Mobile Arena",
            "duration": None,
        }

        mock_field = """June 7, 2018

Stanley Cup Final
Arena: T-Mobile Arena
Logos via Sports Logos.net / About logos
"""

        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_away_shutout_single_goalies(self):
        """Return test away shutout single goalies."""
        shutout = ["1", "0"]

        self.boxscore._away_shutout = shutout
        self.boxscore._away_goalies = 1

        assert self.boxscore.away_shutout == 1

    def test_away_shutout_multiple_goalies(self):
        """Return test away shutout multiple goalies."""
        shutout = ["0", "1", "0"]

        self.boxscore._away_shutout = shutout
        self.boxscore._away_goalies = 2

        assert self.boxscore.away_shutout == 1

    def test_away_shutout_multiple_goalies_empty_field(self):
        """Return test away shutout multiple goalies empty field."""
        shutout = ["", "1", "0"]

        self.boxscore._away_shutout = shutout
        self.boxscore._away_goalies = 2

        assert self.boxscore.away_shutout == 1

    def test_home_shutout_single_goalies(self):
        """Return test home shutout single goalies."""
        shutout = ["0", "1"]

        self.boxscore._home_shutout = shutout
        self.boxscore._away_goalies = 1

        assert self.boxscore.home_shutout == 1

    def test_home_shutout_multiple_goalies(self):
        """Return test home shutout multiple goalies."""
        shutout = ["0", "0", "1"]

        self.boxscore._home_shutout = shutout
        self.boxscore._away_goalies = 1

        assert self.boxscore.home_shutout == 1

    def test_home_shutout_multiple_goalies_empty_field(self):
        """Return test home shutout multiple goalies empty field."""
        shutout = ["0", "", "1"]

        self.boxscore._home_shutout = shutout
        self.boxscore._away_goalies = 1

        assert self.boxscore.home_shutout == 1

    def test_away_saves_single_goalies(self):
        """Return test away saves single goalies."""
        saves = ["29", "30"]

        self.boxscore._away_saves = saves
        self.boxscore._away_goalies = 1

        assert self.boxscore.away_saves == 29

    def test_away_saves_multiple_goalies(self):
        """Return test away saves multiple goalies."""
        saves = ["29", "3", "30"]

        self.boxscore._away_saves = saves
        self.boxscore._away_goalies = 2

        assert self.boxscore.away_saves == 32

    def test_away_saves_multiple_goalies_empty_field(self):
        """Return test away saves multiple goalies empty field."""
        saves = ["29", "", "30"]

        self.boxscore._away_saves = saves
        self.boxscore._away_goalies = 2

        assert self.boxscore.away_saves == 29

    def test_home_saves_single_goalies(self):
        """Return test home saves single goalies."""
        saves = ["29", "30"]

        self.boxscore._home_saves = saves
        self.boxscore._away_goalies = 1

        assert self.boxscore.home_saves == 30

    def test_home_saves_multiple_goalies(self):
        """Return test home saves multiple goalies."""
        saves = ["29", "3", "30"]

        self.boxscore._home_saves = saves
        self.boxscore._away_goalies = 1

        assert self.boxscore.home_saves == 33

    def test_home_saves_multiple_goalies_empty_field(self):
        """Return test home saves multiple goalies empty field."""
        saves = ["29", "30", ""]

        self.boxscore._home_saves = saves
        self.boxscore._away_goalies = 1

        assert self.boxscore.home_saves == 30

    def test_away_save_percentage(self):
        """Return test away save percentage."""
        self.boxscore._away_saves = ["30", "0"]
        self.boxscore._away_goalies = 1
        self.boxscore._home_shots_on_goal = 33

        assert self.boxscore.away_save_percentage == 0.909

    def test_away_save_percentage_zero_shots(self):
        """Return test away save percentage zero shots."""
        self.boxscore._away_saves = ["0", "0"]
        self.boxscore._away_goalies = 1
        self.boxscore._home_shots_on_goal = 0

        assert self.boxscore.away_save_percentage == 0.0

    def test_home_save_percentage(self):
        """Return test home save percentage."""
        self.boxscore._home_saves = ["0", "30"]
        self.boxscore._away_goalies = 1
        self.boxscore._away_shots_on_goal = 33

        assert self.boxscore.home_save_percentage == 0.909

    def test_home_save_percentage_zero_shots(self):
        """Return test home save percentage zero shots."""
        self.boxscore._home_saves = ["0", "0"]
        self.boxscore._away_goalies = 1
        self.boxscore._away_shots_on_goal = 0

        assert self.boxscore.home_save_percentage == 0.0

    def test_no_class_information_returns_dataframe_of_none(self):
        """Return test no class information returns dataframe of none."""
        self.boxscore._away_goals = None
        self.boxscore._home_goals = None

        assert self.boxscore.dataframe is None

    def test_no_players_during_extraction(self):
        """Return test no players during extraction."""
        table = PyQuery("<tbody><tr></tr><tr></tr></tbody>")
        player_dict = self.boxscore._extract_player_stats(table, {}, "Home")

        assert not player_dict


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
    <td><a href="/teams/DET/2019.html">Detroit Red Wings</a></td>
    <td class="right">3</td>
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
    <td><a href="/teams/LAK/2019.html">Los Angeles Kings</a></td>
    <td class="right">1</td>
    <td class="right gamelink">
        <a href="/boxscores/201812100DET.html">Final</a>
    </td>
</tr>
<tr class="winner">
    <td class="right">3</td>
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
    <td><a href="/teams/LAK/2019.html">Los Angeles Kings</a></td>
    <td class="right gamelink">
        <a href="/boxscores/201812100DET.html">Final</a>
    </td>
</tr>
<tr class="loser">
    <td><a href="/teams/DET/2019.html">Detroit Red Wings</a></td>
    <td class="right">&nbsp;
    </td>
</tr>
</tbody>
</table>""")
        games = self.boxscores._extract_game_info([mock_html])

        assert games == [
            {
                "away_abbr": "LAK",
                "away_name": "Los Angeles Kings",
                "away_score": None,
                "boxscore": "201812100DET",
                "home_abbr": "DET",
                "home_name": "Detroit Red Wings",
                "home_score": None,
                "losing_abbr": None,
                "losing_name": None,
                "winning_abbr": None,
                "winning_name": None,
            }
        ]
