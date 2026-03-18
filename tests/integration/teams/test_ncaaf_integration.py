"""Provide utilities for test ncaaf integration."""

import os

import polars as pl
import pytest

from sportsipy import utils
from sportsipy.ncaaf.conferences import Conferences
from sportsipy.ncaaf.constants import (
    DEFENSIVE_STATS_URL,
    OFFENSIVE_STATS_URL,
    SEASON_PAGE_URL,
)
from sportsipy.ncaaf.teams import Team, Teams

MONTH = 9
YEAR = 2017

ORIGINAL_GET_STATS_TABLE = utils.get_stats_table
ORIGINAL_NO_DATA_FOUND = utils.no_data_found
ORIGINAL_FIND_YEAR_FOR_SEASON = utils.find_year_for_season


def read_file(filename):
    """Return read file."""
    filepath = os.path.join(os.path.dirname(__file__), "ncaaf_stats", filename)
    return open(f"{filepath}", encoding="utf8").read()


def mock_pyquery(url, timeout=None):
    """Return mock pyquery."""

    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

        def __call__(self, div):
            if div == "table#offense":
                return read_file(f"{YEAR}-team-offense_offense.html")
            if div == "table#defense":
                return read_file(f"{YEAR}-team-defense_defense.html")
            return read_file(f"{YEAR}-standings_standings.html")

    offensive_contents = read_file(f"{YEAR}-team-offense.html")
    defensive_contents = read_file(f"{YEAR}-team-defense.html")
    standings_contents = read_file(f"{YEAR}-standings.html")
    if url == OFFENSIVE_STATS_URL % YEAR:
        return MockPQ(offensive_contents)
    if url == DEFENSIVE_STATS_URL % YEAR:
        return MockPQ(defensive_contents)
    if url == SEASON_PAGE_URL % YEAR:
        return MockPQ(standings_contents)


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


