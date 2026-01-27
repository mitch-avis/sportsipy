from flexmock import flexmock
from mock import patch

from sportsipy.nhl.player import AbstractPlayer
from sportsipy.nhl.roster import Player


def mock_pyquery(url, timeout=None):
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
    def setup_method(self):
        flexmock(AbstractPlayer).should_receive("_parse_player_data").and_return(None)
        flexmock(Player).should_receive("_pull_player_data").and_return(None)
        flexmock(Player).should_receive("find_initial_index").and_return(None)

    @patch("requests.get", side_effect=mock_pyquery)
    def test_invalid_url_returns_none(self, *args, **kwargs):
        player = Player(None)
        player._player_id = "BAD"

        result = player._retrieve_html_page()

        assert result is None

    @patch("requests.get", side_effect=mock_pyquery)
    def test_missing_weight_returns_none(self, *args, **kwargs):
        player = Player(None)
        player._weight = None

        assert not player.weight
