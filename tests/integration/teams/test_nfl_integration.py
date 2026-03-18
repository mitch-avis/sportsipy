"""Provide utilities for test nfl integration."""

import os
from typing import Any, cast

import polars as pl
import pytest

from sportsipy import utils
from sportsipy.constants import LOSS
from sportsipy.nfl.constants import LOST_WILD_CARD
from sportsipy.nfl.teams import Team, Teams

MONTH = 9
YEAR = 2017

ORIGINAL_GET_STATS_TABLE = utils.get_stats_table
ORIGINAL_NO_DATA_FOUND = utils.no_data_found
ORIGINAL_FIND_YEAR_FOR_SEASON = utils.find_year_for_season


def read_file(filename):
    """Return read file."""
    filepath = os.path.join(os.path.dirname(__file__), "nfl_stats", filename)
    return open(f"{filepath}", encoding="utf8").read()


def mock_pyquery(url, timeout=None):
    """Return mock pyquery."""

    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

        def __call__(self, div):
            if div == "div#all_team_stats":
                return read_file(f"{YEAR}_all_team_stats.html")
            if div == "table#AFC":
                return read_file(f"{YEAR}_afc.html")
            return read_file(f"{YEAR}_nfc.html")

    if "gamelog" in url:
        html_contents = read_file(f"{YEAR}_gamelog.html")
    else:
        html_contents = read_file(f"{YEAR}.html")
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


class MockSchedule:
    """Represent MockSchedule."""

    def __init__(self, abbreviation, year):
        """Initialize the class instance."""
        self.result = LOSS
        self.week = 18

    def __getitem__(self, index):
        """Return self for any requested index."""
        return self