class TestNCAAFIntegration:
    """Represent TestNCAAFIntegration."""

    def setup_method(self, *args, **kwargs):
        """Return setup method."""
        self.results = {
            "conference": "big-ten",
            "abbreviation": "PURDUE",
            "name": "Purdue",
            "games": 13,
            "wins": 7,
            "losses": 6,
            "win_percentage": 0.538,
            "conference_wins": 4,
            "conference_losses": 5,
            "conference_win_percentage": 0.444,
            "points_per_game": 25.2,
            "points_against_per_game": 20.5,
            "strength_of_schedule": 6.21,
            "simple_rating_system": 9.74,
            "pass_completions": 22.5,
            "pass_attempts": 37.8,
            "pass_completion_percentage": 59.5,
            "pass_yards": 251.5,
            "interceptions": 0.8,
            "pass_touchdowns": 2.1,
            "rush_attempts": 34.4,
            "rush_yards": 151.5,
            "rush_yards_per_attempt": 4.4,
            "rush_touchdowns": 0.9,
            "plays": 72.2,
            "yards": 403.1,
            "turnovers": 1.3,
            "fumbles_lost": 0.5,
            "yards_per_play": 5.6,
            "pass_first_downs": 11.1,
            "rush_first_downs": 8.8,
            "first_downs_from_penalties": 1.8,
            "first_downs": 21.7,
            "penalties": 5.9,
            "yards_from_penalties": 50.6,
            "opponents_pass_completions": 19.1,
            "opponents_pass_attempts": 33.6,
            "opponents_pass_completion_percentage": 56.8,
            "opponents_pass_yards": 242.5,
            "opponents_interceptions": 0.8,
            "opponents_pass_touchdowns": 1.6,
            "opponents_rush_attempts": 37.4,
            "opponents_rush_yards": 133.2,
            "opponents_rush_yards_per_attempt": 3.6,
            "opponents_rush_touchdowns": 0.8,
            "opponents_plays": 71.0,
            "opponents_yards": 375.8,
            "opponents_turnovers": 1.6,
            "opponents_fumbles_lost": 0.8,
            "opponents_yards_per_play": 5.3,
            "opponents_pass_first_downs": 10.6,
            "opponents_rush_first_downs": 6.8,
            "opponents_first_downs_from_penalties": 1.8,
            "opponents_first_downs": 19.2,
            "opponents_penalties": 6.9,
            "opponents_yards_from_penalties": 59.8,
        }
        self.schools = [
            "UCF",
            "Memphis",
            "Oklahoma",
            "Oklahoma State",
            "Arizona",
            "Ohio State",
            "Penn State",
            "Florida Atlantic",
            "Ohio",
            "South Florida",
            "Louisville",
            "Arkansas State",
            "SMU",
            "Missouri",
            "Alabama",
            "Toledo",
            "Washington",
            "Oregon",
            "North Texas",
            "Georgia",
            "Wake Forest",
            "West Virginia",
            "Texas Tech",
            "Notre Dame",
            "Auburn",
            "Louisiana-Monroe",
            "Western Michigan",
            "Wisconsin",
            "Texas Christian",
            "Appalachian State",
            "Colorado State",
            "Clemson",
            "Ole Miss",
            "Texas A&M",
            "USC",
            "Boise State",
            "UCLA",
            "Stanford",
            "Kansas State",
            "North Carolina State",
            "Mississippi State",
            "Arizona State",
            "Troy",
            "Air Force",
            "San Diego State",
            "Army",
            "Massachusetts",
            "Louisiana Tech",
            "Navy",
            "Washington State",
            "Utah State",
            "Texas",
            "Utah",
            "New Mexico State",
            "Tulsa",
            "Iowa State",
            "Northwestern",
            "Southern Mississippi",
            "Miami (FL)",
            "Northern Illinois",
            "Arkansas",
            "Nevada-Las Vegas",
            "Buffalo",
            "Central Michigan",
            "Houston",
            "Iowa",
            "Louisiana",
            "Nevada",
            "Virginia Tech",
            "Georgia Tech",
            "California",
            "Florida State",
            "UAB",
            "Tulane",
            "Syracuse",
            "LSU",
            "Fresno State",
            "Indiana",
            "Marshall",
            "Duke",
            "Colorado",
            "Eastern Michigan",
            "North Carolina",
            "Nebraska",
            "Boston College",
            "Florida International",
            "Kentucky",
            "Middle Tennessee State",
            "Western Kentucky",
            "Bowling Green State",
            "Michigan",
            "Purdue",
            "Temple",
            "East Carolina",
            "Vanderbilt",
            "Michigan State",
            "Miami (OH)",
            "Baylor",
            "South Carolina",
            "Maryland",
            "Pitt",
            "Coastal Carolina",
            "Connecticut",
            "UTSA",
            "Wyoming",
            "Hawaii",
            "Virginia",
            "Akron",
            "Florida",
            "Minnesota",
            "Cincinnati",
            "Idaho",
            "Georgia Southern",
            "New Mexico",
            "Old Dominion",
            "Oregon State",
            "Georgia State",
            "South Alabama",
            "Tennessee",
            "Kansas",
            "Rutgers",
            "Ball State",
            "Texas State",
            "Brigham Young",
            "Rice",
            "San Jose State",
            "Illinois",
            "Charlotte",
            "Kent State",
            "UTEP",
        ]

        team_conference = {
            "florida-state": "acc",
            "boston-college": "acc",
            "clemson": "acc",
            "north-carolina-state": "acc",
            "syracuse": "acc",
            "wake-forest": "acc",
            "louisville": "acc",
            "virginia-tech": "acc",
            "duke": "acc",
            "georgia-tech": "acc",
            "pittsburgh": "acc",
            "virginia": "acc",
            "miami-fl": "acc",
            "north-carolina": "acc",
            "florida": "sec",
            "georgia": "sec",
            "kentucky": "sec",
            "missouri": "sec",
            "south-carolina": "sec",
            "vanderbilt": "sec",
            "tennessee": "sec",
            "alabama": "sec",
            "arkansas": "sec",
            "auburn": "sec",
            "louisiana-state": "sec",
            "mississippi-state": "sec",
            "mississippi": "sec",
            "texas-am": "sec",
            "buffalo": "mac",
            "ohio": "mac",
            "bowling-green-state": "mac",
            "kent-state": "mac",
            "miami-oh": "mac",
            "akron": "mac",
            "ball-state": "mac",
            "eastern-michigan": "mac",
            "toledo": "mac",
            "central-michigan": "mac",
            "northern-illinois": "mac",
            "western-michigan": "mac",
            "georgia-southern": "sun-belt",
            "appalachian-state": "sun-belt",
            "coastal-carolina": "sun-belt",
            "arkansas-state": "sun-belt",
            "georgia-state": "sun-belt",
            "louisiana-lafayette": "sun-belt",
            "louisiana-monroe": "sun-belt",
            "south-alabama": "sun-belt",
            "texas-state": "sun-belt",
            "troy": "sun-belt",
            "idaho": "sun-belt",
            "baylor": "big-12",
            "kansas-state": "big-12",
            "oklahoma": "big-12",
            "oklahoma-state": "big-12",
            "texas-christian": "big-12",
            "west-virginia": "big-12",
            "kansas": "big-12",
            "texas": "big-12",
            "texas-tech": "big-12",
            "iowa-state": "big-12",
            "colorado-state": "mwc",
            "air-force": "mwc",
            "boise-state": "mwc",
            "new-mexico": "mwc",
            "wyoming": "mwc",
            "utah-state": "mwc",
            "hawaii": "mwc",
            "fresno-state": "mwc",
            "nevada": "mwc",
            "nevada-las-vegas": "mwc",
            "san-diego-state": "mwc",
            "san-jose-state": "mwc",
            "california": "pac-12",
            "oregon": "pac-12",
            "stanford": "pac-12",
            "washington-state": "pac-12",
            "oregon-state": "pac-12",
            "washington": "pac-12",
            "arizona-state": "pac-12",
            "colorado": "pac-12",
            "southern-california": "pac-12",
            "utah": "pac-12",
            "arizona": "pac-12",
            "ucla": "pac-12",
            "central-florida": "american",
            "connecticut": "american",
            "cincinnati": "american",
            "south-florida": "american",
            "east-carolina": "american",
            "temple": "american",
            "houston": "american",
            "memphis": "american",
            "tulsa": "american",
            "navy": "american",
            "southern-methodist": "american",
            "tulane": "american",
            "charlotte": "cusa",
            "marshall": "cusa",
            "florida-atlantic": "cusa",
            "florida-international": "cusa",
            "middle-tennessee-state": "cusa",
            "old-dominion": "cusa",
            "western-kentucky": "cusa",
            "louisiana-tech": "cusa",
            "north-texas": "cusa",
            "southern-mississippi": "cusa",
            "alabama-birmingham": "cusa",
            "rice": "cusa",
            "texas-el-paso": "cusa",
            "texas-san-antonio": "cusa",
            "liberty": "independent",
            "massachusetts": "independent",
            "new-mexico-state": "independent",
            "brigham-young": "independent",
            "notre-dame": "independent",
            "army": "independent",
            "indiana": "big-ten",
            "maryland": "big-ten",
            "michigan-state": "big-ten",
            "ohio-state": "big-ten",
            "penn-state": "big-ten",
            "rutgers": "big-ten",
            "michigan": "big-ten",
            "northwestern": "big-ten",
            "purdue": "big-ten",
            "illinois": "big-ten",
            "iowa": "big-ten",
            "minnesota": "big-ten",
            "wisconsin": "big-ten",
            "nebraska": "big-ten",
        }
        self.team_conference = team_conference

    @pytest.fixture(autouse=True)
    def _setup_default_mocks(self, monkeypatch):
        """Patch conference/date lookups for deterministic integration tests."""
        monkeypatch.setattr(utils, "get_stats_table", ORIGINAL_GET_STATS_TABLE)
        monkeypatch.setattr(utils, "no_data_found", ORIGINAL_NO_DATA_FOUND)
        monkeypatch.setattr(utils, "find_year_for_season", ORIGINAL_FIND_YEAR_FOR_SEASON)
        monkeypatch.setattr(utils, "todays_date", lambda: MockDateTime(YEAR, MONTH))
        monkeypatch.setattr(Conferences, "_find_conferences", lambda *_args, **_kwargs: None)
        monkeypatch.setattr(Conferences, "team_conference", self.team_conference)
        self.teams = Teams()

    def test_ncaaf_integration_returns_correct_number_of_teams(self):
        """Return test ncaaf integration returns correct number of teams."""
        assert len(self.teams) == len(self.schools)

    def test_ncaaf_integration_returns_correct_attributes_for_team(self):
        """Return test ncaaf integration returns correct attributes for team."""
        purdue = self.teams("PURDUE")

        for attribute, value in self.results.items():
            assert getattr(purdue, attribute) == value

    def test_ncaaf_integration_returns_correct_team_abbreviations(self):
        """Return test ncaaf integration returns correct team abbreviations."""
        for team in self.teams:
            assert isinstance(team.name, str)
            assert isinstance(team.abbreviation, str)
            assert team.abbreviation

    def test_ncaaf_integration_dataframe_returns_dataframe(self):
        """Return test ncaaf integration dataframe returns dataframe."""
        df = pl.DataFrame([self.results])

        purdue = self.teams("PURDUE")
        # Polars doesn't natively allow comparisons of DataFrames.
        # Concatenating the two DataFrames (the one generated during the test
        # and the expected one above) and dropping duplicate rows leaves only
        # the rows that are unique between the two frames. This allows a quick
        # check of the DataFrame to see if it is empty - if so, all rows are
        # duplicates, and they are equal.
        df1 = pl.concat([df, purdue.dataframe.select(df.columns)]).unique(keep="none")

        assert df1.is_empty()

    def test_ncaaf_integration_all_teams_dataframe_returns_dataframe(self):
        """Return test ncaaf integration all teams dataframe returns dataframe."""
        result = self.teams.dataframes.unique(keep="none")

        assert len(result) == len(self.schools)
        assert set(result.columns) == set(self.results.keys())

    def test_ncaaf_invalid_team_name_raises_value_error(self):
        """Return test ncaaf invalid team name raises value error."""
        with pytest.raises(ValueError):
            self.teams("INVALID_NAME")

    def test_ncaaf_empty_page_returns_no_teams(self, monkeypatch, *args, **kwargs):
        """Return test ncaaf empty page returns no teams."""
        monkeypatch.setattr(utils, "no_data_found", lambda: None)
        monkeypatch.setattr(utils, "get_stats_table", lambda *_args, **_kwargs: None)

        teams = Teams()

        assert len(teams) == 0

    def test_pulling_team_directly(self, *args, **kwargs):
        """Return test pulling team directly."""
        purdue = Team("PURDUE")

        for attribute, value in self.results.items():
            assert getattr(purdue, attribute) == value

    def test_team_string_representation(self, *args, **kwargs):
        """Return test team string representation."""
        purdue = Team("PURDUE")

        assert repr(purdue) == "Purdue (PURDUE) - 2017"

    def test_teams_string_representation(self, *args, **kwargs):
        """Return test teams string representation."""
        teams = Teams()
        teams_repr = _normalize_multiline(repr(teams))

        assert "Clemson (CLEMSON)" in teams_repr
        assert "Purdue (PURDUE)" in teams_repr
        assert "Texas State (TEXAS-STATE)" in teams_repr


