"""Provide utilities for test ncaab schedule."""

from datetime import datetime
from typing import Any, cast

from flexmock import flexmock
from pyquery import PyQuery

from sportsipy.constants import (
    AWAY,
    CONFERENCE_TOURNAMENT,
    HOME,
    LOSS,
    NEUTRAL,
    NON_DI,
    REGULAR_SEASON,
    WIN,
)
from sportsipy.ncaab.constants import (
    CBI_TOURNAMENT,
    CIT_TOURNAMENT,
    NCAA_TOURNAMENT,
    NIT_TOURNAMENT,
)
from sportsipy.ncaab.schedule import Game, Schedule


class TestNCAABSchedule:
    """Represent TestNCAABSchedule."""

    def setup_method(self, *args, **kwargs):
        """Return setup method."""
        flexmock(Game).should_receive("_parse_game_data").and_return(None)

        self.game: Any = Game(None)

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

    def test_regular_season_game_type(self):
        """Return test regular season game type."""
        self.game._type = "REG"

        assert self.game.type == REGULAR_SEASON

    def test_conference_tournament_game_type(self):
        """Return test conference tournament game type."""
        self.game._type = "CTOURN"

        assert self.game.type == CONFERENCE_TOURNAMENT

    def test_ncaa_tournament_game_type(self):
        """Return test ncaa tournament game type."""
        self.game._type = "NCAA"

        assert self.game.type == NCAA_TOURNAMENT

    def test_nit_tournament_game_type(self):
        """Return test nit tournament game type."""
        self.game._type = "NIT"

        assert self.game.type == NIT_TOURNAMENT

    def test_cbi_tournament_game_type(self):
        """Return test cbi tournament game type."""
        self.game._type = "CBI"

        assert self.game.type == CBI_TOURNAMENT

    def test_cit_tournament_game_type(self):
        """Return test cit tournament game type."""
        self.game._type = "CIT"

        assert self.game.type == CIT_TOURNAMENT

    def test_team_with_rank_returns_rank(self):
        """Return test team with rank returns rank."""
        self.game._opponent_name = "Purdue (3)"

        assert self.game.opponent_rank == 3

    def test_team_with_no_rank_returns_none(self):
        """Return test team with no rank returns none."""
        self.game._opponent_name = "Kansas State"

        assert self.game.opponent_rank is None

    def test_overtimes_returns_number_of_overtimes(self):
        """Return test overtimes returns number of overtimes."""
        self.game._overtimes = "OT"

        assert self.game.overtimes == 1

    def test_multiple_overtimes_returns_number_of_overtimes(self):
        """Return test multiple overtimes returns number of overtimes."""
        self.game._overtimes = "2OT"

        assert self.game.overtimes == 2

    def test_no_overtime_returns_zero(self):
        """Return test no overtime returns zero."""
        self.game._overtimes = ""

        assert self.game.overtimes == 0

    def test_bad_overtime_defaults_to_zero(self):
        """Return test bad overtime defaults to zero."""
        self.game._overtimes = "BAD"

        assert self.game.overtimes == 0

    def test_none_time_defaults_to_set_time_in_datetime(self):
        """Return test none time defaults to set time in datetime."""
        self.game._date = "Thu, Dec 13, 2018"
        self.game._time = None

        assert self.game.datetime == datetime(2018, 12, 13, 0, 0)

    def test_blank_time_defaults_to_set_time_in_datetime(self):
        """Return test blank time defaults to set time in datetime."""
        self.game._date = "Thu, Dec 13, 2018"
        self.game._time = ""

        assert self.game.datetime == datetime(2018, 12, 13, 0, 0)

    def test_empty_schedule_class_returns_dataframe_of_none(self):
        """Return test empty schedule class returns dataframe of none."""
        self.game._home_points = None
        self.game._away_points = None

        assert self.game._home_points is None
        assert self.game._away_points is None
        assert self.game.dataframe is None

    def test_empty_schedule_class_returns_dataframe_extended_of_none(self):
        """Return test empty schedule class returns dataframe extended of none."""
        self.game._home_points = None
        self.game._away_points = None

        assert self.game._home_points is None
        assert self.game._away_points is None
        assert self.game.dataframe_extended is None

    def test_no_dataframes_returns_none(self):
        """Return test no dataframes returns none."""
        flexmock(Schedule).should_receive("_pull_schedule").and_return(None)
        schedule = Schedule("PURDUE")

        fake_game = cast(Game, flexmock(dataframe=None))
        schedule._games = [fake_game]

        assert schedule.dataframe is None

    def test_no_dataframes_extended_returns_none(self):
        """Return test no dataframes extended returns none."""
        flexmock(Schedule).should_receive("_pull_schedule").and_return(None)
        schedule = Schedule("PURDUE")

        fake_game = cast(Game, flexmock(dataframe_extended=None))
        schedule._games = [fake_game]

        assert schedule.dataframe_extended is None


class TestNCAABScheduleNames:
    """Represent TestNCAABScheduleNames."""

    def test_non_major_school_returns_name_for_abbreviation(self):
        """Return test non major school returns name for abbreviation."""
        text = '<td class="left " data-stat="opp_name">City College of New York</td>'
        game_data = PyQuery(text)

        game = Game(game_data)

        assert game.opponent_abbr == "City College of New York"

    def test_non_major_school_returns_non_d1_for_conference(self):
        """Return test non major school returns non d1 for conference."""
        game_data = PyQuery('<td class="left " data-stat="conf_abbr"></td>')

        game = Game(game_data)

        assert game.opponent_conference == NON_DI
