"""Provide utilities for test mlb schedule."""

import os
from datetime import datetime

import pandas as pd
import pytest
from flexmock import flexmock

from sportsipy import utils
from sportsipy.constants import AWAY, HOME, LOSS, WIN
from sportsipy.mlb.boxscore import Boxscore
from sportsipy.mlb.constants import NIGHT
from sportsipy.mlb.schedule import Schedule

MONTH = 4
YEAR = 2017

NUM_GAMES_IN_SCHEDULE = 162


def read_file(filename):
    """Return read file."""
    filepath = os.path.join(os.path.dirname(__file__), "mlb", filename)
    return open(f"{filepath}", encoding="utf8").read()


def mock_pyquery(url, timeout=None):
    """Return mock pyquery."""

    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

        def __call__(self, div):
            return read_file("table.html")

    schedule = read_file(f"{YEAR}-schedule-scores.html")
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


def _normalize_multiline(text: str) -> str:
    """Return a multi-line string with empty lines removed."""
    return "\n".join(line for line in text.splitlines() if line.strip())


def _normalize_field(attribute, value):
    """Return normalized field value for comparison."""
    if attribute == "boxscore_index" and isinstance(value, str):
        return value.strip()
    return value


class MockDateTime:
    """Represent MockDateTime."""

    def __init__(self, year, month):
        """Initialize the class instance."""
        self.year = year
        self.month = month


