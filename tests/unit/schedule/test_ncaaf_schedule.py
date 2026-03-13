"""Provide utilities for test ncaaf schedule."""

from datetime import datetime

from flexmock import flexmock
from pyquery import PyQuery

from sportsipy import utils
from sportsipy.constants import AWAY, HOME, LOSS, NEUTRAL, NON_DI, WIN
from sportsipy.ncaaf.schedule import Game, Schedule


class TestNCAAFSchedule:
    """Represent TestNCAAFSchedule."""

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

    def test_neutral_game_returns_neutral_location(self):
        """Return test neutral game returns neutral location."""
        self.game._location = "N"

        assert self.game.location == NEUTRAL

    def test_winning_result_returns_win(self):
        """Return test winning result returns win."""
        self.game._result = "W"

        assert self.game.result == WIN

    def test_losing_result_returns_loss(self):
        """Return test losing result returns loss."""
        self.game._result = "L"

        assert self.game.result == LOSS

    def test_team_with_rank_returns_rank(self):
        """Return test team with rank returns rank."""
        self.game._rank = "(1) Alabama"

        assert self.game.rank == 1

    def test_team_with_no_rank_returns_none(self):
        """Return test team with no rank returns none."""
        self.game._rank = "Missouri"

        assert self.game.rank is None

    def test_opponent_with_rank_returns_rank(self):
        """Return test opponent with rank returns rank."""
        self.game._opponent_name = "(1) Alabama"

        assert self.game.opponent_rank == 1

    def test_opponent_with_no_rank_returns_none(self):
        """Return test opponent with no rank returns none."""
        self.game._opponent_name = "Missouri"

        assert self.game.opponent_rank is None

    def test_datetime_with_no_time(self):
        """Return test datetime with no time."""
        self.game._date = "Aug 31, 2017"
        self.game._time = ""

        assert self.game.datetime == datetime(2017, 8, 31)

    def test_empty_game_class_returns_dataframe_of_none(self):
        """Return test empty game class returns dataframe of none."""
        assert self.game._points_for is None
        assert self.game._points_against is None
        assert self.game.dataframe is None

    def test_no_dataframes_returns_none(self):
        """Return test no dataframes returns none."""
        flexmock(Schedule).should_receive("_pull_schedule").and_return(None)
        schedule = Schedule("PURDUE")

        fake_game = flexmock(dataframe=None)
        schedule._games = [fake_game]

        assert schedule.dataframe is None

    def test_no_dataframes_extended_returns_none(self):
        """Return test no dataframes extended returns none."""
        flexmock(Schedule).should_receive("_pull_schedule").and_return(None)
        schedule = Schedule("PURDUE")

        fake_game = flexmock(dataframe_extended=None)
        schedule._games = [fake_game]

        assert schedule.dataframe_extended is None


class TestNCAAFScheduleNames:
    """Represent TestNCAAFScheduleNames."""

    def test_non_major_school_returns_name_for_abbreviation(self):
        """Return test non major school returns name for abbreviation."""
        text = '<td class="left " data-stat="opp_name">Citadel</td>'
        game_data = PyQuery(text)

        flexmock(utils).should_receive("parse_field").and_return(None)

        game = Game(game_data)

        assert game.opponent_abbr == "Citadel"

    def test_non_major_school_returns_non_d1_for_conference(self):
        """Return test non major school returns non d1 for conference."""
        text = '<td class="left " data-stat="conf_abbr">Non-Major</td>'
        game_data = PyQuery(text)

        game = Game(game_data)

        assert game.opponent_conference == NON_DI
