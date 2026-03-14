"""Provide utilities for test fb schedule."""

from datetime import datetime
from os import path

import pandas as pd
import pytest
from pyquery import PyQuery

from sportsipy import utils
from sportsipy.constants import AWAY, DRAW
from sportsipy.fb.schedule import Schedule

NUM_GAMES_IN_SCHEDULE = 52

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


CORE_MATCH_FIELDS = (
    "competition",
    "matchweek",
    "day",
    "date",
    "time",
    "datetime",
    "venue",
    "result",
    "goals_for",
    "goals_against",
    "opponent",
    "opponent_id",
    "attendance",
    "captain",
    "captain_id",
    "formation",
    "referee",
    "match_report",
)


def read_file(filename):
    """Return read file."""
    filepath = path.join(path.dirname(__file__), "fb_stats", filename)
    return open(f"{filepath}", encoding="utf8").read()


def mock_pyquery(url, timeout=None):
    """Return mock pyquery."""

    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

    contents = read_file("tottenham-hotspur-2019-2020.html")
    return MockPQ(contents)


def _normalize_multiline(text: str) -> str:
    """Return a multi-line string with empty lines removed."""
    return "\n".join(line for line in text.splitlines() if line.strip())


class TestFBSchedule:
    """Represent TestFBSchedule."""

    def setup_method(self, *args, **kwargs):
        """Return setup method."""
        self.results = {
            "competition": "Premier League",
            "matchweek": "Matchweek 2",
            "day": "Sat",
            "date": "2019-08-17",
            "time": "17:30",
            "datetime": datetime(2019, 8, 17, 17, 30),
            "venue": AWAY,
            "result": DRAW,
            "goals_for": 2,
            "goals_against": 2,
            "shootout_scored": None,
            "shootout_against": None,
            "opponent": "Manchester City",
            "opponent_id": "b8fd03ef",
            "expected_goals": 0.1,
            "expected_goals_against": 2.9,
            "attendance": 54503,
            "captain": "Hugo Lloris",
            "captain_id": "8f62b6ee",
            "formation": "4-2-3-1",
            "referee": "Michael Oliver",
            "match_report": "a4ba771e",
            "notes": "",
        }

        self.schedule = Schedule("Tottenham Hotspur")

    def test_fb_schedule_returns_correct_number_of_games(self):
        """Return test fb schedule returns correct number of games."""
        assert len(self.schedule) == NUM_GAMES_IN_SCHEDULE

    def test_fb_schedule_returns_requested_match_from_index(self):
        """Return test fb schedule returns requested match from index."""
        match_two = self.schedule[1]

        for attribute in CORE_MATCH_FIELDS:
            assert getattr(match_two, attribute) == self.results[attribute]

    def test_fb_schedule_returns_requested_match_from_date(self):
        """Return test fb schedule returns requested match from date."""
        match_two = self.schedule(datetime(2019, 8, 17))

        for attribute in CORE_MATCH_FIELDS:
            assert getattr(match_two, attribute) == self.results[attribute]

    def test_no_games_for_date_raises_value_error(self):
        """Return test no games for date raises value error."""
        with pytest.raises(ValueError):
            self.schedule(datetime(2020, 7, 1))

    def test_empty_page_return_no_games(self, *args, **kwargs):
        """Return test empty page return no games."""
        utils.no_data_found = lambda: None
        utils.get_stats_table = lambda *_args, **_kwargs: None

        schedule = Schedule("Tottenham Hotspur")

        assert len(schedule) == 0

    def test_schedule_iter_returns_correct_number_of_games(self):
        """Return test schedule iter returns correct number of games."""
        count = 0
        for _, _ in enumerate(self.schedule):
            count += 1

        assert count == NUM_GAMES_IN_SCHEDULE

    def test_fb_schedule_dataframe_returns_dataframe(self):
        """Return test fb schedule dataframe returns dataframe."""
        match_two = self.schedule[1]
        df = match_two.dataframe

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "a4ba771e" in df.index
        for attribute in CORE_MATCH_FIELDS:
            assert attribute in df.columns

    def test_no_captain_returns_default(self):
        """Return test no captain returns default."""
        table_item = '<td data-stat="captain"><a></a></td>'

        captain = self.schedule[0]._parse_captain_id(PyQuery(table_item))

        assert not captain

    def test_no_match_report_returns_default(self):
        """Return test no match report returns default."""
        table_item = '<td data-stat="match_report"><a></a></td>'

        report = self.schedule[0]._parse_match_report(PyQuery(table_item))

        assert not report

    def test_fb_schedule_string_representation(self):
        """Return test fb schedule string representation."""
        schedule_repr = _normalize_multiline(repr(self.schedule))

        assert "2019-08-10 - Aston Villa" in schedule_repr
        assert "2019-08-17 - Manchester City" in schedule_repr
        assert "2020-07-26 - Crystal Palace" in schedule_repr

    def test_fb_game_string_representation(self):
        """Return test fb game string representation."""
        game = self.schedule[0]

        assert repr(game) == "2019-08-10 - Aston Villa"
