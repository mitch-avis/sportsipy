"""Provide utilities for test nhl integration."""

import os

import polars as pl
import pytest

from sportsipy import utils
from sportsipy.nhl.teams import Team, Teams

MONTH = 1
YEAR = 2017

ORIGINAL_GET_STATS_TABLE = utils.get_stats_table
ORIGINAL_NO_DATA_FOUND = utils.no_data_found
ORIGINAL_FIND_YEAR_FOR_SEASON = utils.find_year_for_season


def read_file(filename):
    """Return read file."""
    filepath = os.path.join(os.path.dirname(__file__), "nhl_stats", filename)
    return open(f"{filepath}", encoding="utf8").read()


def mock_pyquery(url, timeout=None):
    """Return mock pyquery."""

    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

        def __call__(self, div):
            return read_file(f"NHL_{YEAR}_all_stats.html")

    html_contents = read_file(f"NHL_{YEAR}.html")
    return MockPQ(html_contents)


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


class MockDateTime:
    """Represent MockDateTime."""

    def __init__(self, year, month):
        """Initialize the class instance."""
        self.year = year
        self.month = month


class TestNHLIntegration:
    """Represent TestNHLIntegration."""

    @pytest.fixture(autouse=True)
    def _patch_todays_date(self, monkeypatch):
        """Patch today's date for deterministic tests."""
        monkeypatch.setattr(utils, "get_stats_table", ORIGINAL_GET_STATS_TABLE)
        monkeypatch.setattr(utils, "no_data_found", ORIGINAL_NO_DATA_FOUND)
        monkeypatch.setattr(utils, "find_year_for_season", ORIGINAL_FIND_YEAR_FOR_SEASON)
        monkeypatch.setattr(utils, "todays_date", lambda: MockDateTime(YEAR, MONTH))

    def setup_method(self, *args, **kwargs):
        """Return setup method."""
        self.results = {
            "rank": 25,
            "abbreviation": "DET",
            "name": "Detroit Red Wings",
            "average_age": 28.4,
            "games_played": 82,
            "wins": 33,
            "losses": 36,
            "overtime_losses": 13,
            "points": 79,
            "points_percentage": 0.482,
            "goals_for": 198,
            "goals_against": None,
            "simple_rating_system": -0.41,
            "strength_of_schedule": 0.04,
            "total_goals_per_game": None,
            "power_play_goals": 38,
            "power_play_opportunities": 252,
            "power_play_percentage": 15.08,
            "power_play_goals_against": 45,
            "power_play_opportunities_against": 235,
            "penalty_killing_percentage": 80.85,
            "short_handed_goals": 3,
            "short_handed_goals_against": 9,
            "shots_on_goal": 2335,
            "shooting_percentage": 8.5,
            "shots_against": 2507,
            "save_percentage": 0.903,
            "pdo_at_even_strength": None,
        }
        self.abbreviations = [
            "WSH",
            "PIT",
            "CHI",
            "CBJ",
            "MIN",
            "ANA",
            "MTL",
            "EDM",
            "NYR",
            "STL",
            "SJS",
            "OTT",
            "TOR",
            "BOS",
            "TBL",
            "NYI",
            "NSH",
            "CGY",
            "PHI",
            "WPG",
            "CAR",
            "LAK",
            "FLA",
            "DAL",
            "DET",
            "BUF",
            "ARI",
            "NJD",
            "VAN",
            "COL",
        ]
        _ = read_file(f"NHL_{YEAR}.html")

        self.teams = Teams()

    def test_nhl_integration_returns_correct_number_of_teams(self):
        """Return test nhl integration returns correct number of teams."""
        assert len(self.teams) == len(self.abbreviations)

    def test_nhl_integration_returns_correct_attributes_for_team(self):
        """Return test nhl integration returns correct attributes for team."""
        detroit = self.teams("DET")

        for attribute, value in self.results.items():
            assert getattr(detroit, attribute) == value

    def test_nhl_integration_returns_correct_team_abbreviations(self):
        """Return test nhl integration returns correct team abbreviations."""
        for team in self.teams:
            assert team.abbreviation in self.abbreviations

    def test_nhl_integration_dataframe_returns_dataframe(self):
        """Return test nhl integration dataframe returns dataframe."""
        df = pl.DataFrame([self.results])

        detroit = self.teams("DET")
        # Polars doesn't natively allow comparisons of DataFrames.
        # Concatenating the two DataFrames (the one generated during the test
        # and the expected one above) and dropping duplicate rows leaves only
        # the rows that are unique between the two frames. This allows a quick
        # check of the DataFrame to see if it is empty - if so, all rows are
        # duplicates, and they are equal.
        df1 = pl.concat([df, detroit.dataframe.select(df.columns)]).unique(keep="none")

        assert df1.is_empty()

    def test_nhl_integration_all_teams_dataframe_returns_dataframe(self):
        """Return test nhl integration all teams dataframe returns dataframe."""
        result = self.teams.dataframes.unique(keep="none")

        assert len(result) == len(self.abbreviations)
        assert set(result.columns) == set(self.results.keys())

    def test_nhl_invalid_team_name_raises_value_error(self):
        """Return test nhl invalid team name raises value error."""
        with pytest.raises(ValueError):
            self.teams("INVALID_NAME")

    def test_nhl_empty_page_returns_no_teams(self, monkeypatch, *args, **kwargs):
        """Return test nhl empty page returns no teams."""
        monkeypatch.setattr(utils, "no_data_found", lambda: None)
        monkeypatch.setattr(utils, "get_stats_table", lambda *_args, **_kwargs: None)

        teams = Teams()

        assert len(teams) == 0

    def test_pulling_team_directly(self, *args, **kwargs):
        """Return test pulling team directly."""
        detroit = Team("DET")

        for attribute, value in self.results.items():
            assert getattr(detroit, attribute) == value

    def test_team_string_representation(self, *args, **kwargs):
        """Return test team string representation."""
        detroit = Team("DET")

        assert repr(detroit) == "Detroit Red Wings (DET) - 2017"

    def test_teams_string_representation(self, *args, **kwargs):
        """Return test teams string representation."""
        expected = """Washington Capitals (WSH)

Pittsburgh Penguins (PIT)
Chicago Blackhawks (CHI)
Columbus Blue Jackets (CBJ)
Minnesota Wild (MIN)
Anaheim Ducks (ANA)
Montreal Canadiens (MTL)
Edmonton Oilers (EDM)
New York Rangers (NYR)
St. Louis Blues (STL)
San Jose Sharks (SJS)
Ottawa Senators (OTT)
Toronto Maple Leafs (TOR)
Boston Bruins (BOS)
Calgary Flames (CGY)
Tampa Bay Lightning (TBL)
Nashville Predators (NSH)
New York Islanders (NYI)
Philadelphia Flyers (PHI)
Winnipeg Jets (WPG)
Carolina Hurricanes (CAR)
Los Angeles Kings (LAK)
Florida Panthers (FLA)
Dallas Stars (DAL)
Detroit Red Wings (DET)
Buffalo Sabres (BUF)
New Jersey Devils (NJD)
Arizona Coyotes (ARI)
Vancouver Canucks (VAN)
Colorado Avalanche (COL)"""

        teams = Teams()

        assert _normalize_multiline(repr(teams)) == _normalize_multiline(expected)


class TestNHLIntegrationInvalidYear:
    """Represent TestNHLIntegrationInvalidYear."""

    def test_invalid_default_year_reverts_to_previous_year(self, monkeypatch, *args, **kwargs):
        """Return test invalid default year reverts to previous year."""
        monkeypatch.setattr(utils, "find_year_for_season", lambda _league: 2018)

        teams = Teams()

        for team in teams:
            assert team._year == "2017"
