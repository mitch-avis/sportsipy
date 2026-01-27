from typing import Any, cast

from flexmock import flexmock

from sportsipy.ncaab.schedule import Schedule
from sportsipy.ncaab.teams import Team


class TestNCAABTeams:
    def test_ncaab_schedule_returns_schedule(self, *args, **kwargs):
        flexmock(Team).should_receive("_parse_team_data").and_return(None)
        flexmock(Schedule).should_receive("_pull_schedule").and_return(None)

        team = Team(None, 1)

        assert len(team.schedule) == 0

    def test_two_point_field_goal_percentage_returns_default(self):
        flexmock(Team).should_receive("_parse_team_data").and_return(None)
        flexmock(Schedule).should_receive("_pull_schedule").and_return(None)

        team = Team(None, 1)
        typed_team = cast(Any, team)
        typed_team._field_goals = 0
        typed_team._three_point_field_goals = 0
        typed_team._field_goal_attempts = 0
        typed_team._three_point_field_goal_attempts = 0

        result = team.two_point_field_goal_percentage

        assert result == 0.0

    def test_opp_two_point_field_goal_percentage_returns_default(self):
        flexmock(Team).should_receive("_parse_team_data").and_return(None)
        flexmock(Schedule).should_receive("_pull_schedule").and_return(None)

        team = Team(None, 1)
        typed_team = cast(Any, team)
        typed_team._opp_field_goals = 0
        typed_team._opp_three_point_field_goals = 0
        typed_team._opp_field_goal_attempts = 0
        typed_team._opp_three_point_field_goal_attempts = 0

        result = team.opp_two_point_field_goal_percentage

        assert result == 0.0

    def test_defensive_rebounds_with_missing_data_returns_default(self):
        flexmock(Team).should_receive("_parse_team_data").and_return(None)
        flexmock(Schedule).should_receive("_pull_schedule").and_return(None)

        team = Team(None, 1)
        team._offensive_rebounds = None

        result = team.defensive_rebounds

        assert not result

    def test_opp_defensive_rebounds_with_missing_data_returns_default(self):
        flexmock(Team).should_receive("_parse_team_data").and_return(None)
        flexmock(Schedule).should_receive("_pull_schedule").and_return(None)

        team = Team(None, 1)
        team._opp_offensive_rebounds = None

        result = team.opp_defensive_rebounds

        assert not result

    def test_net_rating_with_missing_data_returns_default(self):
        flexmock(Team).should_receive("_parse_team_data").and_return(None)
        flexmock(Schedule).should_receive("_pull_schedule").and_return(None)

        team = Team(None, 1)
        team._offensive_rating = None

        result = team.net_rating

        assert not result
