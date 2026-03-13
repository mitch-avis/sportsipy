"""Provide utilities for test nba integration."""

import os

import pandas as pd
import pytest
from flexmock import flexmock

from sportsipy import utils
from sportsipy.nba.teams import Team, Teams

MONTH = 1
YEAR = 2021


def read_file(filename):
    """Return read file."""
    filepath = os.path.join(os.path.dirname(__file__), "nba_stats", filename)
    return open(f"{filepath}", encoding="utf8").read()


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


def mock_pyquery(url, timeout=None):
    """Return mock pyquery."""

    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

        def __call__(self, div):
            if div == "div#div_totals-team":
                return read_file(f"{YEAR}_team.html")
            return read_file(f"{YEAR}_opponent.html")

    html_contents = read_file(f"NBA_{YEAR}.html")
    return MockPQ(html_contents)


def _normalize_multiline(text: str) -> str:
    """Return a multi-line string with empty lines removed."""
    return "\n".join(line for line in text.splitlines() if line.strip())


class MockDateTime:
    """Represent MockDateTime."""

    def __init__(self, year, month):
        """Initialize the class instance."""
        self.year = year
        self.month = month


class TestNBAIntegration:
    """Represent TestNBAIntegration."""

    def setup_method(self, *args, **kwargs):
        """Return setup method."""
        self.results = {
            "rank": 27,
            "abbreviation": "DET",
            "name": "Detroit Pistons",
            "games_played": 72,
            "wins": 20,
            "losses": 52,
            "win_percentage": 0.278,
            "minutes_played": 17430,
            "field_goals": 2783,
            "field_goal_attempts": 6162,
            "field_goal_percentage": 0.452,
            "three_point_field_goals": 832,
            "three_point_field_goal_attempts": 2370,
            "three_point_field_goal_percentage": 0.351,
            "two_point_field_goals": 1951,
            "two_point_field_goal_attempts": 3792,
            "two_point_field_goal_percentage": 0.515,
            "free_throws": 1278,
            "free_throw_attempts": 1683,
            "free_throw_percentage": 0.759,
            "offensive_rebounds": 694,
            "defensive_rebounds": 2381,
            "total_rebounds": 3075,
            "assists": 1743,
            "steals": 531,
            "blocks": 371,
            "turnovers": 1075,
            "personal_fouls": 1477,
            "points": 7676,
            "opp_field_goals": 2980,
            "opp_field_goal_attempts": 6260,
            "opp_field_goal_percentage": 0.476,
            "opp_three_point_field_goals": 817,
            "opp_three_point_field_goal_attempts": 2260,
            "opp_three_point_field_goal_percentage": 0.362,
            "opp_two_point_field_goals": 2163,
            "opp_two_point_field_goal_attempts": 4000,
            "opp_two_point_field_goal_percentage": 0.541,
            "opp_free_throws": 1221,
            "opp_free_throw_attempts": 1607,
            "opp_free_throw_percentage": 0.760,
            "opp_offensive_rebounds": 717,
            "opp_defensive_rebounds": 2475,
            "opp_total_rebounds": 3192,
            "opp_assists": 1785,
            "opp_steals": 578,
            "opp_blocks": 419,
            "opp_turnovers": 1004,
            "opp_personal_fouls": 1469,
            "opp_points": 7998,
        }
        self.abbreviations = [
            "BOS",
            "CLE",
            "TOR",
            "WAS",
            "ATL",
            "MIL",
            "IND",
            "CHI",
            "MIA",
            "DET",
            "CHO",
            "NYK",
            "ORL",
            "PHI",
            "BRK",
            "GSW",
            "SAS",
            "HOU",
            "LAC",
            "UTA",
            "OKC",
            "MEM",
            "POR",
            "DEN",
            "NOP",
            "DAL",
            "SAC",
            "MIN",
            "LAL",
            "PHO",
        ]
        flexmock(utils).should_receive("todays_date").and_return(MockDateTime(YEAR, MONTH))

        self.teams = Teams()

    def test_nba_integration_returns_correct_number_of_teams(self):
        """Return test nba integration returns correct number of teams."""
        assert len(self.teams) == len(self.abbreviations)

    def test_nba_integration_returns_correct_attributes_for_team(self):
        """Return test nba integration returns correct attributes for team."""
        detroit = self.teams("DET")

        for attribute, value in self.results.items():
            assert getattr(detroit, attribute) == value

    def test_nba_integration_returns_correct_team_abbreviations(self):
        """Return test nba integration returns correct team abbreviations."""
        for team in self.teams:
            assert team.abbreviation in self.abbreviations

    def test_nba_integration_dataframe_returns_dataframe(self):
        """Return test nba integration dataframe returns dataframe."""
        df = pd.DataFrame([self.results], index=["DET"])

        detroit = self.teams("DET")
        # Pandas doesn't natively allow comparisons of DataFrames.
        # Concatenating the two DataFrames (the one generated during the test
        # and the expected one above) and dropping duplicate rows leaves only
        # the rows that are unique between the two frames. This allows a quick
        # check of the DataFrame to see if it is empty - if so, all rows are
        # duplicates, and they are equal.
        frames = [df, detroit.dataframe]
        df1 = pd.concat(frames).drop_duplicates(keep=False)

        assert df1.empty

    def test_nba_integration_all_teams_dataframe_returns_dataframe(self):
        """Return test nba integration all teams dataframe returns dataframe."""
        result = self.teams.dataframes.drop_duplicates(keep=False)

        assert len(result) == len(self.abbreviations)
        assert set(result.columns.values) == set(self.results.keys())

    def test_nba_invalid_team_name_raises_value_error(self):
        """Return test nba invalid team name raises value error."""
        with pytest.raises(ValueError):
            self.teams("INVALID_NAME")

    def test_nba_empty_page_returns_no_teams(self, *args, **kwargs):
        """Return test nba empty page returns no teams."""
        flexmock(utils).should_receive("no_data_found").once()
        flexmock(utils).should_receive("get_stats_table").and_return(None)

        teams = Teams()

        assert len(teams) == 0

    def test_pulling_team_directly(self, *args, **kwargs):
        """Return test pulling team directly."""
        detroit = Team("DET")

        for attribute, value in self.results.items():
            assert getattr(detroit, attribute) == value

    def test_team_string_representation(self):
        """Return test team string representation."""
        detroit = self.teams("DET")

        assert repr(detroit) == "Detroit Pistons (DET) - 2021"


