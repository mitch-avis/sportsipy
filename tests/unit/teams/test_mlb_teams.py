from typing import Any

from flexmock import flexmock

from sportsipy.mlb.schedule import Schedule
from sportsipy.mlb.teams import Team


class TestMLBTeams:
    def test_mlb_schedule_returns_schedule(self, *args, **kwargs):
        flexmock(Team).should_receive("_parse_team_data").and_return(None)
        flexmock(Schedule).should_receive("_pull_schedule").and_return(None)

        team: Any = Team(None, 1)

        assert len(team.schedule) == 0

    def test_mlb_bad_attribute_property_returns_default(self):
        flexmock(Team).should_receive("_parse_team_data").and_return(None)
        team: Any = Team(None, 1)

        team._extra_inning_record = None

        assert team.extra_inning_wins is None

    def test_mlb_bad_int_property_returns_default(self):
        flexmock(Team).should_receive("_parse_team_data").and_return(None)
        team: Any = Team(None, 1)

        team._extra_inning_record = "Bad-Bad"

        assert team.extra_inning_wins is None
