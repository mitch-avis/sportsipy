"""Provide utilities for test ncaaf roster."""

from unittest.mock import patch

import pytest
from flexmock import flexmock

from sportsipy import utils
from sportsipy.ncaaf import roster as roster_module
from sportsipy.ncaaf.player import AbstractPlayer
from sportsipy.ncaaf.roster import (
    Player,
    Roster,
    _float_property_decorator,
    _int_property_decorator,
)


def mock_pyquery(url, timeout=None, **kwargs):
    """Return mock pyquery."""

    class MockPQ:
        def __init__(self, html_contents):
            self.url = url
            self.reason = "Bad URL"  # Used when throwing HTTPErrors
            self.headers = {}  # Used when throwing HTTPErrors
            self.status_code = 404
            self.html_contents = html_contents
            self.text = html_contents

    return MockPQ(None)


class TestNCAAFPlayer:
    """Represent TestNCAAFPlayer."""

    def setup_method(self):
        """Return setup method."""
        flexmock(AbstractPlayer).should_receive("_parse_player_data").and_return(None)
        flexmock(Player).should_receive("_pull_player_data").and_return(None)
        flexmock(Player).should_receive("find_initial_index").and_return(None)

    @patch("requests.get", side_effect=mock_pyquery)
    def test_invalid_url_returns_none(self, *args, **kwargs):
        """Return test invalid url returns none."""
        player = Player(None)
        player._player_id = "BAD"

        result = player._retrieve_html_page()

        assert result is None

    @patch("requests.get", side_effect=mock_pyquery)
    def test_missing_weight_returns_none(self, *args, **kwargs):
        """Return test missing weight returns none."""
        player = Player(None)
        player._weight = None

        result = player.weight

        assert result is None


class _DecoratedIntExample:
    def __init__(self, values, index):
        self._values = values
        self._index = index

    @_int_property_decorator
    def values(self):
        return self._values


class _DecoratedFloatExample:
    def __init__(self, values, index):
        self._values = values
        self._index = index

    @_float_property_decorator
    def values(self):
        return self._values


class TestNCAAFRosterHelpers:
    """Represent TestNCAAFRosterHelpers."""

    def test_private_int_decorator_handles_errors(self):
        """Return test private int decorator handles errors."""
        assert _DecoratedIntExample(["1", "2"], 1).values == 2
        assert _DecoratedIntExample(["1"], 2).values is None
        assert _DecoratedIntExample(["BAD"], 0).values is None

    def test_private_float_decorator_handles_errors(self):
        """Return test private float decorator handles errors."""
        assert _DecoratedFloatExample(["1.5", "2.5"], 0).values == 1.5
        assert _DecoratedFloatExample(["1.5"], 3).values is None
        assert _DecoratedFloatExample(["BAD"], 0).values is None


