from typing import Any

from flexmock import flexmock

from sportsipy.constants import AWAY, HOME, LOSS, WIN
from sportsipy.nhl.constants import OVERTIME_LOSS, SHOOTOUT
from sportsipy.nhl.schedule import Game, Schedule

YEAR = 2017


class TestNHLSchedule:
    def setup_method(self, *args, **kwargs):
        flexmock(Game).should_receive("_parse_game_data").and_return(None)

        self.game: Any = Game(None)

    def test_away_game_returns_away_location(self):
        self.game._location = "@"

        assert self.game.location == AWAY

    def test_home_game_returns_home_location(self):
        self.game._location = ""

        assert self.game.location == HOME

    def test_winning_result_returns_win(self):
        self.game._result = "W"

        assert self.game.result == WIN

    def test_losing_result_in_overtime_returns_overtime_loss(self):
        self.game._result = "L"
        self.game._overtime = "OT"

        assert self.game.result == OVERTIME_LOSS

    def test_losing_result_in_regulation_returns_loss(self):
        self.game._result = "L"
        self.game._overtime = ""

        assert self.game.result == LOSS

    def test_overtime_returns_one(self):
        self.game._overtime = "OT"

        assert self.game.overtime == 1

    def test_no_overtime_returns_zero(self):
        self.game._overtime = ""

        assert self.game.overtime == 0

    def test_double_overtime_returns_two(self):
        self.game._overtime = "2OT"

        assert self.game.overtime == 2

    def test_shootout_returns_shootout_constant(self):
        self.game._overtime = "SO"

        assert self.game.overtime == SHOOTOUT

    def test_bad_overtime_returns_default_number(self):
        self.game._overtime = "BAD"

        assert self.game.overtime == 0

    def test_bad_shots_on_goal_returns_default_number(self):
        self.game._shots_on_goal = ""

        assert self.game.shots_on_goal is None

    def test_bad_penalties_in_minutes_returns_default_number(self):
        self.game._penalties_in_minutes = ""

        assert self.game.penalties_in_minutes is None

    def test_bad_power_play_goals_returns_default_number(self):
        self.game._power_play_goals = ""

        assert self.game.power_play_goals is None

    def test_bad_power_play_opportunities_returns_default_number(self):
        self.game._power_play_opportunities = ""

        assert self.game.power_play_opportunities is None

    def test_bad_short_handed_goals_returns_default_number(self):
        self.game._short_handed_goals = ""

        assert self.game.short_handed_goals is None

    def test_bad_opp_shots_on_goal_returns_default_number(self):
        self.game._opp_shots_on_goal = ""

        assert self.game.opp_shots_on_goal is None

    def test_bad_opp_penalties_in_minutes_returns_default_number(self):
        self.game._opp_penalties_in_minutes = ""

        assert self.game.opp_penalties_in_minutes is None

    def test_bad_opp_power_play_goals_returns_default_number(self):
        self.game._opp_power_play_goals = ""

        assert self.game.opp_power_play_goals is None

    def test_bad_opp_power_play_opportunities_returns_default_number(self):
        self.game._opp_power_play_opportunities = ""

        assert self.game.opp_power_play_opportunities is None

    def test_bad_opp_short_handed_goals_returns_default_number(self):
        self.game._opp_short_handed_goals = ""

        assert self.game.opp_short_handed_goals is None

    def test_bad_corsi_for_returns_default_number(self):
        self.game._corsi_for = ""

        assert self.game.corsi_for is None

    def test_bad_corsi_against_returns_default_number(self):
        self.game._corsi_against = ""

        assert self.game.corsi_against is None

    def test_bad_corsi_for_percentage_returns_default_number(self):
        self.game._corsi_for_percentage = ""

        assert self.game.corsi_for_percentage is None

    def test_bad_fenwick_for_returns_default_number(self):
        self.game._fenwick_for = ""

        assert self.game.fenwick_for is None

    def test_bad_fenwick_against_returns_default_number(self):
        self.game._fenwick_against = ""

        assert self.game.fenwick_against is None

    def test_bad_fenwick_for_percentage_returns_default_number(self):
        self.game._fenwick_for_percentage = ""

        assert self.game.fenwick_for_percentage is None

    def test_bad_faceoff_wins_returns_default_number(self):
        self.game._faceoff_wins = ""

        assert self.game.faceoff_wins is None

    def test_bad_faceoff_losses_returns_default_number(self):
        self.game._faceoff_losses = ""

        assert self.game.faceoff_losses is None

    def test_bad_faceoff_win_percentage_returns_default_number(self):
        self.game._faceoff_win_percentage = ""

        assert self.game.faceoff_win_percentage is None

    def test_bad_offensive_zone_start_percentage_returns_default_number(self):
        self.game._offensive_zone_start_percentage = ""

        assert self.game.offensive_zone_start_percentage is None

    def test_bad_pdo_returns_default_number(self):
        self.game._pdo = ""

        assert self.game.pdo is None

    def test_empty_game_class_returns_dataframe_of_none(self):
        assert self.game._goals_scored is None
        assert self.game._goals_allowed is None
        assert self.game.dataframe is None

    def test_no_dataframes_returns_none(self):
        flexmock(Schedule).should_receive("_pull_schedule").and_return(None)
        schedule = Schedule("DET")

        fake_game = flexmock(dataframe=None)
        schedule.__iter__ = lambda: iter([fake_game])

        assert schedule.dataframe is None

    def test_no_dataframes_extended_returns_none(self):
        flexmock(Schedule).should_receive("_pull_schedule").and_return(None)
        schedule = Schedule("DET")

        fake_game = flexmock(dataframe_extended=None)
        schedule.__iter__ = lambda: iter([fake_game])

        assert schedule.dataframe_extended is None
