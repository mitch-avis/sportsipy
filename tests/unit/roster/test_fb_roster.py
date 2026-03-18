"""Provide utilities for test fb roster."""

from unittest import mock
from urllib.error import HTTPError

import pytest
from flexmock import flexmock
from pyquery import PyQuery

from sportsipy.fb.roster import Roster, SquadPlayer


class MockSquadPlayer:
    """Represent MockSquadPlayer."""

    def __init__(self, name=None, player_id=None):
        """Initialize the class instance."""
        self.name = name
        self.player_id = player_id

    def __call__(self, obj):
        """Return   call  ."""
        return PyQuery("<tr></tr>")


def mock_httperror(url, timeout=None, **kwargs):
    """Return mock httperror."""

    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 504
            self.html_contents = html_contents
            self.text = html_contents
            self.url = url
            self.reason = HTTPError
            self.headers = None

    return MockPQ(None)


class TestFBRoster:
    """Represent TestFBRoster."""

    def setup_method(self):
        """Return setup method."""
        flexmock(Roster).should_receive("__init__").and_return(None)
        flexmock(SquadPlayer).should_receive("_parse_player_stats").and_return(None)
        self.roster = Roster(None)
        self.player = SquadPlayer(None, None)

    def test_no_country_returns_none(self):
        """Return test no country returns none."""
        result = self.player._parse_nationality(PyQuery("<tr></tr>"))

        assert not result

    def test_no_player_name_or_player_id_raises_value_error(self):
        """Return test no player name or player id raises value error."""
        self.roster._players = [MockSquadPlayer()]

        with pytest.raises(ValueError):
            self.roster("")

    def test_invalid_player_id_returns_none(self):
        """Return test invalid player id returns none."""
        result = self.roster._player_id(PyQuery('<th data-stat="player"></th>'))

        assert not result

    def test_no_player_id_skips_player(self):
        """Return test no player id skips player."""
        result = self.roster._add_stats_data([MockSquadPlayer()], {})

        assert not result

    @mock.patch("requests.get", side_effect=mock_httperror)
    def test_invalid_http_page_error(self, *args, **kwargs):
        """Return test invalid http page error."""
        flexmock(Roster).should_receive("__init__").and_return(None)
        roster = Roster(None)
        roster._squad_id = ""

        output = roster._pull_stats(None)

        assert not output