class TestMLBSchedule:
    """Represent TestMLBSchedule."""

    def setup_method(self, *args, **kwargs):
        """Return setup method."""
        self.results = {
            "game": 2,
            "boxscore_index": "TBA/TBA201704040",
            "date": "Tuesday, Apr 4",
            "datetime": datetime(2017, 4, 4),
            "game_number_for_day": 1,
            "location": AWAY,
            "opponent_abbr": "TBR",
            "result": WIN,
            "runs_scored": 5,
            "runs_allowed": 0,
            "innings": 9,
            "record": "1-1",
            "rank": 3,
            "games_behind": 0.5,
            "winner": "Sabathia",
            "loser": "Odorizzi",
            "save": None,
            "game_duration": "3:07",
            "day_or_night": NIGHT,
            "attendance": 19366,
            "streak": "+",
        }
        flexmock(Boxscore).should_receive("_parse_game_data").and_return(None)
        flexmock(Boxscore).should_receive("dataframe").and_return(pd.DataFrame([{"key": "value"}]))
        flexmock(utils).should_receive("todays_date").and_return(MockDateTime(YEAR, MONTH))

        self.schedule = Schedule("NYY")

    def test_mlb_schedule_returns_correct_number_of_games(self):
        """Return test mlb schedule returns correct number of games."""
        assert len(self.schedule) == NUM_GAMES_IN_SCHEDULE

    def test_mlb_schedule_returns_requested_match_from_index(self):
        """Return test mlb schedule returns requested match from index."""
        match_two = self.schedule[1]

        for attribute, value in self.results.items():
            assert _normalize_field(attribute, getattr(match_two, attribute)) == value

    def test_mlb_schedule_returns_requested_match_from_date(self):
        """Return test mlb schedule returns requested match from date."""
        match_two = self.schedule(datetime(2017, 4, 4))

        for attribute, value in self.results.items():
            assert _normalize_field(attribute, getattr(match_two, attribute)) == value

    def test_mlb_schedule_returns_second_game_in_double_header(self):
        """Return test mlb schedule returns second game in double header."""
        match_two = self.schedule(datetime(2017, 5, 14), 2)
        results = {
            "game": 35,
            "date": "Sunday, May 14 (2)",
            "datetime": datetime(2017, 5, 14),
            "game_number_for_day": 2,
            "location": HOME,
            "opponent_abbr": "HOU",
            "result": LOSS,
            "runs_scored": 7,
            "runs_allowed": 10,
            "innings": 9,
            "record": "22-13",
            "rank": 1,
            "games_behind": -0.5,
            "winner": "Morton",
            "loser": "Tanaka",
            "save": None,
            "game_duration": "3:49",
            "day_or_night": NIGHT,
            "attendance": 47883,
            "streak": "-",
        }

        for attribute, value in results.items():
            assert getattr(match_two, attribute) == value

    def test_mlb_schedule_dataframe_returns_dataframe(self):
        """Return test mlb schedule dataframe returns dataframe."""
        match_two = self.schedule[1]
        df = match_two.dataframe

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "boxscore_index" in df.columns

    def test_mlb_schedule_dataframe_extended_returns_dataframe(self):
        """Return test mlb schedule dataframe extended returns dataframe."""
        df = pd.DataFrame([{"key": "value"}])

        result = self.schedule[1].dataframe_extended

        frames = [df, result]
        df1 = pd.concat(frames).drop_duplicates(keep=False)

        assert df1.empty

    def test_mlb_schedule_all_dataframe_returns_dataframe(self):
        """Return test mlb schedule all dataframe returns dataframe."""
        df = self.schedule.dataframe
        assert df is not None
        result = df.drop_duplicates(keep=False)

        assert len(result) == NUM_GAMES_IN_SCHEDULE
        assert set(result.columns.values) == set(self.results.keys())

    def test_mlb_schedule_all_dataframe_extended_returns_dataframe(self):
        """Return test mlb schedule all dataframe extended returns dataframe."""
        result = self.schedule.dataframe_extended
        assert result is not None

        assert len(result) == NUM_GAMES_IN_SCHEDULE

    def test_no_games_for_date_raises_value_error(self):
        """Return test no games for date raises value error."""
        with pytest.raises(ValueError):
            self.schedule(datetime.now())

    def test_empty_page_return_no_games(self, *args, **kwargs):
        """Return test empty page return no games."""
        flexmock(utils).should_receive("no_data_found").once()
        flexmock(utils).should_receive("get_stats_table").and_return(None)

        schedule = Schedule("NYY")

        assert len(schedule) == 0

    def test_game_string_representation(self):
        """Return test game string representation."""
        game = self.schedule[0]

        assert repr(game) == "Sunday, Apr 2 - TBR"

    def test_schedule_string_representation(self):
        """Return test schedule string representation."""
        expected = """Sunday, Apr 2 - TBR

Tuesday, Apr 4 - TBR
Wednesday, Apr 5 - TBR
Friday, Apr 7 - BAL
Saturday, Apr 8 - BAL
Sunday, Apr 9 - BAL
Monday, Apr 10 - TBR
Wednesday, Apr 12 - TBR
Thursday, Apr 13 - TBR
Friday, Apr 14 - STL
Saturday, Apr 15 - STL
Sunday, Apr 16 - STL
Monday, Apr 17 - CHW
Tuesday, Apr 18 - CHW
Wednesday, Apr 19 - CHW
Friday, Apr 21 - PIT
Saturday, Apr 22 - PIT
Sunday, Apr 23 - PIT
Wednesday, Apr 26 - BOS
Thursday, Apr 27 - BOS
Friday, Apr 28 - BAL
Saturday, Apr 29 - BAL
Sunday, Apr 30 - BAL
Monday, May 1 - TOR
Tuesday, May 2 - TOR
Wednesday, May 3 - TOR
Friday, May 5 - CHC
Saturday, May 6 - CHC
Sunday, May 7 - CHC
Monday, May 8 - CIN
Tuesday, May 9 - CIN
Thursday, May 11 - HOU
Friday, May 12 - HOU
Sunday, May 14 (1) - HOU
Sunday, May 14 (2) - HOU
Tuesday, May 16 - KCR
Wednesday, May 17 - KCR
Thursday, May 18 - KCR
Friday, May 19 - TBR
Saturday, May 20 - TBR
Sunday, May 21 - TBR
Monday, May 22 - KCR
Tuesday, May 23 - KCR
Wednesday, May 24 - KCR
Friday, May 26 - OAK
Saturday, May 27 - OAK
Sunday, May 28 - OAK
Monday, May 29 - BAL
Tuesday, May 30 - BAL
Wednesday, May 31 - BAL
Thursday, Jun 1 - TOR
Friday, Jun 2 - TOR
Saturday, Jun 3 - TOR
Sunday, Jun 4 - TOR
Tuesday, Jun 6 - BOS
Wednesday, Jun 7 - BOS
Thursday, Jun 8 - BOS
Friday, Jun 9 - BAL
Saturday, Jun 10 - BAL
Sunday, Jun 11 - BAL
Monday, Jun 12 - LAA
Tuesday, Jun 13 - LAA
Wednesday, Jun 14 - LAA
Thursday, Jun 15 - OAK
Friday, Jun 16 - OAK
Saturday, Jun 17 - OAK
Sunday, Jun 18 - OAK
Tuesday, Jun 20 - LAA
Wednesday, Jun 21 - LAA
Thursday, Jun 22 - LAA
Friday, Jun 23 - TEX
Saturday, Jun 24 - TEX
Sunday, Jun 25 - TEX
Monday, Jun 26 - CHW
Tuesday, Jun 27 - CHW
Wednesday, Jun 28 - CHW
Thursday, Jun 29 - CHW
Friday, Jun 30 - HOU
Saturday, Jul 1 - HOU
Sunday, Jul 2 - HOU
Monday, Jul 3 - TOR
Tuesday, Jul 4 - TOR
Wednesday, Jul 5 - TOR
Friday, Jul 7 - MIL
Saturday, Jul 8 - MIL
Sunday, Jul 9 - MIL
Friday, Jul 14 - BOS
Saturday, Jul 15 - BOS
Sunday, Jul 16 (1) - BOS
Sunday, Jul 16 (2) - BOS
Monday, Jul 17 - MIN
Tuesday, Jul 18 - MIN
Wednesday, Jul 19 - MIN
Thursday, Jul 20 - SEA
Friday, Jul 21 - SEA
Saturday, Jul 22 - SEA
Sunday, Jul 23 - SEA
Tuesday, Jul 25 - CIN
Wednesday, Jul 26 - CIN
Thursday, Jul 27 - TBR
Friday, Jul 28 - TBR
Saturday, Jul 29 - TBR
Sunday, Jul 30 - TBR
Monday, Jul 31 - DET
Tuesday, Aug 1 - DET
Wednesday, Aug 2 - DET
Thursday, Aug 3 - CLE
Friday, Aug 4 - CLE
Saturday, Aug 5 - CLE
Sunday, Aug 6 - CLE
Tuesday, Aug 8 - TOR
Wednesday, Aug 9 - TOR
Thursday, Aug 10 - TOR
Friday, Aug 11 - BOS
Saturday, Aug 12 - BOS
Sunday, Aug 13 - BOS
Monday, Aug 14 - NYM
Tuesday, Aug 15 - NYM
Wednesday, Aug 16 - NYM
Thursday, Aug 17 - NYM
Friday, Aug 18 - BOS
Saturday, Aug 19 - BOS
Sunday, Aug 20 - BOS
Tuesday, Aug 22 - DET
Wednesday, Aug 23 - DET
Thursday, Aug 24 - DET
Friday, Aug 25 - SEA
Saturday, Aug 26 - SEA
Sunday, Aug 27 - SEA
Monday, Aug 28 - CLE
Wednesday, Aug 30 (1) - CLE
Wednesday, Aug 30 (2) - CLE
Thursday, Aug 31 - BOS
Friday, Sep 1 - BOS
Saturday, Sep 2 - BOS
Sunday, Sep 3 - BOS
Monday, Sep 4 - BAL
Tuesday, Sep 5 - BAL
Thursday, Sep 7 - BAL
Friday, Sep 8 - TEX
Saturday, Sep 9 - TEX
Sunday, Sep 10 - TEX
Monday, Sep 11 - TBR
Tuesday, Sep 12 - TBR
Wednesday, Sep 13 - TBR
Thursday, Sep 14 - BAL
Friday, Sep 15 - BAL
Saturday, Sep 16 - BAL
Sunday, Sep 17 - BAL
Monday, Sep 18 - MIN
Tuesday, Sep 19 - MIN
Wednesday, Sep 20 - MIN
Friday, Sep 22 - TOR
Saturday, Sep 23 - TOR
Sunday, Sep 24 - TOR
Monday, Sep 25 - KCR
Tuesday, Sep 26 - TBR
Wednesday, Sep 27 - TBR
Thursday, Sep 28 - TBR
Friday, Sep 29 - TOR
Saturday, Sep 30 - TOR
Sunday, Oct 1 - TOR"""

        assert _normalize_multiline(repr(self.schedule)) == _normalize_multiline(expected)


