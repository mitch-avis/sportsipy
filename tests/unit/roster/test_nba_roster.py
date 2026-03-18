"""Provide utilities for test nba roster."""

from typing import Any
from unittest.mock import patch

from flexmock import flexmock

from sportsipy.nba.player import AbstractPlayer
from sportsipy.nba.player import _cleanup as _cleanup_player
from sportsipy.nba.roster import Player, _cleanup


class MockItem:
    """Represent MockItem."""

    def attr(self, item):
        """Return attr."""
        return "contracts_"


class MockInfo:
    """Represent MockInfo."""

    def __call__(self, item):
        """Return   call  ."""
        return self

    def items(self):
        """Return items."""
        return [MockItem()]


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


class TestNBAPlayer:
    """Represent TestNBAPlayer."""

    def setup_method(self):
        """Return setup method."""
        flexmock(AbstractPlayer).should_receive("_parse_player_data").and_return(None)
        flexmock(Player).should_receive("__init__").and_return(None)

    def test_no_float_returns_default_value_abstract_class(self):
        """Return test no float returns default value abstract class."""
        player: Any = Player(None)
        player._field_goal_percentage = [""]
        player._index = 0

        result = player.field_goal_percentage

        assert result is None

    def test_no_float_returns_default_value_player_class(self):
        """Return test no float returns default value player class."""
        player: Any = Player(None)
        player._player_efficiency_rating = [""]
        player._index = 0

        result = player.player_efficiency_rating

        assert result is None

    @patch("requests.get", side_effect=mock_pyquery)
    def test_invalid_url_returns_none(self, *args, **kwargs):
        """Return test invalid url returns none."""
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

    def test_empty_contract_is_none(self):
        """Return test empty contract is none."""
        player_info = MockInfo()

        flexmock(Player).should_receive("_parse_contract_headers").and_return(None)

        flexmock(Player).should_receive("_parse_contract_wages").and_return(None)

        flexmock(Player).should_receive("_combine_contract").and_return({})

        player: Any = Player(None)

        player._parse_contract(player_info)

        assert player._contract is None

    @patch("requests.get", side_effect=mock_pyquery)
    def test_missing_weight_returns_none(self, *args, **kwargs):
        """Return test missing weight returns none."""
        player: Any = Player(None)
        player._weight = None

        assert not player.weight


class TestInvalidNBAPlayer:
    """Represent TestInvalidNBAPlayer."""

    def test_no_player_data_returns_no_stats(self):
        """Return test no player data returns no stats."""
        flexmock(Player).should_receive("_retrieve_html_page").and_return(None)

        stats = Player(None)._pull_player_data()

        assert stats is None
