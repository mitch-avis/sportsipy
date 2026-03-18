"""Provide utilities for test ncaab roster."""

import os
from typing import Any, cast
from unittest import mock

from sportsipy.ncaab.roster import Player

YEAR = 2018


def _normalize_multiline(text: str) -> str:
    """Return a multi-line string with empty lines removed."""
    return "\n".join(line for line in text.splitlines() if line.strip())


def read_file(filename):
    """Return read file."""
    filepath = os.path.join(os.path.dirname(__file__), "ncaab", filename)
    return open(f"{filepath}.html", encoding="utf8").read()


def mock_pyquery(url, timeout=None):
    """Return mock pyquery."""

    class MockPQ:
        def __init__(self, html_contents, status=200):
            self.url = url
            self.reason = "Bad URL"  # Used when throwing HTTPErrors
            self.headers = {}  # Used when throwing HTTPErrors
            self.status_code = status
            self.html_contents = html_contents
            self.text = html_contents

    if "purdue" in url:
        mock_pq = MockPQ(read_file("2018"))
    elif "isaac-haas-1" in url:
        mock_pq = MockPQ(read_file("isaac-haas-1"))
    elif "vince-edwards-2" in url:
        mock_pq = MockPQ(read_file("vince-edwards-2"))
    elif "bad" in url:
        mock_pq = MockPQ(None, 404)
    else:
        mock_pq = MockPQ(read_file("carsen-edwards-1"))
    return mock_pq


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


class TestNCAABPlayer:
    """Represent TestNCAABPlayer."""

    def setup_method(self, *args, **kwargs):
        """Return setup method."""
        self.results_career = {
            "assist_percentage": 17.3,
            "assists": 166,
            "block_percentage": 0.6,
            "blocks": 11,
            "box_plus_minus": 6.1,
            "conference": "",
            "defensive_box_plus_minus": 1.9,
            "defensive_rebound_percentage": 11.8,
            "defensive_rebounds": 206,
            "defensive_win_shares": 3.5,
            "effective_field_goal_percentage": 0.515,
            "field_goal_attempts": 835,
            "field_goal_percentage": 0.428,
            "field_goals": 357,
            "free_throw_attempt_rate": 0.279,
            "free_throw_attempts": 233,
            "free_throw_percentage": 0.798,
            "free_throws": 186,
            "games_played": 72,
            "games_started": 58,
            "height": "6-1",
            "minutes_played": 1905,
            "name": "Carsen Edwards",
            "offensive_box_plus_minus": 4.2,
            "offensive_rebound_percentage": 1.8,
            "offensive_rebounds": 27,
            "offensive_win_shares": 4.4,
            "personal_fouls": 133,
            "player_efficiency_rating": 19.9,
            "points": 1046,
            "points_produced": 961,
            "position": "Guard",
            "season": "Career",
            "steal_percentage": 2.4,
            "steals": 78,
            "team_abbreviation": "purdue",
            "three_point_attempt_rate": 0.459,
            "three_point_attempts": 383,
            "three_point_percentage": 0.381,
            "three_pointers": 146,
            "total_rebound_percentage": 7.2,
            "total_rebounds": 233,
            "true_shooting_percentage": 0.553,
            "turnover_percentage": 11.9,
            "turnovers": 128,
            "two_point_attempts": 452,
            "two_point_percentage": 0.467,
            "two_pointers": 211,
            "usage_percentage": 28.9,
            "weight": 190,
            "win_shares": 8.0,
            "win_shares_per_40_minutes": 0.167,
        }

        self.results_2018 = {
            "assist_percentage": 19.5,
            "assists": 104,
            "block_percentage": 0.8,
            "blocks": 8,
            "box_plus_minus": 9.0,
            "conference": "big-ten",
            "defensive_box_plus_minus": 1.5,
            "defensive_rebound_percentage": 12.9,
            "defensive_rebounds": 129,
            "defensive_win_shares": 2.0,
            "effective_field_goal_percentage": 0.555,
            "field_goal_attempts": 500,
            "field_goal_percentage": 0.458,
            "field_goals": 229,
            "free_throw_attempt_rate": 0.318,
            "free_throw_attempts": 159,
            "free_throw_percentage": 0.824,
            "free_throws": 131,
            "games_played": 37,
            "games_started": 37,
            "height": "6-1",
            "minutes_played": 1092,
            "name": "Carsen Edwards",
            "offensive_box_plus_minus": 7.6,
            "offensive_rebound_percentage": 1.5,
            "offensive_rebounds": 13,
            "offensive_win_shares": 4.0,
            "personal_fouls": 65,
            "player_efficiency_rating": 25.4,
            "points": 686,
            "points_produced": 626,
            "position": "Guard",
            "season": "2017-18",
            "steal_percentage": 2.3,
            "steals": 42,
            "team_abbreviation": "purdue",
            "three_point_attempt_rate": 0.478,
            "three_point_attempts": 239,
            "three_point_percentage": 0.406,
            "three_pointers": 97,
            "total_rebound_percentage": 7.7,
            "total_rebounds": 142,
            "true_shooting_percentage": 0.596,
            "turnover_percentage": 10.0,
            "turnovers": 64,
            "two_point_attempts": 261,
            "two_point_percentage": 0.506,
            "two_pointers": 132,
            "usage_percentage": 30.5,
            "weight": 190,
            "win_shares": 6.1,
            "win_shares_per_40_minutes": 0.223,
        }

        self.player = Player("carsen-edwards-1")

    def test_ncaab_player_returns_requested_player_career_stats(self):
        """Return test ncaab player returns requested player career stats."""
        # Request the career stats
        player = self.player("")

        assert player.name == "Carsen Edwards"
        assert player.player_id == "carsen-edwards-1"
        assert player.dataframe is not None

    def test_ncaab_player_returns_requested_player_season_stats(self):
        """Return test ncaab player returns requested player season stats."""
        # Request the 2017-18 stats
        player = self.player("2017-18")

        assert player.name == "Carsen Edwards"
        assert player.player_id == "carsen-edwards-1"
        assert player.dataframe is not None

    def test_correct_initial_index_found(self):
        """Return test correct initial index found."""
        seasons = ["2017-18", "Career", "2016-17"]
        mock_season = mock.PropertyMock(return_value=seasons)
        cast(Any, type(self.player))._season = mock_season

        self.player.find_initial_index()

        assert self.player._index == 1

    def test_dataframe_returns_dataframe(self):
        """Return test dataframe returns dataframe."""
