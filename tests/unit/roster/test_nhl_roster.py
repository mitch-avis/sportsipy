"""Provide utilities for test nhl roster."""

from unittest.mock import patch

from flexmock import flexmock

from sportsipy.nhl.player import AbstractPlayer
from sportsipy.nhl.roster import Player


def mock_pyquery(url, timeout=None):
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


class TestNHLPlayer:
    """Represent TestNHLPlayer."""

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

        assert not player.weight
