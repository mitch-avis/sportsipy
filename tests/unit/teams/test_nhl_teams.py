"""Provide utilities for test nhl teams."""

from flexmock import flexmock

from sportsipy.nhl.schedule import Schedule
from sportsipy.nhl.teams import Team


class TestNHLTeams:
    """Represent TestNHLTeams."""

    def test_nhl_schedule_returns_schedule(self, *args, **kwargs):
        """Return test nhl schedule returns schedule."""
        flexmock(Team).should_receive("_parse_team_data").and_return(None)
        flexmock(Schedule).should_receive("_pull_schedule").and_return(None)

        team = Team(None, 1)

        assert len(team.schedule) == 0