class TestMLBScheduleInvalidYear:
    """Represent TestMLBScheduleInvalidYear."""

    def test_mlb_invalid_default_year_reverts_to_previous_year(self, *args, **kwargs):
        """Return test mlb invalid default year reverts to previous year."""
        results = {
            "game": 2,
            "boxscore_index": "TBA/TBA201704040",
            "date": "Tuesday, Apr 4",
            "datetime": datetime(2017, 4, 4),
            "game_number_for_day": 1,
            "location": AWAY,
            "opponent_abbr": "TBR",
            "result": WIN,
            "runs_scored": 5,
            "runs_allowed": 0,
            "innings": 9,
            "record": "1-1",
            "rank": 3,
            "games_behind": 0.5,
            "winner": "Sabathia",
            "loser": "Odorizzi",
            "save": None,
            "game_duration": "3:07",
            "day_or_night": NIGHT,
            "attendance": 19366,
            "streak": "+",
        }
        flexmock(Boxscore).should_receive("_parse_game_data").and_return(None)
        flexmock(Boxscore).should_receive("dataframe").and_return(pd.DataFrame([{"key": "value"}]))
        flexmock(utils).should_receive("find_year_for_season").and_return(2018)

        schedule = Schedule("NYY")

        for attribute, value in results.items():
            assert _normalize_field(attribute, getattr(schedule[1], attribute)) == value
