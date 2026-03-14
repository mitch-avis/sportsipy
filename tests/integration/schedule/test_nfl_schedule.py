"""Provide utilities for test nfl schedule."""

import os
from datetime import datetime
from typing import Any, cast

import pandas as pd
import pytest

from sportsipy import utils
from sportsipy.constants import AWAY, REGULAR_SEASON, WIN
from sportsipy.nfl.boxscore import Boxscore
from sportsipy.nfl.schedule import Schedule

MONTH = 9
YEAR = 2017

NUM_GAMES_IN_SCHEDULE = 19

ORIGINAL_TODAYS_DATE = utils.todays_date
ORIGINAL_GET_STATS_TABLE = utils.get_stats_table
ORIGINAL_NO_DATA_FOUND = utils.no_data_found
ORIGINAL_FIND_YEAR_FOR_SEASON = utils.find_year_for_season


@pytest.fixture(autouse=True)
def _reset_utils(monkeypatch):
    """Reset shared utils callables for isolated tests."""
    monkeypatch.setattr(utils, "todays_date", ORIGINAL_TODAYS_DATE)
    monkeypatch.setattr(utils, "get_stats_table", ORIGINAL_GET_STATS_TABLE)
    monkeypatch.setattr(utils, "no_data_found", ORIGINAL_NO_DATA_FOUND)
    monkeypatch.setattr(utils, "find_year_for_season", ORIGINAL_FIND_YEAR_FOR_SEASON)


@pytest.fixture(autouse=True)
def _patch_boxscore(monkeypatch):
    """Patch Boxscore parsing/dataframe for deterministic schedule tests."""
    monkeypatch.setattr(Boxscore, "_parse_game_data", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        cast(Any, Boxscore),
        "dataframe",
        property(lambda _self: pd.DataFrame([{"key": "value"}])),
    )


def _normalize_multiline(text: str) -> str:
    """Return a multi-line string with empty lines removed."""
    return "\n".join(line for line in text.splitlines() if line.strip())


def read_file(filename):
    """Return read file."""
    filepath = os.path.join(os.path.dirname(__file__), "nfl", filename)
    return open(f"{filepath}", encoding="utf8").read()


def mock_pyquery(url, timeout=None):
    """Return mock pyquery."""

    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

        def __call__(self, div):
            if "playoff" in div.lower():
                return read_file("playoff_table.html")
            return read_file("table.html")

    schedule = read_file("gamelog.html")
    return MockPQ(schedule)


def mock_request(url, timeout=None):
    """Return mock request."""

    class MockRequest:
        def __init__(self, html_contents, status_code=200):
            self.status_code = status_code
            self.html_contents = html_contents
            self.text = html_contents

    if str(YEAR) in url:
        return MockRequest("good")
    return MockRequest("bad", status_code=404)


class MockDateTime:
    """Represent MockDateTime."""

    def __init__(self, year, month):
        """Initialize the class instance."""
        self.year = year
        self.month = month


