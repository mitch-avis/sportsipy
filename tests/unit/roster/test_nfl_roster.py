"""Provide utilities for test nfl roster."""

from unittest.mock import patch

from flexmock import flexmock

from sportsipy.nfl.player import AbstractPlayer
from sportsipy.nfl.roster import Player


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


class TestNFLPlayer:
    """Represent TestNFLPlayer."""

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

    @patch("requests.get", side_effect=mock_pyquery)
    def test_requesting_detailed_season_returns_proper_index(self, *args, **kwargs):
        """Return test requesting detailed season returns proper index."""
        player = Player(None)
        player._detailed_stats_seasons = ["2017", "2018", "Career"]
        player._season = ["2015", "2016", "2017", "2018", "Career"]
        player = player("2018")

        assert player._detailed_stats_index == 1