class TestNCAAFIntegrationInvalidYear:
    """Represent TestNCAAFIntegrationInvalidYear."""

    def test_invalid_default_year_reverts_to_previous_year(self, monkeypatch, *args, **kwargs):
        """Return test invalid default year reverts to previous year."""
        team_conference = {
            "florida-state": "acc",
            "boston-college": "acc",
            "clemson": "acc",
            "north-carolina-state": "acc",
            "syracuse": "acc",
            "wake-forest": "acc",
            "louisville": "acc",
            "virginia-tech": "acc",
            "duke": "acc",
            "georgia-tech": "acc",
            "pittsburgh": "acc",
            "virginia": "acc",
            "miami-fl": "acc",
            "north-carolina": "acc",
            "florida": "sec",
            "georgia": "sec",
            "kentucky": "sec",
            "missouri": "sec",
            "south-carolina": "sec",
            "vanderbilt": "sec",
            "tennessee": "sec",
            "alabama": "sec",
            "arkansas": "sec",
            "auburn": "sec",
            "louisiana-state": "sec",
            "mississippi-state": "sec",
            "mississippi": "sec",
            "texas-am": "sec",
            "buffalo": "mac",
            "ohio": "mac",
            "bowling-green-state": "mac",
            "kent-state": "mac",
            "miami-oh": "mac",
            "akron": "mac",
            "ball-state": "mac",
            "eastern-michigan": "mac",
            "toledo": "mac",
            "central-michigan": "mac",
            "northern-illinois": "mac",
            "western-michigan": "mac",
            "georgia-southern": "sun-belt",
            "appalachian-state": "sun-belt",
            "coastal-carolina": "sun-belt",
            "arkansas-state": "sun-belt",
            "georgia-state": "sun-belt",
            "louisiana-lafayette": "sun-belt",
            "louisiana-monroe": "sun-belt",
            "south-alabama": "sun-belt",
            "texas-state": "sun-belt",
            "troy": "sun-belt",
            "idaho": "sun-belt",
            "baylor": "big-12",
            "kansas-state": "big-12",
            "oklahoma": "big-12",
            "oklahoma-state": "big-12",
            "texas-christian": "big-12",
            "west-virginia": "big-12",
            "kansas": "big-12",
            "texas": "big-12",
            "texas-tech": "big-12",
            "iowa-state": "big-12",
            "colorado-state": "mwc",
            "air-force": "mwc",
            "boise-state": "mwc",
            "new-mexico": "mwc",
            "wyoming": "mwc",
            "utah-state": "mwc",
            "hawaii": "mwc",
            "fresno-state": "mwc",
            "nevada": "mwc",
            "nevada-las-vegas": "mwc",
            "san-diego-state": "mwc",
            "san-jose-state": "mwc",
            "california": "pac-12",
            "oregon": "pac-12",
            "stanford": "pac-12",
            "washington-state": "pac-12",
            "oregon-state": "pac-12",
            "washington": "pac-12",
            "arizona-state": "pac-12",
            "colorado": "pac-12",
            "southern-california": "pac-12",
            "utah": "pac-12",
            "arizona": "pac-12",
            "ucla": "pac-12",
            "central-florida": "american",
            "connecticut": "american",
            "cincinnati": "american",
            "south-florida": "american",
            "east-carolina": "american",
            "temple": "american",
            "houston": "american",
            "memphis": "american",
            "tulsa": "american",
            "navy": "american",
            "southern-methodist": "american",
            "tulane": "american",
            "charlotte": "cusa",
            "marshall": "cusa",
            "florida-atlantic": "cusa",
            "florida-international": "cusa",
            "middle-tennessee-state": "cusa",
            "old-dominion": "cusa",
            "western-kentucky": "cusa",
            "louisiana-tech": "cusa",
            "north-texas": "cusa",
            "southern-mississippi": "cusa",
            "alabama-birmingham": "cusa",
            "rice": "cusa",
            "texas-el-paso": "cusa",
            "texas-san-antonio": "cusa",
            "liberty": "independent",
            "massachusetts": "independent",
            "new-mexico-state": "independent",
            "brigham-young": "independent",
            "notre-dame": "independent",
            "army": "independent",
            "indiana": "big-ten",
            "maryland": "big-ten",
            "michigan-state": "big-ten",
            "ohio-state": "big-ten",
            "penn-state": "big-ten",
            "rutgers": "big-ten",
            "michigan": "big-ten",
            "northwestern": "big-ten",
            "purdue": "big-ten",
            "illinois": "big-ten",
            "iowa": "big-ten",
            "minnesota": "big-ten",
            "wisconsin": "big-ten",
            "nebraska": "big-ten",
        }

        monkeypatch.setattr(Conferences, "_find_conferences", lambda *_args, **_kwargs: None)
        monkeypatch.setattr(Conferences, "team_conference", team_conference)
        monkeypatch.setattr(utils, "find_year_for_season", lambda _league: 2018)

        teams = Teams()

        for team in teams:
            assert team._year == "2017"


