"""Provide utilities for test nfl schedule."""

from typing import cast

from flexmock import flexmock

from sportsipy import utils
from sportsipy.constants import (
    AWAY,
    HOME,
    LOSS,
    NEUTRAL,
    POST_SEASON,
    REGULAR_SEASON,
    TIE,
    WIN,
)
from sportsipy.nfl.constants import CONF_CHAMPIONSHIP, DIVISION, SUPER_BOWL, WILD_CARD
from sportsipy.nfl.schedule import Game, Schedule

YEAR = 2017


class TestNFLSchedule:
    """Represent TestNFLSchedule."""

    def setup_method(self, *args, **kwargs):
        """Return setup method."""
        flexmock(Game).should_receive("_parse_game_data").and_return(None)

        self.game = Game(None, REGULAR_SEASON, YEAR)

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

    def test_tied_result_returns_tie(self):
        """Return test tied result returns tie."""
        self.game._result = "T"

        assert self.game.result == TIE

    def test_invalid_result_returns_none(self):
        """Return test invalid result returns none."""
        self.game._result = "X"

        assert self.game.result is None

    def test_no_result_returns_none(self):
        """Return test no result returns none."""
        self.game._result = ""

        assert self.game.result is None

    def test_overtime_returns_overtime(self):
        """Return test overtime returns overtime."""
        self.game._overtime = "OT"

        assert self.game.overtime

    def test_no_overtime_returns_none(self):
        """Return test no overtime returns none."""
        self.game._overtime = ""

        assert not self.game.overtime

    def test_regular_season_type(self):
        """Return test regular season type."""
        assert self.game.type == REGULAR_SEASON

    def test_playoff_type(self):
        """Return test playoff type."""
        game = Game(None, POST_SEASON, YEAR)

        assert game.type == POST_SEASON

    def test_wild_card_game_returns_wild_card(self):
        """Return test wild card game returns wild card."""
        self.game._week = "Wild Card"

        assert self.game.week == WILD_CARD

    def test_division_playoff_game_returns_division(self):
        """Return test division playoff game returns division."""
        self.game._week = "Division"

        assert self.game.week == DIVISION

    def test_conference_championship_returns_division(self):
        """Return test conference championship returns division."""
        self.game._week = "Conf. Champ."

        assert self.game.week == CONF_CHAMPIONSHIP

    def test_super_bowl_returns_super_bowl(self):
        """Return test super bowl returns super bowl."""
        self.game._week = "SuperBowl"

        assert self.game.week == SUPER_BOWL

    def test_empty_game_class_returns_dataframe_of_none(self):
        """Return test empty game class returns dataframe of none."""
        assert self.game._points_scored is None
        assert self.game._points_allowed is None
        assert self.game.dataframe is None

    def test_date_property_formats_iso_date(self):
        """Return test date property formats iso date."""
        self.game._date = "2017-09-17"

        assert self.game.date == "September 17"

    def test_datetime_property_handles_iso_date(self):
        """Return test datetime property handles iso date."""
        self.game._date = "2017-09-17"
        self.game._day = "Sun"

        result = self.game.datetime

        assert result is not None
        assert result.year == 2017
        assert result.month == 9
        assert result.day == 17

    def test_datetime_property_returns_none_without_year(self):
        """Return test datetime property returns none without year."""
        self.game._year = None
        self.game._date = "September 17"
        self.game._day = "Sun"

        assert self.game.datetime is None

    def test_parse_abbreviation_without_href_sets_none(self):
        """Return test parse abbreviation without href sets none."""
        game_data = utils.pq('<tr><td data-stat="opp_name_abbr">No Opponent</td></tr>')

        self.game._parse_abbreviation(game_data)

        assert self.game.opponent_abbr is None

    def test_parse_boxscore_falls_back_to_date_cell(self):
        """Return test parse boxscore falls back to date cell."""
        game_data = utils.pq(
            '<tr><td data-stat="boxscore_word"></td>'
            '<td data-stat="game_date"><a href="/boxscores/201709170nor.htm">Date</a></td></tr>'
        )

        self.game._parse_boxscore(game_data)

        assert self.game.boxscore_index == "201709170nor"

    def test_parse_boxscore_without_href_sets_empty_string(self):
        """Return test parse boxscore without href sets empty string."""
        game_data = utils.pq(
            '<tr><td data-stat="boxscore_word"></td><td data-stat="game_date">Date</td></tr>'
        )

        self.game._parse_boxscore(game_data)

        assert self.game.boxscore_index == ""

    def test_no_dataframes_returns_none(self):
        """Return test no dataframes returns none."""
        flexmock(Schedule).should_receive("_pull_schedule").and_return(None)
        schedule = Schedule("DET")

        fake_game = cast(Game, flexmock(dataframe=None))
        schedule._games = [fake_game]

        assert schedule.dataframe is None

    def test_no_dataframes_extended_returns_none(self):
        """Return test no dataframes extended returns none."""
        flexmock(Schedule).should_receive("_pull_schedule").and_return(None)
        schedule = Schedule("DET")

        fake_game = cast(Game, flexmock(dataframe_extended=None))
        schedule._games = [fake_game]

        assert schedule.dataframe_extended is None
