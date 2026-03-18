"""Provide utilities for test nba schedule."""

from flexmock import flexmock

from sportsipy.constants import AWAY, HOME, LOSS, WIN
from sportsipy.nba.schedule import Game, Schedule


class TestNBASchedule:
    """Represent TestNBASchedule."""

    def setup_method(self, *args, **kwargs):
        """Return setup method."""
        flexmock(Game).should_receive("_parse_game_data").and_return(None)

        self.game = Game(None)

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

    def test_empty_game_class_returns_dataframe_of_none(self):
        """Return test empty game class returns dataframe of none."""
        assert self.game._points_allowed is None
        assert self.game._points_scored is None
        assert self.game.dataframe is None

    def test_no_dataframes_returns_none(self):
        """Return test no dataframes returns none."""
        flexmock(Schedule).should_receive("_pull_schedule").and_return(None)
        schedule = Schedule("DET")

        fake_game = Game(None)
        schedule._games = [fake_game]

        assert schedule.dataframe is None

    def test_no_dataframes_extended_returns_none(self):
        """Return test no dataframes extended returns none."""
        flexmock(Schedule).should_receive("_pull_schedule").and_return(None)
        schedule = Schedule("DET")

        fake_game = Game(None)
        schedule._games = [fake_game]

        assert schedule.dataframe_extended is None
