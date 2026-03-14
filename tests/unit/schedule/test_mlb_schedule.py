"""Provide utilities for test mlb schedule."""

from datetime import datetime
from typing import Any, cast

from flexmock import flexmock

from sportsipy.constants import AWAY, HOME, LOSS, WIN
from sportsipy.mlb.constants import DAY, NIGHT
from sportsipy.mlb.schedule import Game, Schedule


class TestMLBSchedule:
    """Represent TestMLBSchedule."""

    def setup_method(self, *args, **kwargs):
        """Return setup method."""
        flexmock(Game).should_receive("_parse_game_data").and_return(None)

        self.game: Any = Game(None, None)

    def test_double_header_returns_second_game(self):
        """Return test double header returns second game."""
        self.game._date = "Sunday, May 14 (2)"
        self.game._year = "2017"

        assert self.game.datetime == datetime(2017, 5, 14)
        assert self.game.game_number_for_day == 2

    def test_away_game_returns_away_location(self):
        """Return test away game returns away location."""
        self.game._location = "@"

        assert self.game.location == AWAY

    def test_home_game_returns_home_location(self):
        """Return test home game returns home location."""
        self.game._location = ""

        assert self.game.location == HOME

    def test_winning_result_returns_win(self):
        """Return test winning result returns win."""
        self.game._result = "W"

        assert self.game.result == WIN

    def test_losing_result_returns_loss(self):
        """Return test losing result returns loss."""
        self.game._result = "L"

        assert self.game.result == LOSS

    def test_regular_length_game_returns_9_innings(self):
        """Return test regular length game returns 9 innings."""
        self.game._innings = ""

        assert self.game.innings == 9

    def test_extra_innings_returns_total_innings(self):
        """Return test extra innings returns total innings."""
        self.game._innings = "12"

        assert self.game.innings == 12

    def test_games_behind_returns_zero_when_tied(self):
        """Return test games behind returns zero when tied."""
        self.game._games_behind = "Tied"

        assert self.game.games_behind == 0.0

    def test_games_behind_returns_number_of_games_behind(self):
        """Return test games behind returns number of games behind."""
        self.game._games_behind = "1.5"

        assert self.game.games_behind == 1.5

    def test_games_behind_returns_number_of_games_ahead(self):
        """Return test games behind returns number of games ahead."""
        self.game._games_behind = "up 1.5"

        assert self.game.games_behind == -1.5

        self.game._games_behind = "up13.0"

        assert self.game.games_behind == -13.0

    def test_no_save_returns_none(self):
        """Return test no save returns none."""
        self.game._save = ""

        assert self.game.save is None

    def test_save_returns_name(self):
        """Return test save returns name."""
        self.game._save = "Verlander"

        assert self.game.save == "Verlander"

    def test_day_game_returns_daytime(self):
        """Return test day game returns daytime."""
        self.game._day_or_night = "D"

        assert self.game.day_or_night == DAY

    def test_night_game_returns_nighttime(self):
        """Return test night game returns nighttime."""
        self.game._day_or_night = "N"

        assert self.game.day_or_night == NIGHT

    def test_empty_game_class_returns_dataframe_of_none(self):
        """Return test empty game class returns dataframe of none."""
        assert self.game.runs_allowed is None
        assert self.game.runs_scored is None
        assert self.game.dataframe is None

    def test_empty_boxscore_class_returns_dataframe_of_none(self):
        """Return test empty boxscore class returns dataframe of none."""
        assert self.game.runs_allowed is None
        assert self.game.runs_scored is None
        assert self.game.dataframe_extended is None

    def test_invalid_dataframe_not_included_with_schedule_dataframes(self):
        """Return test invalid dataframe not included with schedule dataframes."""
        # If a DataFrame is not valid, it should not be included with the
        # dataframes property. If no dataframes are present, the DataFrame
        # should return the default value of None.
        flexmock(Schedule).should_receive("_pull_schedule").and_return(None)
        schedule = Schedule("HOU")

        fake_game = cast(Game, flexmock(runs_scored=None, runs_allowed=None, dataframe=None))
        schedule._games = [fake_game]

        assert schedule.dataframe is None

    def test_no_dataframes_extended_returns_none(self):
        """Return test no dataframes extended returns none."""
        flexmock(Schedule).should_receive("_pull_schedule").and_return(None)
        schedule = Schedule("HOU")

        fake_game = cast(Game, flexmock(dataframe_extended=None))
        schedule._games = [fake_game]

        assert schedule.dataframe_extended is None

    def test_bad_games_up_returns_default(self):
        """Return test bad games up returns default."""
        self.game._games_behind = "up BAD"

        assert self.game.games_behind is None

    def test_bad_games_ahead_returns_default(self):
        """Return test bad games ahead returns default."""
        self.game._games_behind = "BAD"

        assert self.game.games_behind is None
