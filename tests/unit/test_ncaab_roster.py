from flexmock import flexmock
from mock import patch

from sportsipy.ncaab.player import AbstractPlayer
from sportsipy.ncaab.player import _cleanup as _cleanup_player
from sportsipy.ncaab.roster import Player, _cleanup


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


class TestNCAABPlayer:
    def setup_method(self):
        flexmock(AbstractPlayer).should_receive("_parse_player_data").and_return(None)
        flexmock(Player).should_receive("_pull_player_data").and_return(None)
        flexmock(Player).should_receive("find_initial_index").and_return(None)

    def test_no_int_return_default_value_abstract_class(self):
        player = Player(None)
        player._field_goals = [""]
        player._index = 0

        result = player.field_goals

        assert result is None

    def test_no_float_returns_default_value_abstract_class(self):
        player = Player(None)
        player._field_goal_percentage = [""]
        player._index = 0

        result = player.field_goal_percentage

        assert result is None

    def test_no_int_return_default_value_player_class(self):
        player = Player(None)
        player._games_played = [""]
        player._index = 0

        result = player.games_played

        assert result is None

    def test_no_float_returns_default_value_player_class(self):
        player = Player(None)
        player._player_efficiency_rating = [""]
        player._index = 0

        result = player.player_efficiency_rating

        assert result is None

    @patch("requests.get", side_effect=mock_pyquery)
    def test_invalid_url_returns_none(self, *args, **kwargs):
        player = Player(None)
        player._player_id = "BAD"

        result = player._retrieve_html_page()

        assert result is None

    def test_cleanup_of_none_returns_default(self):
        result = _cleanup(None)

        assert result == ""

    def test_cleanup_of_none_returns_default_for_player(self):
        result = _cleanup_player(None)

        assert result == ""

    def test_player_with_no_stats(self):
        player = Player(None)
        result = player._combine_season_stats(None, None, {})

        assert not result

    def test_player_with_no_weight_returns_none(self):
        player = Player(None)
        player._weight = None

        result = player.weight

        assert result is None