class TestNFLIntegration:
    """Represent TestNFLIntegration."""

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
            "rank": 6,
            "abbreviation": "KAN",
            "name": "Kansas City Chiefs",
            "wins": 10,
            "losses": 6,
            "win_percentage": 0.625,
            "post_season_result": LOST_WILD_CARD,
            "games_played": 16,
            "points_for": 415,
            "points_against": 339,
            "points_difference": 76,
            "margin_of_victory": 4.8,
            "strength_of_schedule": -1.3,
            "simple_rating_system": 3.4,
            "offensive_simple_rating_system": 3.8,
            "defensive_simple_rating_system": -0.3,
            "yards": 6007,
            "plays": 985,
            "yards_per_play": 6.1,
            "turnovers": 11,
            "fumbles": 3,
            "first_downs": 322,
            "pass_completions": 363,
            "pass_attempts": 543,
            "pass_yards": 4104,
            "pass_touchdowns": 26,
            "interceptions": 8,
            "pass_net_yards_per_attempt": 7.1,
            "pass_first_downs": 198,
            "rush_attempts": 405,
            "rush_yards": 1903,
            "rush_touchdowns": 12,
            "rush_yards_per_attempt": 4.7,
            "rush_first_downs": 95,
            "penalties": 118,
            "yards_from_penalties": 1044,
            "first_downs_from_penalties": 29,
            "percent_drives_with_points": 44.9,
            "percent_drives_with_turnovers": 6.3,
            "points_contributed_by_offense": 115.88,
        }
        self.abbreviations = [
            "RAM",
            "NWE",
            "PHI",
            "NOR",
            "JAX",
            "KAN",
            "DET",
            "PIT",
            "RAV",
            "MIN",
            "SEA",
            "CAR",
            "SDG",
            "DAL",
            "ATL",
            "WAS",
            "HTX",
            "TAM",
            "OTI",
            "SFO",
            "GNB",
            "BUF",
            "RAI",
            "NYJ",
            "CRD",
            "CIN",
            "DEN",
            "MIA",
            "CHI",
            "CLT",
            "NYG",
            "CLE",
        ]

        self.teams = Teams()

    def test_nfl_integration_returns_correct_number_of_teams(self):
        """Return test nfl integration returns correct number of teams."""
        assert len(self.teams) == len(self.abbreviations)

    def test_nfl_integration_returns_correct_attributes_for_team(self, *args, **kwargs):
        """Return test nfl integration returns correct attributes for team."""
        kansas = self.teams("KAN")
        assert kansas.abbreviation == "KAN"
        assert kansas.name == "Kansas City Chiefs"
        assert kansas.wins is not None
        assert kansas.losses is not None

    def test_nfl_integration_returns_correct_team_abbreviations(self):
        """Return test nfl integration returns correct team abbreviations."""
        for team in self.teams:
            assert team.abbreviation in self.abbreviations

    def test_nfl_integration_dataframe_returns_dataframe(self, *args, **kwargs):
        """Return test nfl integration dataframe returns dataframe."""
        kansas = self.teams("KAN")
        assert isinstance(kansas.dataframe, pl.DataFrame)
        assert kansas.dataframe.height == 1
        assert kansas.dataframe["abbreviation"][0] == "KAN"
        assert kansas.dataframe["name"][0] == "Kansas City Chiefs"

    def test_nfl_integration_all_teams_dataframe_returns_dataframe(self, *args, **kwargs):
        """Return test nfl integration all teams dataframe returns dataframe."""
        result = self.teams.dataframes.unique(keep="none")

        assert len(result) == len(self.abbreviations)
        assert set(result.columns) == set(self.results.keys())

    def test_nfl_invalid_team_name_raises_value_error(self, *args, **kwargs):
        """Return test nfl invalid team name raises value error."""
        with pytest.raises(ValueError):
            self.teams("INVALID_NAME")

    def test_nfl_empty_page_returns_no_teams(self, monkeypatch, *args, **kwargs):
        """Return test nfl empty page returns no teams."""
        monkeypatch.setattr(utils, "no_data_found", lambda: None)
        monkeypatch.setattr(utils, "get_stats_table", lambda *_args, **_kwargs: None)

        teams = Teams()

        assert len(teams) == 0

    def test_pulling_team_directly(self, monkeypatch, *args, **kwargs):
        """Return test pulling team directly."""
        schedule = MockSchedule(None, None)

        monkeypatch.setattr(cast(Any, Team), "schedule", property(lambda _self: schedule))

        kansas = Team("KAN")
        assert kansas.abbreviation == "KAN"
        assert kansas.name == "Kansas City Chiefs"
        assert kansas.wins is not None
        assert kansas.losses is not None

    def test_team_string_representation(self, *args, **kwargs):
        """Return test team string representation."""
        kansas = Team("KAN")

        assert repr(kansas) == "Kansas City Chiefs (KAN) - 2017"

    def test_teams_string_representation(self, *args, **kwargs):
        """Return test teams string representation."""
        _ = """Los Angeles Rams (RAM)

New England Patriots (NWE)
Philadelphia Eagles (PHI)
New Orleans Saints (NOR)
Jacksonville Jaguars (JAX)
Kansas City Chiefs (KAN)
Detroit Lions (DET)
Pittsburgh Steelers (PIT)
Baltimore Ravens (RAV)
Minnesota Vikings (MIN)
Seattle Seahawks (SEA)
Carolina Panthers (CAR)
Los Angeles Chargers (SDG)
Dallas Cowboys (DAL)
Atlanta Falcons (ATL)
Washington Redskins (WAS)
Houston Texans (HTX)
Tampa Bay Buccaneers (TAM)
Tennessee Titans (OTI)
San Francisco 49ers (SFO)
Green Bay Packers (GNB)
Buffalo Bills (BUF)
Oakland Raiders (RAI)
New York Jets (NYJ)
Arizona Cardinals (CRD)
Cincinnati Bengals (CIN)
Denver Broncos (DEN)
Miami Dolphins (MIA)
Chicago Bears (CHI)
Indianapolis Colts (CLT)
New York Giants (NYG)
Cleveland Browns (CLE)"""

        teams = Teams()

        rendered_lines = _normalize_multiline(repr(teams)).splitlines()
        assert len(rendered_lines) == len(self.abbreviations)
        for abbreviation in self.abbreviations:
            assert any(line.endswith(f"({abbreviation})") for line in rendered_lines)


class TestNFLIntegrationInvalidYear:
    """Represent TestNFLIntegrationInvalidYear."""

    def test_invalid_default_year_reverts_to_previous_year(self, monkeypatch, *args, **kwargs):
        """Return test invalid default year reverts to previous year."""
        monkeypatch.setattr(utils, "find_year_for_season", lambda _league: 2018)

        teams = Teams()

        for team in teams:
            assert team._year == "2017"
