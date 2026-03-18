"""Provide utilities for test ncaaf teams."""

from typing import Any

from flexmock import flexmock

from sportsipy.ncaaf.schedule import Schedule
from sportsipy.ncaaf.teams import Team


class TestNCAAFTeams:
    """Represent TestNCAAFTeams."""

    def setup_method(self, *args, **kwargs):
        """Return setup method."""
        flexmock(Team).should_receive("_parse_team_data").and_return(None)

        self.team: Any = Team(None)

    def test_no_conference_wins_data_returns_default(self):
        """Return test no conference wins data returns default."""
        self.team._conference_wins = ""

        assert self.team.conference_wins is None

    def test_no_conference_losses_data_returns_default(self):
        """Return test no conference losses data returns default."""
        self.team._conference_losses = ""

        assert self.team.conference_losses is None

    def test_no_conference_percentage_returns_default(self):
        """Return test no conference percentage returns default."""
        self.team._conference_win_percentage = ""

        assert self.team.conference_win_percentage is None

    def test_ncaaf_schedule_returns_schedule(self):
        """Return test ncaaf schedule returns schedule."""
        flexmock(Schedule).should_receive("_pull_schedule").and_return(None)

        team = Team(None, 1)

        assert len(team.schedule) == 0