class TestNCAAFPlayerProperties:
    """Represent TestNCAAFPlayerProperties."""

    def setup_method(self):
        """Return setup method."""
        flexmock(AbstractPlayer).should_receive("_parse_player_data").and_return(None)
        flexmock(Player).should_receive("_pull_player_data").and_return(None)
        flexmock(Player).should_receive("find_initial_index").and_return(None)

    def test_property_accessors_and_dataframe(self):
        """Return test property accessors and dataframe."""
        player = Player("test-player")
        player.__dict__.update(
            {
                "_season": ["2020", "Career"],
                "_most_recent_season": "2020",
                "_index": 0,
                "_name": "Test Player",
                "_player_id": "test-player",
                "_height": "6-2",
                "_weight": "215lb",
                "_team_abbreviation": ["PURDUE", "PURDUE"],
                "_position": ["QB", ""],
                "_year": ["SR", ""],
                "_games": ["12", "48"],
                "_completed_passes": ["120", "500"],
                "_pass_attempts": ["200", "800"],
                "_passing_completion": ["60.0", "62.5"],
                "_passing_yards": ["1500", "6000"],
                "_passing_touchdowns": ["10", "45"],
                "_interceptions_thrown": ["4", "20"],
                "_passing_yards_per_attempt": ["7.5", "7.4"],
                "_adjusted_yards_per_attempt": ["8.1", "8.0"],
                "_quarterback_rating": ["140.3", "138.1"],
                "_rush_attempts": ["40", "150"],
                "_rush_yards": ["120", "400"],
                "_rush_yards_per_attempt": ["3.0", "2.7"],
                "_rush_touchdowns": ["2", "8"],
                "_receptions": ["0", "5"],
                "_receiving_yards": ["0", "80"],
                "_receiving_yards_per_reception": ["0.0", "16.0"],
                "_receiving_touchdowns": ["0", "1"],
                "_plays_from_scrimmage": ["40", "155"],
                "_yards_from_scrimmage": ["120", "480"],
                "_yards_from_scrimmage_per_play": ["3.0", "3.1"],
                "_rushing_and_receiving_touchdowns": ["2", "9"],
                "_solo_tackles": ["1", "4"],
                "_assists_on_tackles": ["0", "1"],
                "_total_tackles": ["1", "5"],
                "_tackles_for_loss": ["0.0", "1.0"],
                "_sacks": ["0.0", "0.0"],
                "_interceptions": ["0", "0"],
                "_yards_returned_from_interceptions": ["0", "0"],
                "_yards_returned_per_interception": ["0.0", "0.0"],
                "_interceptions_returned_for_touchdown": ["0", "0"],
                "_passes_defended": ["0", "0"],
                "_fumbles_recovered": ["0", "1"],
                "_yards_recovered_from_fumble": ["0", "0"],
                "_fumbles_recovered_for_touchdown": ["0", "0"],
                "_fumbles_forced": ["0", "0"],
                "_punt_return_touchdowns": ["0", "0"],
                "_kickoff_return_touchdowns": ["0", "0"],
                "_other_touchdowns": ["0", "0"],
                "_total_touchdowns": ["12", "54"],
                "_extra_points_made": ["0", "0"],
                "_field_goals_made": ["0", "0"],
                "_two_point_conversions": ["1", "2"],
                "_safeties": ["0", "0"],
                "_points": ["74", "326"],
            }
        )

        assert player.team_abbreviation == "PURDUE"
        assert player.position == "QB"
        assert player.weight == 215
        assert player.games == 12
        assert player.passing_completion == 60.0
        assert player.rush_yards_per_attempt == 3.0
        assert player.yards_from_scrimmage == 120
        assert player.sacks == 0.0
        assert player.total_touchdowns == 12
        assert player.points == 74

        player("Career")
        assert player.position == "QB"

        player.__dict__["_weight"] = "BAD"
        assert player.weight is None

        player.__dict__["_weight"] = "215lb"
        df = player.dataframe
        assert df is not None
        assert "name" in df.columns
        assert "points" in df.columns

    def test_parse_season_and_call_paths(self):
        """Return test parse season and call paths."""
        player = Player("test-player")
        assert player._parse_season(utils.pq("<tr></tr>")) is None

        season = player._parse_season(utils.pq('<tr><th data-stat="year_id">2017*+</th></tr>'))
        assert season == "2017"

        player.__dict__.update({"_season": ["2017", "Career"], "_index": 0})
        player("2017")
        assert player.season == "2017"

        player.__dict__["_season"] = None
        assert player("2017") is player

    def test_position_and_dataframe_none_paths(self):
        """Return test position and dataframe none paths."""
        player = Player("test-player")
        player.__dict__.update(
            {
                "_season": ["Career"],
                "_index": 0,
                "_position": [""],
                "_most_recent_season": None,
            }
        )
        assert player.position is None

        player.__dict__["_season"] = None
        assert player.dataframe is None

    def test_combine_stats_and_pull_player_data_paths(self, monkeypatch):
        """Return test combine stats and pull player data paths."""
        player = Player("test-player")
        player.__dict__["_most_recent_season"] = None

        row = utils.pq('<tr><th data-stat="year_id">2017</th><td>A</td></tr>')
        career = iter([utils.pq('<tr><th data-stat="year_id">Career</th><td>B</td></tr>')])
        stats = player._combine_season_stats([row], career, {})
        assert "2017" in stats
        assert "Career" in stats

        monkeypatch.setattr(utils, "get_stats_table", lambda *_args, **_kwargs: [])
        combined = player._combine_all_stats(utils.pq("<html></html>"))
        assert combined == {}

        monkeypatch.setattr(Player, "_retrieve_html_page", lambda _self: None)
        assert player._pull_player_data() is None

    def test_combine_all_stats_checks_standard_table_ids(self, monkeypatch):
        """Return test combine all stats checks modern *_standard table ids."""
        player = Player("test-player")
        requested_divs = []

        def fake_get_stats_table(_html, div, footer=False):
            requested_divs.append((div, footer))
            return []

        monkeypatch.setattr(utils, "get_stats_table", fake_get_stats_table)

        player._combine_all_stats(utils.pq("<html></html>"))

        assert ("table#passing_standard", False) in requested_divs
        assert ("table#rushing_standard", False) in requested_divs
        assert ("table#scoring_standard", False) in requested_divs

    def test_parse_player_information_sets_attributes(self):
        """Return test parse player information sets attributes."""
        player = Player("test-player")
        html = utils.pq(
            '<h1 itemprop="name">Name</h1>'
            '<span itemprop="height">6-2</span>'
            '<span itemprop="weight">215lb</span>'
        )
        player._parse_player_information(html)
        assert player.height == "6-2"
        assert player.weight == 215


