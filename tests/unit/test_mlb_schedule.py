from datetime import datetime

from flexmock import flexmock

from sportsipy.constants import AWAY, HOME, LOSS, WIN
from sportsipy.mlb.constants import DAY, NIGHT
from sportsipy.mlb.schedule import Game, Schedule


class TestMLBSchedule:
    def setup_method(self, *args, **kwargs):
        flexmock(Game).should_receive("_parse_game_data").and_return(None)

        self.game = Game(None, None)

    def test_double_header_returns_second_game(self):
        self.game._date = "Sunday, May 14 (2)"
        self.game._year = "2017"

        assert self.game.datetime == datetime(2017, 5, 14)
        assert self.game.game_number_for_day == 2

    def test_away_game_returns_away_location(self):
        self.game._location = "@"

        assert self.game.location == AWAY

    def test_home_game_returns_home_location(self):
        self.game._location = ""

        assert self.game.location == HOME

    def test_winning_result_returns_win(self):
        self.game._result = "W"

        assert self.game.result == WIN

    def test_losing_result_returns_loss(self):
        self.game._result = "L"

        assert self.game.result == LOSS

    def test_regular_length_game_returns_9_innings(self):
        self.game._innings = ""

        assert self.game.innings == 9

    def test_extra_innings_returns_total_innings(self):
        self.game._innings = "12"

        assert self.game.innings == 12

    def test_games_behind_returns_zero_when_tied(self):
        self.game._games_behind = "Tied"

        assert self.game.games_behind == 0.0

    def test_games_behind_returns_number_of_games_behind(self):
        self.game._games_behind = "1.5"

        assert self.game.games_behind == 1.5

    def test_games_behind_returns_number_of_games_ahead(self):
        self.game._games_behind = "up 1.5"

        assert self.game.games_behind == -1.5

        self.game._games_behind = "up13.0"

        assert self.game.games_behind == -13.0

    def test_no_save_returns_none(self):
        self.game._save = ""

        assert self.game.save is None

    def test_save_returns_name(self):
        self.game._save = "Verlander"

        assert self.game.save == "Verlander"

    def test_day_game_returns_daytime(self):
        self.game._day_or_night = "D"

        assert self.game.day_or_night == DAY

    def test_night_game_returns_nighttime(self):
        self.game._day_or_night = "N"

        assert self.game.day_or_night == NIGHT

    def test_empty_game_class_returns_dataframe_of_none(self):
        assert self.game.runs_allowed is None
        assert self.game.runs_scored is None
        assert self.game.dataframe is None

    def test_empty_boxscore_class_returns_dataframe_of_none(self):
        assert self.game.runs_allowed is None
        assert self.game.runs_scored is None
        assert self.game.dataframe_extended is None

    def test_invalid_dataframe_not_included_with_schedule_dataframes(self):
        # If a DataFrame is not valid, it should not be included with the
        # dataframes property. If no dataframes are present, the DataFrame
        # should return the default value of None.
        flexmock(Schedule).should_receive("_pull_schedule").and_return(None)
        schedule = Schedule("HOU")

        fake_game = flexmock(_runs_scored=None, _runs_allowed=None)
        schedule.__iter__ = lambda: iter([fake_game])

        assert schedule.dataframe is None

    def test_no_dataframes_extended_returns_none(self):
        flexmock(Schedule).should_receive("_pull_schedule").and_return(None)
        schedule = Schedule("HOU")

        fake_game = flexmock(dataframe_extended=None)
        schedule.__iter__ = lambda: iter([fake_game])

        assert schedule.dataframe_extended is None

    def test_bad_games_up_returns_default(self):
        self.game._games_behind = "up BAD"

        assert self.game.games_behind is None

    def test_bad_games_ahead_returns_default(self):
        self.game._games_behind = "BAD"

        assert self.game.games_behind is None
