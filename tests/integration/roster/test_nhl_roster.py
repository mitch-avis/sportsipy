"""Provide utilities for test nhl roster."""

import os

import pandas as pd
import pytest

from sportsipy import utils
from sportsipy.nhl.roster import Player, Roster
from sportsipy.nhl.teams import Team

YEAR = 2018


def _normalize_multiline(text: str) -> str:
    """Return a multi-line string with empty lines removed."""
    return "\n".join(line for line in text.splitlines() if line.strip())


def read_file(filename):
    """Return read file."""
    filepath = os.path.join(os.path.dirname(__file__), "nhl", filename)
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
    elif "zettehe01" in url:
        mock_pq = MockPQ(read_file("zettehe01"))
    elif "2018" in url:
        mock_pq = MockPQ(read_file("2018"))
    else:
        mock_pq = MockPQ(read_file("howarja02"))
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


class TestNHLPlayer:
    """Represent TestNHLPlayer."""

    def setup_method(self):
        """Return setup method."""
        self.skater_results_career = {
            "adjusted_assists": 692,
            "adjusted_goals": 377,
            "adjusted_goals_against_average": None,
            "adjusted_goals_created": 394,
            "adjusted_points": 1069,
            "age": None,
            "assists": 623,
            "average_time_on_ice": "19:33",
            "blocks_at_even_strength": 267,
            "corsi_against": 11732.0,
            "corsi_for": 17716.0,
            "corsi_for_percentage": 60.2,
            "defensive_point_shares": 29.4,
            "defensive_zone_start_percentage": 38.4,
            "even_strength_assists": 379,
            "even_strength_goals": 228,
            "even_strength_goals_allowed": None,
            "even_strength_save_percentage": None,
            "even_strength_shots_faced": None,
            "faceoff_losses": 5602,
            "faceoff_percentage": 51.1,
            "faceoff_wins": 5863,
            "fenwick_against": 9267,
            "fenwick_for": 13624,
            "fenwick_for_percentage": 59.5,
            "game_winning_goals": 64,
            "games_played": 1082,
            "giveaways": 482,
            "goal_against_percentage_relative": None,
            "goalie_point_shares": None,
            "goals": 337,
            "goals_against": None,
            "goals_against_average": None,
            "goals_against_on_ice": 648,
            "goals_created": None,
            "goals_for_on_ice": 1012,
            "goals_saved_above_average": None,
            "height": "6-0",
            "hits_at_even_strength": 471,
            "league": "NHL",
            "losses": None,
            "minutes": None,
            "name": "Henrik Zetterberg",
            "offensive_point_shares": 79.9,
            "offensive_zone_start_percentage": 61.6,
            "pdo": 100.8,
            "penalties_in_minutes": 401,
            "player_id": "zettehe01",
            "plus_minus": 160,
            "point_shares": 109.3,
            "points": 960,
            "power_play_assists": 235,
            "power_play_goals": 100,
            "power_play_goals_against_on_ice": 140,
            "power_play_goals_allowed": None,
            "power_play_goals_for_on_ice": 490,
            "power_play_save_percentage": None,
            "power_play_shots_faced": None,
            "quality_start_percentage": None,
            "quality_starts": None,
            "really_bad_starts": None,
            "relative_corsi_for_percentage": 10.9,
            "relative_fenwick_for_percentage": 10.3,
            "save_percentage": None,
            "save_percentage_on_ice": None,
            "saves": None,
            "season": "Career",
            "shooting_percentage": 9.8,
            "shooting_percentage_on_ice": 10.2,
            "shootout_attempts": 57,
            "shootout_goals": 13,
            "shootout_misses": 44,
            "shootout_percentage": 22.8,
            "short_handed_assists": 9,
            "short_handed_goals": 9,
            "short_handed_goals_allowed": None,
            "short_handed_save_percentage": None,
            "short_handed_shots_faced": None,
            "shots_against": None,
            "shots_on_goal": 3455,
            "shutouts": None,
            "takeaways": 454,
            "team_abbreviation": None,
            "ties_plus_overtime_loss": None,
            "time_on_ice": 21148,
            "time_on_ice_even_strength": 15041.0,
            "total_goals_against_on_ice": 851,
            "total_goals_for_on_ice": 1362,
            "total_shots": 5408,
            "weight": 197,
            "wins": None,
        }

        self.skater_results_2017 = {
            "adjusted_assists": 46,
            "adjusted_goals": 11,
            "adjusted_goals_against_average": None,
            "adjusted_goals_created": 19,
            "adjusted_points": 57,
            "age": 37,
            "assists": 45,
            "average_time_on_ice": "19:30",
            "blocks_at_even_strength": 34,
            "corsi_against": 1281.0,
            "corsi_for": 1606.0,
            "corsi_for_percentage": 55.6,
            "defensive_point_shares": 2.0,
            "defensive_zone_start_percentage": 37.5,
            "even_strength_assists": 28,
            "even_strength_goals": 10,
            "even_strength_goals_allowed": None,
            "even_strength_save_percentage": None,
            "even_strength_shots_faced": None,
            "faceoff_losses": 709,
            "faceoff_percentage": 48.4,
            "faceoff_wins": 666,
            "fenwick_against": 978,
            "fenwick_for": 1244,
            "fenwick_for_percentage": 56.0,
            "game_winning_goals": 2,
            "games_played": 82,
            "giveaways": 57,
            "goal_against_percentage_relative": None,
            "goalie_point_shares": None,
            "goals": 11,
            "goals_against": None,
            "goals_against_average": None,
            "goals_against_on_ice": 53,
            "goals_created": None,
            "goals_for_on_ice": 79,
            "goals_saved_above_average": None,
            "height": "6-0",
            "hits_at_even_strength": 49,
            "league": "NHL",
            "losses": None,
            "minutes": None,
            "name": "Henrik Zetterberg",
            "offensive_point_shares": 2.4,
            "offensive_zone_start_percentage": 62.5,
            "pdo": 101.2,
            "penalties_in_minutes": 14,
            "player_id": "zettehe01",
            "plus_minus": 1,
            "point_shares": 4.4,
            "points": 56,
            "power_play_assists": 17,
            "power_play_goals": 1,
            "power_play_goals_against_on_ice": 0,
            "power_play_goals_allowed": None,
            "power_play_goals_for_on_ice": 25,
            "power_play_save_percentage": None,
            "power_play_shots_faced": None,
            "quality_start_percentage": None,
            "quality_starts": None,
            "really_bad_starts": None,
            "relative_corsi_for_percentage": 10.3,
            "relative_fenwick_for_percentage": 10.1,
            "save_percentage": None,
            "save_percentage_on_ice": None,
            "saves": None,
            "season": "2017-18",
            "shooting_percentage": 6.1,
            "shooting_percentage_on_ice": 8.7,
            "shootout_attempts": 3,
            "shootout_goals": 0,
            "shootout_misses": 3,
            "shootout_percentage": 0.0,
            "short_handed_assists": 0,
            "short_handed_goals": 0,
            "short_handed_goals_allowed": None,
            "short_handed_save_percentage": None,
            "short_handed_shots_faced": None,
            "shots_against": None,
            "shots_on_goal": 180,
            "shutouts": None,
            "takeaways": 51,
            "team_abbreviation": "DET",
            "ties_plus_overtime_loss": None,
            "time_on_ice": 1599,
            "time_on_ice_even_strength": 1598.7,
            "total_goals_against_on_ice": 53,
            "total_goals_for_on_ice": 79,
            "total_shots": 332,
            "weight": 197,
            "wins": None,
        }

        self.goalie_results_career = {
            "adjusted_assists": None,
            "adjusted_goals": None,
            "adjusted_goals_against_average": 2.98,
            "adjusted_goals_created": None,
            "adjusted_points": None,
            "age": None,
            "assists": 9,
            "average_time_on_ice": None,
            "blocks_at_even_strength": None,
            "corsi_against": None,
            "corsi_for": None,
            "corsi_for_percentage": None,
            "defensive_point_shares": None,
            "defensive_zone_start_percentage": None,
            "even_strength_assists": None,
            "even_strength_goals": None,
            "even_strength_goals_allowed": 980,
            "even_strength_save_percentage": 0.921,
            "even_strength_shots_faced": 12394,
            "faceoff_losses": None,
            "faceoff_percentage": None,
            "faceoff_wins": None,
            "fenwick_against": None,
            "fenwick_for": None,
            "fenwick_for_percentage": None,
            "game_winning_goals": None,
            "games_played": 543,
            "giveaways": None,
            "goal_against_percentage_relative": 98,
            "goalie_point_shares": 90.4,
            "goals": 0,
            "goals_against": 1343,
            "goals_against_average": 2.62,
            "goals_against_on_ice": None,
            "goals_created": None,
            "goals_for_on_ice": None,
            "goals_saved_above_average": -1.3,
            "height": "6-1",
            "hits_at_even_strength": None,
            "league": "NHL",
            "losses": 196,
            "minutes": None,
            "name": "Jimmy Howard",
            "offensive_point_shares": None,
            "offensive_zone_start_percentage": None,
            "pdo": None,
            "penalties_in_minutes": 36,
            "player_id": "howarja02",
            "plus_minus": None,
            "point_shares": None,
            "points": 9,
            "power_play_assists": None,
            "power_play_goals": None,
            "power_play_goals_against_on_ice": None,
            "power_play_goals_allowed": 313,
            "power_play_goals_for_on_ice": None,
            "power_play_save_percentage": 0.869,
            "power_play_shots_faced": 2390,
            "quality_start_percentage": 0.533,
            "quality_starts": 276,
            "really_bad_starts": 76,
            "relative_corsi_for_percentage": None,
            "relative_fenwick_for_percentage": None,
            "save_percentage": 0.912,
            "save_percentage_on_ice": None,
            "saves": 13970,
            "season": "Career",
            "shooting_percentage": None,
            "shooting_percentage_on_ice": None,
            "shootout_attempts": None,
            "shootout_goals": None,
            "shootout_misses": None,
            "shootout_percentage": None,
            "short_handed_assists": None,
            "short_handed_goals": None,
            "short_handed_goals_allowed": 33,
            "short_handed_save_percentage": 0.916,
            "short_handed_shots_faced": 392,
            "shots_against": 15313,
            "shots_on_goal": None,
            "shutouts": 24,
            "takeaways": None,
            "team_abbreviation": None,
            "ties_plus_overtime_loss": 70,
            "time_on_ice": None,
            "time_on_ice_even_strength": None,
            "total_goals_against_on_ice": None,
            "total_goals_for_on_ice": None,
            "total_shots": None,
            "weight": 218,
            "wins": 246,
        }

        self.goalie_results_2017 = {
            "adjusted_assists": None,
            "adjusted_goals": None,
            "adjusted_goals_against_average": 3.08,
            "adjusted_goals_created": None,
            "adjusted_points": None,
            "age": 33,
            "assists": 1,
            "average_time_on_ice": None,
            "blocks_at_even_strength": None,
            "corsi_against": None,
            "corsi_for": None,
            "corsi_for_percentage": None,
            "defensive_point_shares": None,
            "defensive_zone_start_percentage": None,
            "even_strength_assists": None,
            "even_strength_goals": None,
            "even_strength_goals_allowed": 122,
            "even_strength_save_percentage": 0.916,
            "even_strength_shots_faced": 1455,
            "faceoff_losses": None,
            "faceoff_percentage": None,
            "faceoff_wins": None,
            "fenwick_against": None,
            "fenwick_for": None,
            "fenwick_for_percentage": None,
            "game_winning_goals": None,
            "games_played": 60,
            "giveaways": None,
            "goal_against_percentage_relative": 103,
            "goalie_point_shares": 9.4,
            "goals": 0,
            "goals_against": 160,
            "goals_against_average": 2.85,
            "goals_against_on_ice": None,
            "goals_created": None,
            "goals_for_on_ice": None,
            "goals_saved_above_average": -4.7,
            "height": "6-1",
            "hits_at_even_strength": None,
            "league": "NHL",
            "losses": 27,
            "minutes": None,
            "name": "Jimmy Howard",
            "offensive_point_shares": None,
            "offensive_zone_start_percentage": None,
            "pdo": None,
            "penalties_in_minutes": 10,
            "player_id": "howarja02",
            "plus_minus": None,
            "point_shares": None,
            "points": 1,
            "power_play_assists": None,
            "power_play_goals": None,
            "power_play_goals_against_on_ice": None,
            "power_play_goals_allowed": 36,
            "power_play_goals_for_on_ice": None,
            "power_play_save_percentage": 0.869,
            "power_play_shots_faced": 275,
            "quality_start_percentage": 0.491,
            "quality_starts": 28,
            "really_bad_starts": 6,
            "relative_corsi_for_percentage": None,
            "relative_fenwick_for_percentage": None,
            "save_percentage": 0.91,
            "save_percentage_on_ice": None,
            "saves": 1610,
            "season": "2017-18",
            "shooting_percentage": None,
            "shooting_percentage_on_ice": None,
            "shootout_attempts": None,
            "shootout_goals": None,
            "shootout_misses": None,
            "shootout_percentage": None,
            "short_handed_assists": None,
            "short_handed_goals": None,
            "short_handed_goals_allowed": 2,
            "short_handed_save_percentage": 0.949,
            "short_handed_shots_faced": 39,
            "shots_against": 1770,
            "shots_on_goal": None,
            "shutouts": 1,
            "takeaways": None,
            "team_abbreviation": "DET",
            "ties_plus_overtime_loss": 9,
            "time_on_ice": None,
            "time_on_ice_even_strength": None,
            "total_goals_against_on_ice": None,
            "total_goals_for_on_ice": None,
            "total_shots": None,
            "weight": 218,
            "wins": 22,
        }

    def test_nhl_skater_returns_requested_career_stats(self, *args, **kwargs):
        """Return test nhl skater returns requested career stats."""
        # Request the career stats
        player = Player("zettehe01")
        player = player("")

        for attribute, value in self.skater_results_career.items():
            assert getattr(player, attribute) == value

    def test_nhl_skater_returns_player_season_stats(self, *args, **kwargs):
        """Return test nhl skater returns player season stats."""
        # Request the 2017 stats
        player = Player("zettehe01")
        player = player("2017-18")

        for attribute, value in self.skater_results_2017.items():
            assert getattr(player, attribute) == value

    def test_nhl_goalie_returns_requested_career_stats(self, *args, **kwargs):
        """Return test nhl goalie returns requested career stats."""
        # Request the career stats
        player = Player("howarja02")
        player = player("")

        for attribute, value in self.goalie_results_career.items():
            assert getattr(player, attribute) == value

    def test_nhl_goalie_returns_player_season_stats(self, *args, **kwargs):
        """Return test nhl goalie returns player season stats."""
        # Request the 2017 stats
        player = Player("howarja02")
        player = player("2017-18")

        for attribute, value in self.goalie_results_2017.items():
            assert getattr(player, attribute) == value

    def test_dataframe_returns_dataframe(self, *args, **kwargs):
        """Return test dataframe returns dataframe."""
        dataframe = [
            {
                "adjusted_assists": 46,
                "adjusted_goals": 11,
                "adjusted_goals_against_average": None,
                "adjusted_goals_created": 19,
                "adjusted_points": 57,
                "age": 37,
                "assists": 45,
                "average_time_on_ice": "19:30",
                "blocks_at_even_strength": 34,
                "corsi_against": 1243.0,
                "corsi_for": None,
                "corsi_for_percentage": 50.6,
                "defensive_point_shares": 2.0,
                "defensive_zone_start_percentage": 45.2,
                "even_strength_assists": 28,
                "even_strength_goals": 10,
                "even_strength_goals_allowed": None,
                "even_strength_save_percentage": None,
                "even_strength_shots_faced": None,
                "faceoff_losses": 709,
                "faceoff_percentage": 48.4,
                "faceoff_wins": 666,
                "fenwick_against": 948,
                "fenwick_for": 975,
                "fenwick_for_percentage": 50.7,
                "game_winning_goals": 2,
                "games_played": 82,
                "giveaways": 57,
                "goal_against_percentage_relative": None,
                "goalie_point_shares": None,
                "goals": 11,
                "goals_against": None,
                "goals_against_average": None,
                "goals_against_on_ice": 52,
                "goals_created": 18,
                "goals_for_on_ice": 54,
                "goals_saved_above_average": None,
                "height": "6-0",
                "hits_at_even_strength": 49,
                "league": "NHL",
                "losses": None,
                "minutes": None,
                "name": "Henrik Zetterberg",
                "offensive_point_shares": 2.4,
                "offensive_zone_start_percentage": 54.8,
                "pdo": 99.9,
                "penalties_in_minutes": 14,
                "player_id": "zettehe01",
                "plus_minus": 1,
                "point_shares": 4.4,
                "points": 56,
                "power_play_assists": 17,
                "power_play_goals": 1,
                "power_play_goals_against_on_ice": 0,
                "power_play_goals_allowed": None,
                "power_play_goals_for_on_ice": 25,
                "power_play_save_percentage": None,
                "power_play_shots_faced": None,
                "quality_start_percentage": None,
                "quality_starts": None,
                "really_bad_starts": None,
                "relative_corsi_for_percentage": 2.7,
                "relative_fenwick_for_percentage": 2.0,
                "save_percentage": None,
                "save_percentage_on_ice": None,
                "saves": None,
                "season": "2017-18",
                "shooting_percentage": 6.1,
                "shooting_percentage_on_ice": 7.6,
                "shootout_attempts": 3,
                "shootout_goals": 0,
                "shootout_misses": 3,
                "shootout_percentage": 0.0,
                "short_handed_assists": 0,
                "short_handed_goals": 0,
                "short_handed_goals_allowed": None,
                "short_handed_save_percentage": None,
                "short_handed_shots_faced": None,
                "shots_against": None,
                "shots_on_goal": 180,
                "shutouts": None,
                "takeaways": 51,
                "team_abbreviation": "DET",
                "ties_plus_overtime_loss": None,
                "time_on_ice": 1599,
                "time_on_ice_even_strength": 1382.2,
                "total_goals_against_on_ice": 53,
                "total_goals_for_on_ice": 79,
                "total_shots": 332,
                "weight": 197,
                "wins": None,
            },
            {
                "adjusted_assists": 692,
                "adjusted_goals": 377,
                "adjusted_goals_against_average": None,
                "adjusted_goals_created": 394,
                "adjusted_points": 1069,
                "age": None,
                "assists": 623,
                "average_time_on_ice": "19:35",
                "blocks_at_even_strength": 267,
                "corsi_against": 10322.0,
                "corsi_for": None,
                "corsi_for_percentage": 55.1,
                "defensive_point_shares": 29.4,
                "defensive_zone_start_percentage": 45.5,
                "even_strength_assists": 379,
                "even_strength_goals": 228,
                "even_strength_goals_allowed": None,
                "even_strength_save_percentage": None,
                "even_strength_shots_faced": None,
                "faceoff_losses": 5602,
                "faceoff_percentage": 51.1,
                "faceoff_wins": 5863,
                "fenwick_against": 8123,
                "fenwick_for": 9757,
                "fenwick_for_percentage": 54.6,
                "game_winning_goals": 64,
                "games_played": 1082,
                "giveaways": 482,
                "goal_against_percentage_relative": None,
                "goalie_point_shares": None,
                "goals": 337,
                "goals_against": None,
                "goals_against_average": None,
                "goals_against_on_ice": 530,
                "goals_created": 348,
                "goals_for_on_ice": 633,
                "goals_saved_above_average": None,
                "height": "6-0",
                "hits_at_even_strength": 471,
                "league": "NHL",
                "losses": None,
                "minutes": None,
                "name": "Henrik Zetterberg",
                "offensive_point_shares": 79.9,
                "offensive_zone_start_percentage": 54.5,
                "pdo": 100.0,
                "penalties_in_minutes": 401,
                "player_id": "zettehe01",
                "plus_minus": 160,
                "point_shares": 109.3,
                "points": 960,
                "power_play_assists": 235,
                "power_play_goals": 100,
                "power_play_goals_against_on_ice": 140,
                "power_play_goals_allowed": None,
                "power_play_goals_for_on_ice": 490,
                "power_play_save_percentage": None,
                "power_play_shots_faced": None,
                "quality_start_percentage": None,
                "quality_starts": None,
                "really_bad_starts": None,
                "relative_corsi_for_percentage": 3.3,
                "relative_fenwick_for_percentage": 3.1,
                "save_percentage": None,
                "save_percentage_on_ice": None,
                "saves": None,
                "season": "Career",
                "shooting_percentage": 9.8,
                "shooting_percentage_on_ice": 8.8,
                "shootout_attempts": 47,
                "shootout_goals": 10,
                "shootout_misses": 37,
                "shootout_percentage": 21.3,
                "short_handed_assists": 9,
                "short_handed_goals": 9,
                "short_handed_goals_allowed": None,
                "short_handed_save_percentage": None,
                "short_handed_shots_faced": None,
                "shots_against": None,
                "shots_on_goal": 3455,
                "shutouts": None,
                "takeaways": 454,
                "team_abbreviation": None,
                "ties_plus_overtime_loss": None,
                "time_on_ice": 21186,
                "time_on_ice_even_strength": 12658.7,
                "total_goals_against_on_ice": 851,
                "total_goals_for_on_ice": 1362,
                "total_shots": 5408,
                "weight": 197,
                "wins": None,
            },
        ]
        indices = ["2017", "Career"]

        df = pd.DataFrame(dataframe, index=indices)
        player = Player("zettehe01")

        # Pandas doesn't natively allow comparisons of DataFrames.
        # Concatenating the two DataFrames (the one generated during the test
        # and the expected on above) and dropping duplicate rows leaves only
        # the rows that are unique between the two frames. This allows a quick
        # check of the DataFrame to see if it is empty - if so, all rows are
        # duplicates, and they are equal.
        frames = [df, player.dataframe]
        pd.concat(df.dropna(axis=1, how="all") for df in frames).drop_duplicates(keep=False)

    def test_nhl_404_returns_none_with_no_errors(self, *args, **kwargs):
        """Return test nhl 404 returns none with no errors."""
        player = Player("bad")

        assert player.name is None
        assert player.dataframe is None

    def test_nhl_404_returns_none_for_different_season(self, *args, **kwargs):
        """Return test nhl 404 returns none for different season."""
        player = Player("bad")

        assert player.name is None
        assert player.dataframe is None

    def test_nhl_player_string_representation(self, *args, **kwargs):
        """Return test nhl player string representation."""
        player = Player("zettehe01")

        assert repr(player) == "Henrik Zetterberg (zettehe01)"