class TestNCAAFRosterClass:
    """Represent TestNCAAFRosterClass."""

    def test_create_url_handles_missing_team(self):
        """Return test create url handles missing team."""
        roster = object.__new__(Roster)
        roster._team = None

        result = roster._create_url("2017")

        assert "/schools//2017" in result

    def test_pull_team_page_returns_none_on_http_error(self, monkeypatch):
        """Return test pull team page returns none on http error."""
        roster = object.__new__(Roster)
        roster._team = "PURDUE"
        monkeypatch.setattr(utils, "get_page_source", lambda url: None)

        assert roster._pull_team_page("https://example.com") is None

    def test_find_players_with_coach_slim_mode(self, monkeypatch):
        """Return test find players with coach slim mode."""
        html = (
            '<table id="roster"><tbody>'
            '<tr><th data-stat="player"><a href="/cfb/players/a/player-one-1.html">'
            "Player One</a></th></tr>"
            '<tr><th data-stat="player"><a href="/cfb/players/b/player-two-1.html">'
            "Player Two</a></th></tr>"
            "</tbody></table>"
            "<p><strong>Coach:</strong> <a>Jeff Brohm</a></p>"
        )
        monkeypatch.setattr(Roster, "_pull_team_page", lambda _self, _url: utils.pq(html))

        roster = Roster("PURDUE", year=2017, slim=True)

        assert isinstance(roster.players, dict)
        assert roster.players.get("a/player-one-1") == "Player One"
        assert roster.coach == "Jeff Brohm"

    def test_find_players_with_coach_full_mode_uses_player_fallback_name(self, monkeypatch):
        """Return test find players with coach full mode uses player fallback name."""

        class FakePlayer:
            def __init__(self, player_id):
                self.player_id = player_id
                self.name = None
                self._name = None

        html = (
            '<table id="roster"><tbody>'
            '<tr><th data-stat="player"><a href="/cfb/players/a/player-one-1.html">'
            "Player One</a></th></tr>"
            "</tbody></table>"
            "<p><strong>Coach:</strong> <a>Jeff Brohm</a></p>"
        )
        monkeypatch.setattr(Roster, "_pull_team_page", lambda _self, _url: utils.pq(html))
        monkeypatch.setattr(roster_module, "Player", FakePlayer)

        roster = Roster("PURDUE", year=2017, slim=False)

        assert isinstance(roster.players, list)
        assert len(roster.players) == 1
        assert roster.players[0]._name == "Player One"

    def test_find_players_with_coach_raises_for_missing_page(self, monkeypatch):
        """Return test find players with coach raises for missing page."""
        monkeypatch.setattr(Roster, "_pull_team_page", lambda _self, _url: None)

        with pytest.raises(ValueError):
            Roster("PURDUE", year=2017, slim=True)

    def test_str_and_repr_for_slim_and_full(self, monkeypatch):
        """Return test str and repr for slim and full rosters."""
        html = (
            '<table id="roster"><tbody>'
            '<tr><th data-stat="player"><a href="/cfb/players/a/player-one-1.html">'
            "Player One</a></th></tr>"
            "</tbody></table>"
            "<p><strong>Coach:</strong> <a>Jeff Brohm</a></p>"
        )
        monkeypatch.setattr(Roster, "_pull_team_page", lambda _self, _url: utils.pq(html))

        slim_roster = Roster("PURDUE", year=2017, slim=True)
        assert "Player One" in str(slim_roster)
        assert "Player One" in repr(slim_roster)

        class FakePlayer:
            def __init__(self, player_id):
                self.player_id = player_id
                self.name = "Player One"

        monkeypatch.setattr(roster_module, "Player", FakePlayer)
        full_roster = Roster("PURDUE", year=2017, slim=False)
        assert "Player One" in str(full_roster)
        assert "Player One" in repr(full_roster)
