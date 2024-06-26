import os
from datetime import datetime

import mock
import pandas as pd
from flexmock import flexmock

from sportsipy import utils
from sportsipy.constants import HOME
from sportsipy.ncaab.boxscore import Boxscore, Boxscores
from sportsipy.ncaab.constants import BOXSCORES_URL

MONTH = 1
YEAR = 2020

BOXSCORE = "2020-01-22-19-louisville"


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), "ncaab", filename)
    return open(f"{filepath}", "r", encoding="utf8").read()


def mock_pyquery(url, timeout=None):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

        def __call__(self, div):
            return read_file("table.html")

    if url == BOXSCORES_URL % (MONTH, 5, YEAR):
        return MockPQ(read_file("boxscores-1-5-2020.html"))
    if url == BOXSCORES_URL % (MONTH, 6, YEAR):
        return MockPQ(read_file("boxscores-1-6-2020.html"))
    boxscore = read_file(f"{BOXSCORE}.html")
    return MockPQ(boxscore)


class MockDateTime:
    def __init__(self, year, month):
        self.year = year
        self.month = month


class TestNCAABBoxscore:
    @mock.patch("requests.get", side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            "date": "January 22, 2020",
            "location": "KFC Yum! Center, Louisville, Kentucky",
            "winner": HOME,
            "winning_name": "Louisville",
            "winning_abbr": "LOUISVILLE",
            "losing_name": "Georgia Tech",
            "losing_abbr": "GEORGIA-TECH",
            "pace": 66.2,
            "away_ranking": None,
            "away_win_percentage": 0.421,
            "away_wins": 8,
            "away_losses": 11,
            "away_minutes_played": 200,
            "away_field_goals": 22,
            "away_field_goal_attempts": 48,
            "away_field_goal_percentage": 0.458,
            "away_two_point_field_goals": 17,
            "away_two_point_field_goal_attempts": 31,
            "away_two_point_field_goal_percentage": 0.548,
            "away_three_point_field_goals": 5,
            "away_three_point_field_goal_attempts": 17,
            "away_three_point_field_goal_percentage": 0.294,
            "away_free_throws": 15,
            "away_free_throw_attempts": 20,
            "away_free_throw_percentage": 0.750,
            "away_offensive_rebounds": 7,
            "away_defensive_rebounds": 23,
            "away_total_rebounds": 30,
            "away_assists": 11,
            "away_steals": 4,
            "away_blocks": 4,
            "away_turnovers": 16,
            "away_personal_fouls": 18,
            "away_points": 64,
            "away_true_shooting_percentage": 0.557,
            "away_effective_field_goal_percentage": 0.510,
            "away_three_point_attempt_rate": 0.354,
            "away_free_throw_attempt_rate": 0.417,
            "away_offensive_rebound_percentage": 28.0,
            "away_defensive_rebound_percentage": 63.9,
            "away_total_rebound_percentage": 49.2,
            "away_assist_percentage": 50.0,
            "away_steal_percentage": 6.1,
            "away_block_percentage": 10.5,
            "away_turnover_percentage": 22.0,
            "away_offensive_rating": 97.0,
            "away_defensive_rating": 103.0,
            "home_ranking": 6,
            "home_win_percentage": 0.842,
            "home_wins": 16,
            "home_losses": 3,
            "home_minutes_played": 200,
            "home_field_goals": 24,
            "home_field_goal_attempts": 58,
            "home_field_goal_percentage": 0.414,
            "home_two_point_field_goals": 18,
            "home_two_point_field_goal_attempts": 38,
            "home_two_point_field_goal_percentage": 0.474,
            "home_three_point_field_goals": 6,
            "home_three_point_field_goal_attempts": 20,
            "home_three_point_field_goal_percentage": 0.300,
            "home_free_throws": 14,
            "home_free_throw_attempts": 23,
            "home_free_throw_percentage": 0.609,
            "home_offensive_rebounds": 13,
            "home_defensive_rebounds": 18,
            "home_total_rebounds": 31,
            "home_assists": 12,
            "home_steals": 9,
            "home_blocks": 3,
            "home_turnovers": 10,
            "home_personal_fouls": 17,
            "home_points": 68,
            "home_true_shooting_percentage": 0.493,
            "home_effective_field_goal_percentage": 0.466,
            "home_three_point_attempt_rate": 0.345,
            "home_free_throw_attempt_rate": 0.397,
            "home_offensive_rebound_percentage": 36.1,
            "home_defensive_rebound_percentage": 72.0,
            "home_total_rebound_percentage": 50.8,
            "home_assist_percentage": 50.0,
            "home_steal_percentage": 13.6,
            "home_block_percentage": 9.7,
            "home_turnover_percentage": 12.8,
            "home_offensive_rating": 103.0,
            "home_defensive_rating": 97.0,
        }
        flexmock(utils).should_receive("todays_date").and_return(MockDateTime(YEAR, MONTH))

        self.boxscore = Boxscore("2020-01-22-19-louisville")

    def test_ncaab_boxscore_returns_requested_boxscore(self):
        for attribute, value in self.results.items():
            assert getattr(self.boxscore, attribute) == value
        assert getattr(self.boxscore, "summary") == {
            # Box score is not parsed correctly
            "away": [],
            "home": [],
        }

    def test_invalid_url_yields_empty_class(self):
        flexmock(Boxscore).should_receive("_retrieve_html_page").and_return(None)

        boxscore = Boxscore(BOXSCORE)

        for key, value in boxscore.__dict__.items():
            if key == "_uri":
                continue
            assert value is None

    def test_ncaab_boxscore_dataframe_returns_dataframe_of_all_values(self):
        df = pd.DataFrame([self.results], index=[BOXSCORE])

        # Pandas doesn't natively allow comparisons of DataFrames.
        # Concatenating the two DataFrames (the one generated during the test
        # and the expected one above) and dropping duplicate rows leaves only
        # the rows that are unique between the two frames. This allows a quick
        # check of the DataFrame to see if it is empty - if so, all rows are
        # duplicates, and they are equal.
        frames = [df, self.boxscore.dataframe]
        df1 = pd.concat(frames).drop_duplicates(keep=False)

        assert df1.empty

    def test_ncaab_boxscore_players(self):
        assert len(self.boxscore.home_players) == 10
        assert len(self.boxscore.away_players) == 7

        for player in self.boxscore.home_players:
            assert not player.dataframe.empty
        for player in self.boxscore.away_players:
            assert not player.dataframe.empty

    def test_ncaab_boxscore_string_representation(self):
        expected = "Boxscore for Georgia Tech at Louisville (January 22, 2020)"

        assert repr(self.boxscore) == expected