class TestNHLRoster:
    """Represent TestNHLRoster."""

    def test_roster_class_pulls_all_player_stats(self, monkeypatch, *args, **kwargs):
        """Return test roster class pulls all player stats."""
        monkeypatch.setattr(utils, "find_year_for_season", lambda _: "2018")
        roster = Roster("DET")

        assert len(roster.players) == 30

        players = roster.players
        assert isinstance(players, list)
        player_names = {player.player_id: player.name for player in players}
        assert player_names["abdelju01"] == "Justin Abdelkader"
        assert player_names["howarja02"] == "Jimmy Howard"
        assert player_names["zettehe01"] == "Henrik Zetterberg"

    def test_bad_url_raises_value_error(self, *args, **kwargs):
        """Return test bad url raises value error."""
        with pytest.raises(ValueError):
            Roster("bad")

    def test_roster_from_team_class(self, monkeypatch, *args, **kwargs):
        """Return test roster from team class."""
        monkeypatch.setattr(Team, "_parse_team_data", lambda *_args, **_kwargs: None)
        team = Team(team_data=None, rank=1, year="2018")
        team._abbreviation = "DET"

        assert len(team.roster.players) == 30

        players = team.roster.players
        assert isinstance(players, list)
        player_names = {player.player_id: player.name for player in players}
        assert player_names["abdelju01"] == "Justin Abdelkader"
        assert player_names["howarja02"] == "Jimmy Howard"
        assert player_names["zettehe01"] == "Henrik Zetterberg"
        team._abbreviation = None

    def test_roster_class_with_slim_parameter(self, monkeypatch, *args, **kwargs):
        """Return test roster class with slim parameter."""
        monkeypatch.setattr(utils, "find_year_for_season", lambda _: "2018")
        roster = Roster("DET", slim=True)

        players = roster.players
        assert isinstance(players, dict)
        assert len(players) == 30
        assert players["abdelju01"] == "Justin Abdelkader"
        assert players["howarja02"] == "Jimmy Howard"
        assert players["zettehe01"] == "Henrik Zetterberg"

    def test_invalid_default_year_reverts_to_previous_year(self, monkeypatch, *args, **kwargs):
        """Return test invalid default year reverts to previous year."""
        monkeypatch.setattr(utils, "find_year_for_season", lambda _: 2019)

        roster = Roster("DET")

        assert len(roster.players) == 30

        players = roster.players
        assert isinstance(players, list)
        player_names = {player.player_id: player.name for player in players}
        assert player_names["abdelju01"] == "Justin Abdelkader"
        assert player_names["howarja02"] == "Jimmy Howard"
        assert player_names["zettehe01"] == "Henrik Zetterberg"

    def test_roster_class_string_representation(self, monkeypatch, *args, **kwargs):
        """Return test roster class string representation."""
        monkeypatch.setattr(utils, "find_year_for_season", lambda _: "2018")
        roster = Roster("DET")

        roster_lines = _normalize_multiline(repr(roster)).splitlines()
        assert len(roster_lines) == 30
        assert roster_lines[0] == "Justin Abdelkader (abdelju01)"
        assert "Jimmy Howard (howarja02)" in roster_lines
        assert roster_lines[-1] == "Henrik Zetterberg (zettehe01)"

    def test_coach(self, *args, **kwargs):
        """Return test coach."""
        assert Roster("DET", year=YEAR).coach == "Jeff Blashill"
