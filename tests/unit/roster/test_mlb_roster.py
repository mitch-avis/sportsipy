"""Provide utilities for test mlb roster."""

from typing import Any
from unittest.mock import patch

from flexmock import flexmock

from sportsipy.mlb.player import AbstractPlayer
from sportsipy.mlb.player import _cleanup as _cleanup_player
from sportsipy.mlb.roster import Player, _cleanup


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


class TestMLBPlayer:
    """Represent TestMLBPlayer."""

    def setup_method(self):
        """Return setup method."""
        flexmock(AbstractPlayer).should_receive("_parse_player_data").and_return(None)
        flexmock(Player).should_receive("_pull_player_data").and_return(None)
        flexmock(Player).should_receive("find_initial_index").and_return(None)

    def test_no_int_returns_default_value(self):
        """Return test no int returns default value."""
        player: Any = Player(None)
        player._runs = [[""]]
        player._index = 0

        result = player.runs

        assert result is None

    def test_no_float_returns_default_value(self):
        """Return test no float returns default value."""
        player: Any = Player(None)
        player._batting_average = [[""]]
        player._index = 0

        result = player.batting_average

        assert result is None

    def test_no_recent_returns_default_value(self):
        """Return test no recent returns default value."""
        player: Any = Player(None)
        player._position = [[""]]
        player._season = ["2018"]
        player._most_recent_season = "2018"

        result = player.position

        assert result is None

    @patch("requests.get", side_effect=mock_pyquery)
    def test_invalid_url_return_none(self, *args, **kwargs):
        """Return test invalid url return none."""
        player: Any = Player(None)
        player._player_id = "BAD"

        result = player._retrieve_html_page()

        assert result is None

    def test_cleanup_of_none_returns_default(self):
        """Return test cleanup of none returns default."""
        result = _cleanup(None)

        assert result == ""

    def test_cleanup_of_none_returns_default_for_player(self):
        """Return test cleanup of none returns default for player."""
        result = _cleanup_player(None)

        assert result == ""

    @patch("requests.get", side_effect=mock_pyquery)
    def test_missing_weight_returns_none(self, *args, **kwargs):
        """Return test missing weight returns none."""
        player: Any = Player(None)
        player._weight = None

        assert not player.weight