class TestNCAAFIntegrationInvalidConference:
    """Represent TestNCAAFIntegrationInvalidConference."""

    def test_invalid_conference_returns_none(self, monkeypatch, *args, **kwargs):
        """Return test invalid conference returns none."""
        team_conference = {
            "florida-state": "acc",
            "boston-college": "acc",
            "clemson": "acc",
            "north-carolina-state": "acc",
            "syracuse": "acc",
            "wake-forest": "acc",
            "louisville": "acc",
            "virginia-tech": "acc",
            "duke": "acc",
            "georgia-tech": "acc",
            "pittsburgh": "acc",
            "virginia": "acc",
            "miami-fl": "acc",
            "north-carolina": "acc",
            "florida": "sec",
            "georgia": "sec",
            "kentucky": "sec",
            "missouri": "sec",
            "south-carolina": "sec",
            "vanderbilt": "sec",
            "tennessee": "sec",
            "alabama": "sec",
            "arkansas": "sec",
            "auburn": "sec",
            "louisiana-state": "sec",
            "mississippi-state": "sec",
            "mississippi": "sec",
            "texas-am": "sec",
            "buffalo": "mac",
            "ohio": "mac",
            "bowling-green-state": "mac",
            "kent-state": "mac",
            "miami-oh": "mac",
            "akron": "mac",
            "ball-state": "mac",
            "eastern-michigan": "mac",
            "toledo": "mac",
            "central-michigan": "mac",
            "northern-illinois": "mac",
            "western-michigan": "mac",
            "georgia-southern": "sun-belt",
            "appalachian-state": "sun-belt",
            "coastal-carolina": "sun-belt",
            "arkansas-state": "sun-belt",
            "georgia-state": "sun-belt",
            "louisiana-lafayette": "sun-belt",
            "louisiana-monroe": "sun-belt",
            "south-alabama": "sun-belt",
            "texas-state": "sun-belt",
            "troy": "sun-belt",
            "idaho": "sun-belt",
            "baylor": "big-12",
            "kansas-state": "big-12",
            "oklahoma": "big-12",
            "oklahoma-state": "big-12",
            "texas-christian": "big-12",
            "west-virginia": "big-12",
            "kansas": "big-12",
            "texas": "big-12",
            "texas-tech": "big-12",
            "iowa-state": "big-12",
            "colorado-state": "mwc",
            "air-force": "mwc",
            "boise-state": "mwc",
            "new-mexico": "mwc",
            "wyoming": "mwc",
            "utah-state": "mwc",
            "hawaii": "mwc",
            "fresno-state": "mwc",
            "nevada": "mwc",
            "nevada-las-vegas": "mwc",
            "san-diego-state": "mwc",
            "san-jose-state": "mwc",
            "california": "pac-12",
            "oregon": "pac-12",
            "stanford": "pac-12",
            "washington-state": "pac-12",
            "oregon-state": "pac-12",
            "washington": "pac-12",
            "arizona-state": "pac-12",
            "colorado": "pac-12",
            "southern-california": "pac-12",
            "utah": "pac-12",
            "arizona": "pac-12",
            "ucla": "pac-12",
            "central-florida": "american",
            "connecticut": "american",
            "cincinnati": "american",
            "south-florida": "american",
            "east-carolina": "american",
            "temple": "american",
            "houston": "american",
            "memphis": "american",
            "tulsa": "american",
            "navy": "american",
            "southern-methodist": "american",
            "tulane": "american",
            "charlotte": "cusa",
            "marshall": "cusa",
            "florida-atlantic": "cusa",
            "florida-international": "cusa",
            "middle-tennessee-state": "cusa",
            "old-dominion": "cusa",
            "western-kentucky": "cusa",
            "louisiana-tech": "cusa",
            "north-texas": "cusa",
            "southern-mississippi": "cusa",
            "alabama-birmingham": "cusa",
            "rice": "cusa",
            "texas-el-paso": "cusa",
            "texas-san-antonio": "cusa",
            "liberty": "independent",
            "massachusetts": "independent",
            "new-mexico-state": "independent",
            "brigham-young": "independent",
            "notre-dame": "independent",
            "army": "independent",
        }

        monkeypatch.setattr(utils, "todays_date", lambda: MockDateTime(YEAR, MONTH))
        monkeypatch.setattr(Conferences, "_find_conferences", lambda *_args, **_kwargs: None)
        monkeypatch.setattr(Conferences, "team_conference", team_conference)

        big_ten_schools = [
            "indiana",
            "maryland",
            "michigan-state",
            "ohio-state",
            "penn-state",
            "rutgers",
            "michigan",
            "northwestern",
            "purdue",
            "illinois",
            "iowa",
            "minnesota",
            "wisconsin",
            "nebraska",
        ]

        teams = Teams()

        for team in big_ten_schools:
            assert teams(team).conference is None