class TestNFLSchedule:
    """Represent TestNFLSchedule."""

    def setup_method(self, *args, **kwargs):
        """Return setup method."""
        self.results = {
            "week": 2,
            "boxscore_index": "201709170nor",
            "day": "Sun",
            "date": "September 17",
            "type": REGULAR_SEASON,
            "datetime": datetime(2017, 9, 17, 0, 0),
            "result": WIN,
            "overtime": 0,
            "location": AWAY,
            "opponent_abbr": "NOR",
            "opponent_name": "NOR",
            "points_scored": 36,
            "points_allowed": 20,
            "pass_completions": 30,
            "pass_attempts": 39,
            "pass_yards": 436,
            "pass_touchdowns": 3,
            "interceptions": 0,
            "times_sacked": 2,
            "yards_lost_from_sacks": 11,
            "pass_yards_per_attempt": 11.2,
            "pass_completion_rate": 76.9,
            "quarterback_rating": 138.4,
            "rush_attempts": 31,
            "rush_yards": 119,
            "rush_yards_per_attempt": 3.8,
            "rush_touchdowns": 1,
            "field_goals_made": 3,
            "field_goals_attempted": 3,
            "extra_points_made": 3,
            "extra_points_attempted": 4,
            "punts": 3,
            "punt_yards": 111,
            "third_down_conversions": 6,
            "third_down_attempts": 12,
            "fourth_down_conversions": 0,
            "fourth_down_attempts": 0,
            "time_of_possession": "35:06",
        }
        utils.todays_date = lambda: MockDateTime(YEAR, MONTH)

        self.schedule = Schedule("NWE")

    def test_nfl_schedule_returns_correct_number_of_games(self):
        """Return test nfl schedule returns correct number of games."""
        assert len(self.schedule) == NUM_GAMES_IN_SCHEDULE

    def test_nfl_schedule_returns_requested_match_from_index(self):
        """Return test nfl schedule returns requested match from index."""
        match_two = self.schedule[1]

        for attribute, value in self.results.items():
            assert getattr(match_two, attribute) == value

    def test_nfl_schedule_returns_requested_match_from_date(self):
        """Return test nfl schedule returns requested match from date."""
        match_two = self.schedule(datetime(2017, 9, 17))

        for attribute, value in self.results.items():
            assert getattr(match_two, attribute) == value

    def test_nfl_schedule_dataframe_returns_dataframe(self):
        """Return test nfl schedule dataframe returns dataframe."""
        df = pd.DataFrame([self.results], index=["201709170nor"])

        match_two = self.schedule[1]
        # Pandas doesn't natively allow comparisons of DataFrames.
        # Concatenating the two DataFrames (the one generated during the test
        # and the expected one above) and dropping duplicate rows leaves only
        # the rows that are unique between the two frames. This allows a quick
        # check of the DataFrame to see if it is empty - if so, all rows are
        # duplicates, and they are equal.
        frames = [df, match_two.dataframe]
        df1 = pd.concat(frames).drop_duplicates(keep=False)

        assert df1.empty

    def test_nfl_schedule_dataframe_extended_returns_dataframe(self):
        """Return test nfl schedule dataframe extended returns dataframe."""
        df = pd.DataFrame([{"key": "value"}])

        result = self.schedule[1].dataframe_extended

        frames = [df, result]
        df1 = pd.concat(frames).drop_duplicates(keep=False)

        assert df1.empty

    def test_nfl_schedule_all_dataframe_returns_dataframe(self):
        """Return test nfl schedule all dataframe returns dataframe."""
        df = self.schedule.dataframe
        assert df is not None
        result = df.drop_duplicates(keep=False)

        assert len(result) == NUM_GAMES_IN_SCHEDULE
        assert set(result.columns.values) == set(self.results.keys())

    def test_nfl_schedule_all_dataframe_extended_returns_dataframe(self):
        """Return test nfl schedule all dataframe extended returns dataframe."""
        result = self.schedule.dataframe_extended
        assert result is not None

        assert len(result) == NUM_GAMES_IN_SCHEDULE

    def test_no_games_for_date_raises_value_error(self):
        """Return test no games for date raises value error."""
        with pytest.raises(ValueError):
            self.schedule(datetime.now())

    def test_empty_page_return_no_games(self, *args, **kwargs):
        """Return test empty page return no games."""
        utils.no_data_found = lambda: None
        utils.get_stats_table = lambda *_args, **_kwargs: None

        schedule = Schedule("NWE")

        assert len(schedule) == 0

    def test_game_string_representation(self):
        """Return test game string representation."""
        game = self.schedule[0]

        assert repr(game) == "September 7 - KAN"

    def test_schedule_string_representation(self):
        """Return test schedule string representation."""
        expected = """September 7 - KAN

September 17 - NOR
September 24 - HTX
October 1 - CAR
October 5 - TAM
October 15 - NYJ
October 22 - ATL
October 29 - SDG
November 12 - DEN
November 19 - RAI
November 26 - MIA
December 3 - BUF
December 11 - MIA
December 17 - PIT
December 24 - BUF
December 31 - NYJ
January 13 - OTI
January 21 - JAX
February 4 - PHI"""

        assert _normalize_multiline(repr(self.schedule)) == _normalize_multiline(expected)


class TestNFLScheduleInvalidYear:
    """Represent TestNFLScheduleInvalidYear."""

    def test_invalid_default_year_reverts_to_previous_year(self, *args, **kwargs):
        """Return test invalid default year reverts to previous year."""
        results = {
            "week": 2,
            "boxscore_index": "201709170nor",
            "day": "Sun",
            "date": "September 17",
            "type": REGULAR_SEASON,
            "datetime": datetime(2017, 9, 17, 0, 0),
            "result": WIN,
            "overtime": 0,
            "location": AWAY,
            "opponent_abbr": "NOR",
            "opponent_name": "NOR",
            "points_scored": 36,
            "points_allowed": 20,
            "pass_completions": 30,
            "pass_attempts": 39,
            "pass_yards": 436,
            "pass_touchdowns": 3,
            "interceptions": 0,
            "times_sacked": 2,
            "yards_lost_from_sacks": 11,
            "pass_yards_per_attempt": 11.2,
            "pass_completion_rate": 76.9,
            "quarterback_rating": 138.4,
            "rush_attempts": 31,
            "rush_yards": 119,
            "rush_yards_per_attempt": 3.8,
            "rush_touchdowns": 1,
            "field_goals_made": 3,
            "field_goals_attempted": 3,
            "extra_points_made": 3,
            "extra_points_attempted": 4,
            "punts": 3,
            "punt_yards": 111,
            "third_down_conversions": 6,
            "third_down_attempts": 12,
            "fourth_down_conversions": 0,
            "fourth_down_attempts": 0,
            "time_of_possession": "35:06",
        }
        utils.find_year_for_season = lambda _league: 2018

        schedule = Schedule("NWE")

        for attribute, value in results.items():
            assert getattr(schedule[1], attribute) == value