class TestNBAIntegrationAllTeams:
    """Represent TestNBAIntegrationAllTeams."""

    def test_teams_string_representation(self, *args, **kwargs):
        """Return test teams string representation."""
        expected = """Milwaukee Bucks (MIL)

Brooklyn Nets (BRK)
Washington Wizards (WAS)
Utah Jazz (UTA)
Portland Trail Blazers (POR)
Indiana Pacers (IND)
Phoenix Suns (PHO)
Denver Nuggets (DEN)
New Orleans Pelicans (NOP)
Los Angeles Clippers (LAC)
Sacramento Kings (SAC)
Golden State Warriors (GSW)
Atlanta Hawks (ATL)
Philadelphia 76ers (PHI)
Memphis Grizzlies (MEM)
Boston Celtics (BOS)
Dallas Mavericks (DAL)
Minnesota Timberwolves (MIN)
Toronto Raptors (TOR)
San Antonio Spurs (SAS)
Chicago Bulls (CHI)
Los Angeles Lakers (LAL)
Charlotte Hornets (CHO)
Houston Rockets (HOU)
Miami Heat (MIA)
New York Knicks (NYK)
Detroit Pistons (DET)
Oklahoma City Thunder (OKC)
Orlando Magic (ORL)
Cleveland Cavaliers (CLE)"""

        teams = Teams()

        assert _normalize_multiline(repr(teams)) == _normalize_multiline(expected)


class TestNBAIntegrationInvalidDate:
    """Represent TestNBAIntegrationInvalidDate."""

    def test_invalid_default_year_reverts_to_previous_year(self, *args, **kwargs):
        """Return test invalid default year reverts to previous year."""
        flexmock(utils).should_receive("find_year_for_season").and_return(2022)

        teams = Teams()

        for team in teams:
            assert team._year == "2021"