class TestNCAABBoxscores:
    def setup_method(self):
        self.expected = {
            "1-5-2020": [
                {
                    "boxscore": "2020-01-05-13-michigan-state",
                    "away_name": "Michigan",
                    "away_abbr": "michigan",
                    "away_score": 69,
                    "away_rank": 12,
                    "home_name": "Michigan State",
                    "home_abbr": "michigan-state",
                    "home_score": 87,
                    "home_rank": 14,
                    "non_di": False,
                    "top_25": True,
                    "winning_name": "Michigan State",
                    "winning_abbr": "michigan-state",
                    "losing_name": "Michigan",
                    "losing_abbr": "michigan",
                },
                {
                    "boxscore": "2020-01-05-13-saint-josephs",
                    "away_name": "Dayton",
                    "away_abbr": "dayton",
                    "away_score": 80,
                    "away_rank": 20,
                    "home_name": "St. Joseph's",
                    "home_abbr": "saint-josephs",
                    "home_score": 67,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": True,
                    "winning_name": "Dayton",
                    "winning_abbr": "dayton",
                    "losing_name": "St. Joseph's",
                    "losing_abbr": "saint-josephs",
                },
                {
                    "boxscore": "2020-01-05-15-american",
                    "away_name": "Boston University",
                    "away_abbr": "boston-university",
                    "away_score": 63,
                    "away_rank": None,
                    "home_name": "American",
                    "home_abbr": "american",
                    "home_score": 67,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "American",
                    "winning_abbr": "american",
                    "losing_name": "Boston University",
                    "losing_abbr": "boston-university",
                },
                {
                    "boxscore": "2020-01-05-14-lafayette",
                    "away_name": "Bucknell",
                    "away_abbr": "bucknell",
                    "away_score": 78,
                    "away_rank": None,
                    "home_name": "Lafayette",
                    "home_abbr": "lafayette",
                    "home_score": 66,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "Bucknell",
                    "winning_abbr": "bucknell",
                    "losing_name": "Lafayette",
                    "losing_abbr": "lafayette",
                },
                {
                    "boxscore": "2020-01-05-14-duquesne",
                    "away_name": "Davidson",
                    "away_abbr": "davidson",
                    "away_score": 64,
                    "away_rank": None,
                    "home_name": "Duquesne",
                    "home_abbr": "duquesne",
                    "home_score": 71,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "Duquesne",
                    "winning_abbr": "duquesne",
                    "losing_name": "Davidson",
                    "losing_abbr": "davidson",
                },
                {
                    "boxscore": "2020-01-05-16-south-dakota",
                    "away_name": "Denver",
                    "away_abbr": "denver",
                    "away_score": 78,
                    "away_rank": None,
                    "home_name": "South Dakota",
                    "home_abbr": "south-dakota",
                    "home_score": 80,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "South Dakota",
                    "winning_abbr": "south-dakota",
                    "losing_name": "Denver",
                    "losing_abbr": "denver",
                },
                {
                    "boxscore": "2020-01-05-14-canisius",
                    "away_name": "Fairfield",
                    "away_abbr": "fairfield",
                    "away_score": 46,
                    "away_rank": None,
                    "home_name": "Canisius",
                    "home_abbr": "canisius",
                    "home_score": 42,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "Fairfield",
                    "winning_abbr": "fairfield",
                    "losing_name": "Canisius",
                    "losing_abbr": "canisius",
                },
                {
                    "boxscore": "2020-01-05-17-northwestern-state",
                    "away_name": "Houston Baptist",
                    "away_abbr": "houston-baptist",
                    "away_score": 79,
                    "away_rank": None,
                    "home_name": "Northwestern State",
                    "home_abbr": "northwestern-state",
                    "home_score": 106,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "Northwestern State",
                    "winning_abbr": "northwestern-state",
                    "losing_name": "Houston Baptist",
                    "losing_abbr": "houston-baptist",
                },
                {
                    "boxscore": "2020-01-05-14-milwaukee",
                    "away_name": "UIC",
                    "away_abbr": "illinois-chicago",
                    "away_score": 62,
                    "away_rank": None,
                    "home_name": "Milwaukee",
                    "home_abbr": "milwaukee",
                    "home_score": 64,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "Milwaukee",
                    "winning_abbr": "milwaukee",
                    "losing_name": "UIC",
                    "losing_abbr": "illinois-chicago",
                },
                {
                    "boxscore": "2020-01-05-14-monmouth",
                    "away_name": "Iona",
                    "away_abbr": "iona",
                    "away_score": 61,
                    "away_rank": None,
                    "home_name": "Monmouth",
                    "home_abbr": "monmouth",
                    "home_score": 73,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "Monmouth",
                    "winning_abbr": "monmouth",
                    "losing_name": "Iona",
                    "losing_abbr": "iona",
                },
                {
                    "boxscore": "2020-01-05-17-north-dakota",
                    "away_name": "Purdue-Fort Wayne",
                    "away_abbr": "ipfw",
                    "away_score": 69,
                    "away_rank": None,
                    "home_name": "North Dakota",
                    "home_abbr": "north-dakota",
                    "home_score": 83,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "North Dakota",
                    "winning_abbr": "north-dakota",
                    "losing_name": "Purdue-Fort Wayne",
                    "losing_abbr": "ipfw",
                },
                {
                    "boxscore": "2020-01-05-14-green-bay",
                    "away_name": "IUPUI",
                    "away_abbr": "iupui",
                    "away_score": 93,
                    "away_rank": None,
                    "home_name": "Green Bay",
                    "home_abbr": "green-bay",
                    "home_score": 78,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "IUPUI",
                    "winning_abbr": "iupui",
                    "losing_name": "Green Bay",
                    "losing_abbr": "green-bay",
                },
                {
                    "boxscore": "2020-01-05-14-fordham",
                    "away_name": "La Salle",
                    "away_abbr": "la-salle",
                    "away_score": 66,
                    "away_rank": None,
                    "home_name": "Fordham",
                    "home_abbr": "fordham",
                    "home_score": 60,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "La Salle",
                    "winning_abbr": "la-salle",
                    "losing_name": "Fordham",
                    "losing_abbr": "fordham",
                },
                {
                    "boxscore": "2020-01-05-14-lehigh",
                    "away_name": "Loyola (MD)",
                    "away_abbr": "loyola-md",
                    "away_score": 71,
                    "away_rank": None,
                    "home_name": "Lehigh",
                    "home_abbr": "lehigh",
                    "home_score": 78,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "Lehigh",
                    "winning_abbr": "lehigh",
                    "losing_name": "Loyola (MD)",
                    "losing_abbr": "loyola-md",
                },
                {
                    "boxscore": "2020-01-05-13-niagara",
                    "away_name": "Manhattan",
                    "away_abbr": "manhattan",
                    "away_score": 67,
                    "away_rank": None,
                    "home_name": "Niagara",
                    "home_abbr": "niagara",
                    "home_score": 62,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "Manhattan",
                    "winning_abbr": "manhattan",
                    "losing_name": "Niagara",
                    "losing_abbr": "niagara",
                },
                {
                    "boxscore": "2020-01-05-14-saint-peters",
                    "away_name": "Marist",
                    "away_abbr": "marist",
                    "away_score": 40,
                    "away_rank": None,
                    "home_name": "St. Peter's",
                    "home_abbr": "saint-peters",
                    "home_score": 66,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "St. Peter's",
                    "winning_abbr": "saint-peters",
                    "losing_name": "Marist",
                    "losing_abbr": "marist",
                },
                {
                    "boxscore": "2020-01-05-16-saint-louis",
                    "away_name": "UMass",
                    "away_abbr": "massachusetts",
                    "away_score": 80,
                    "away_rank": None,
                    "home_name": "Saint Louis",
                    "home_abbr": "saint-louis",
                    "home_score": 83,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "Saint Louis",
                    "winning_abbr": "saint-louis",
                    "losing_name": "UMass",
                    "losing_abbr": "massachusetts",
                },
                {
                    "boxscore": "2020-01-05-12-holy-cross",
                    "away_name": "Navy",
                    "away_abbr": "navy",
                    "away_score": 61,
                    "away_rank": None,
                    "home_name": "Holy Cross",
                    "home_abbr": "holy-cross",
                    "home_score": 63,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "Holy Cross",
                    "winning_abbr": "holy-cross",
                    "losing_name": "Navy",
                    "losing_abbr": "navy",
                },
                {
                    "boxscore": "2020-01-05-15-oakland",
                    "away_name": "Northern Kentucky",
                    "away_abbr": "northern-kentucky",
                    "away_score": 75,
                    "away_rank": None,
                    "home_name": "Oakland",
                    "home_abbr": "oakland",
                    "home_score": 64,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "Northern Kentucky",
                    "winning_abbr": "northern-kentucky",
                    "losing_name": "Oakland",
                    "losing_abbr": "oakland",
                },
                {
                    "boxscore": "2020-01-05-15-north-dakota-state",
                    "away_name": "Northland",
                    "away_abbr": "Northland",
                    "away_score": 43,
                    "away_rank": None,
                    "home_name": "North Dakota State",
                    "home_abbr": "north-dakota-state",
                    "home_score": 97,
                    "home_rank": None,
                    "non_di": True,
                    "top_25": False,
                    "winning_name": "North Dakota State",
                    "winning_abbr": "north-dakota-state",
                    "losing_name": "Northland",
                    "losing_abbr": "Northland",
                },
                {
                    "boxscore": "2020-01-05-19-minnesota",
                    "away_name": "Northwestern",
                    "away_abbr": "northwestern",
                    "away_score": 68,
                    "away_rank": None,
                    "home_name": "Minnesota",
                    "home_abbr": "minnesota",
                    "home_score": 77,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "Minnesota",
                    "winning_abbr": "minnesota",
                    "losing_name": "Northwestern",
                    "losing_abbr": "northwestern",
                },
                {
                    "boxscore": "2020-01-05-18-colorado",
                    "away_name": "Oregon State",
                    "away_abbr": "oregon-state",
                    "away_score": 76,
                    "away_rank": None,
                    "home_name": "Colorado",
                    "home_abbr": "colorado",
                    "home_score": 68,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "Oregon State",
                    "winning_abbr": "oregon-state",
                    "losing_name": "Colorado",
                    "losing_abbr": "colorado",
                },
                {
                    "boxscore": "2020-01-05-20-illinois",
                    "away_name": "Purdue",
                    "away_abbr": "purdue",
                    "away_score": 37,
                    "away_rank": None,
                    "home_name": "Illinois",
                    "home_abbr": "illinois",
                    "home_score": 63,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "Illinois",
                    "winning_abbr": "illinois",
                    "losing_name": "Purdue",
                    "losing_abbr": "purdue",
                },
                {
                    "boxscore": "2020-01-05-12-rhode-island",
                    "away_name": "Richmond",
                    "away_abbr": "richmond",
                    "away_score": 69,
                    "away_rank": None,
                    "home_name": "Rhode Island",
                    "home_abbr": "rhode-island",
                    "home_score": 61,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "Richmond",
                    "winning_abbr": "richmond",
                    "losing_name": "Rhode Island",
                    "losing_abbr": "rhode-island",
                },
                {
                    "boxscore": "2020-01-05-14-rider",
                    "away_name": "Siena",
                    "away_abbr": "siena",
                    "away_score": 77,
                    "away_rank": None,
                    "home_name": "Rider",
                    "home_abbr": "rider",
                    "home_score": 85,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "Rider",
                    "winning_abbr": "rider",
                    "losing_name": "Siena",
                    "losing_abbr": "siena",
                },
                {
                    "boxscore": "2020-01-05-22-washington",
                    "away_name": "USC",
                    "away_abbr": "southern-california",
                    "away_score": 40,
                    "away_rank": None,
                    "home_name": "Washington",
                    "home_abbr": "washington",
                    "home_score": 72,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "Washington",
                    "winning_abbr": "washington",
                    "losing_name": "USC",
                    "losing_abbr": "southern-california",
                },
                {
                    "boxscore": "2020-01-05-16-george-washington",
                    "away_name": "St. Bonaventure",
                    "away_abbr": "st-bonaventure",
                    "away_score": 71,
                    "away_rank": None,
                    "home_name": "George Washington",
                    "home_abbr": "george-washington",
                    "home_score": 66,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "St. Bonaventure",
                    "winning_abbr": "st-bonaventure",
                    "losing_name": "George Washington",
                    "losing_abbr": "george-washington",
                },
                {
                    "boxscore": "2020-01-05-16-xavier",
                    "away_name": "St. John's (NY)",
                    "away_abbr": "st-johns-ny",
                    "away_score": 67,
                    "away_rank": None,
                    "home_name": "Xavier",
                    "home_abbr": "xavier",
                    "home_score": 75,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "Xavier",
                    "winning_abbr": "xavier",
                    "losing_name": "St. John's (NY)",
                    "losing_abbr": "st-johns-ny",
                },
                {
                    "boxscore": "2020-01-05-13-maine",
                    "away_name": "Stony Brook",
                    "away_abbr": "stony-brook",
                    "away_score": 73,
                    "away_rank": None,
                    "home_name": "Maine",
                    "home_abbr": "maine",
                    "home_score": 52,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "Stony Brook",
                    "winning_abbr": "stony-brook",
                    "losing_name": "Maine",
                    "losing_abbr": "maine",
                },
                {
                    "boxscore": "2020-01-05-12-george-mason",
                    "away_name": "VCU",
                    "away_abbr": "virginia-commonwealth",
                    "away_score": 72,
                    "away_rank": None,
                    "home_name": "George Mason",
                    "home_abbr": "george-mason",
                    "home_score": 59,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "VCU",
                    "winning_abbr": "virginia-commonwealth",
                    "losing_name": "George Mason",
                    "losing_abbr": "george-mason",
                },
                {
                    "boxscore": "2020-01-05-13-detroit-mercy",
                    "away_name": "Wright State",
                    "away_abbr": "wright-state",
                    "away_score": 70,
                    "away_rank": None,
                    "home_name": "Detroit",
                    "home_abbr": "detroit-mercy",
                    "home_score": 69,
                    "home_rank": None,
                    "non_di": False,
                    "top_25": False,
                    "winning_name": "Wright State",
                    "winning_abbr": "wright-state",
                    "losing_name": "Detroit",
                    "losing_abbr": "detroit-mercy",
                },
            ]
        }

    @mock.patch("requests.get", side_effect=mock_pyquery)
    def test_boxscores_search(self, *args, **kwargs):
        result = Boxscores(datetime(2020, 1, 5)).games

        assert result == self.expected

    @mock.patch("requests.get", side_effect=mock_pyquery)
    def test_boxscores_search_invalid_end(self, *args, **kwargs):
        result = Boxscores(datetime(2020, 1, 5), datetime(2020, 1, 4)).games

        assert result == self.expected

    @mock.patch("requests.get", side_effect=mock_pyquery)
    def test_boxscores_search_string_representation(self, *args, **kwargs):
        result = Boxscores(datetime(2020, 1, 5))

        assert repr(result) == "NCAAB games for 1-5-2020"
