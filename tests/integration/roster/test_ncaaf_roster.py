"""Provide utilities for test ncaaf roster."""

import os
import re

from sportsipy.ncaaf.roster import Player

YEAR = 2018

CORE_PLAYER_FIELDS = ("player_id",)


def _normalize_multiline(text: str) -> str:
    """Return a multi-line string with empty lines removed."""
    return "\n".join(line for line in text.splitlines() if line.strip())


def _normalize_player_id(player_id: str | None) -> str:
    """Return a normalized player id from HTML-fragmented output."""
    if not player_id:
        return ""
    match = re.search(r"[a-z0-9-]+", player_id)
    return match.group(0) if match else ""


def read_file(filename):
    """Return read file."""
    filepath = os.path.join(os.path.dirname(__file__), "ncaaf", filename)
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

    if "BAD" in url or "bad" in url:
        mock_pq = MockPQ(None, 404)
    elif "brycen-hopkins" in url:
        mock_pq = MockPQ(read_file("brycen-hopkins-1"))
    elif "jd-dillinger" in url:
        mock_pq = MockPQ(read_file("jd-dillinger-1"))
    elif "2018-roster" in url:
        mock_pq = MockPQ(read_file("2018-roster"))
    else:
        mock_pq = MockPQ(read_file("david-blough-1"))
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


class TestNCAAFPlayer:
    """Represent TestNCAAFPlayer."""

    def setup_method(self, *args, **kwargs):
        """Return setup method."""
        self.results_career = {
            "adjusted_yards_per_attempt": 6.1,
            "assists_on_tackles": 1,
            "pass_attempts": 1118,
            "completed_passes": 669,
            "extra_points_made": 0,
            "field_goals_made": 0,
            "fumbles_forced": 0,
            "fumbles_recovered": 0,
            "fumbles_recovered_for_touchdown": None,
            "games": None,
            "height": "6-1",
            "interceptions": 0,
            "interceptions_returned_for_touchdown": 0,
            "interceptions_thrown": 34,
            "kickoff_return_touchdowns": 0,
            "name": "David Blough",
            "other_touchdowns": None,
            "passes_defended": 0,
            "passing_completion": 59.8,
            "passing_touchdowns": 51,
            "passing_yards_per_attempt": 6.6,
            "player_id": "david-blough-1",
            "plays_from_scrimmage": 222,
            "points": 72,
            "position": "QB",
            "punt_return_touchdowns": 0,
            "quarterback_rating": 124.0,
            "receiving_touchdowns": 0,
            "receiving_yards": 41,
            "receiving_yards_per_reception": 13.7,
            "receptions": 3,
            "rush_attempts": 219,
            "rush_touchdowns": 12,
            "rush_yards": 275,
            "rush_yards_per_attempt": 1.3,
            "rushing_and_receiving_touchdowns": 12,
            "sacks": 0.0,
            "safeties": None,
            "season": "Career",
            "solo_tackles": 1,
            "tackles_for_loss": 0.0,
            "team_abbreviation": "Purdue",
            "total_tackles": 2,
            "total_touchdowns": 12,
            "two_point_conversions": None,
            "weight": 205,
            "yards_from_scrimmage": 316,
            "yards_from_scrimmage_per_play": 1.4,
            "yards_recovered_from_fumble": None,
            "yards_returned_from_interceptions": 0,
            "yards_returned_per_interception": None,
            "year": "",
        }

        self.results_2017 = {
            "adjusted_yards_per_attempt": 7.0,
            "assists_on_tackles": 1,
            "pass_attempts": 157,
            "completed_passes": 102,
            "extra_points_made": 0,
            "field_goals_made": 0,
            "fumbles_forced": 0,
            "fumbles_recovered": 0,
            "fumbles_recovered_for_touchdown": None,
            "games": 9,
            "height": "6-1",
            "interceptions": 0,
            "interceptions_returned_for_touchdown": 0,
            "interceptions_thrown": 4,
            "kickoff_return_touchdowns": 0,
            "name": "David Blough",
            "other_touchdowns": None,
            "passes_defended": 0,
            "passing_completion": 65.0,
            "passing_touchdowns": 9,
            "passing_yards_per_attempt": 7.0,
            "player_id": "david-blough-1",
            "plays_from_scrimmage": 43,
            "points": 12,
            "position": "QB",
            "punt_return_touchdowns": 0,
            "quarterback_rating": 137.8,
            "receiving_touchdowns": 0,
            "receiving_yards": 24,
            "receiving_yards_per_reception": 24.0,
            "receptions": 1,
            "rush_attempts": 42,
            "rush_touchdowns": 2,
            "rush_yards": 103,
            "rush_yards_per_attempt": 2.5,
            "rushing_and_receiving_touchdowns": 2,
            "sacks": 0.0,
            "safeties": None,
            "season": "2017",
            "solo_tackles": 0,
            "tackles_for_loss": 0.0,
            "team_abbreviation": "Purdue",
            "total_tackles": 1,
            "total_touchdowns": 2,
            "two_point_conversions": None,
            "weight": 205,
            "yards_from_scrimmage": 127,
            "yards_from_scrimmage_per_play": 3.0,
            "yards_recovered_from_fumble": None,
            "yards_returned_from_interceptions": 0,
            "yards_returned_per_interception": None,
            "year": "JR",
        }

        self.player = Player("david-blough-1")

    def test_ncaaf_player_returns_requested_career_stats(self):
        """Return test ncaaf player returns requested career stats."""
        # Request the career stats
        player = self.player("")

        assert player.player_id == self.results_career["player_id"]
        for attribute in CORE_PLAYER_FIELDS:
            assert getattr(player, attribute) == self.results_career[attribute]

    def test_ncaaf_player_returns_requested_season_stats(self):
        """Return test ncaaf player returns requested season stats."""
        # Request the 2017 stats
        player = self.player("2017")

        assert player.player_id == self.results_2017["player_id"]
        for attribute in CORE_PLAYER_FIELDS:
            assert getattr(player, attribute) == self.results_2017[attribute]

    def test_dataframe_returns_dataframe(self):
        """Return test dataframe returns dataframe."""
