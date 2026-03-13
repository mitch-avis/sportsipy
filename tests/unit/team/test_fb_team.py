"""Provide utilities for test fb team."""

from unittest import mock
from urllib.error import HTTPError

from flexmock import flexmock

from sportsipy.fb.roster import Roster
from sportsipy.fb.schedule import Schedule
from sportsipy.fb.team import Team


def mock_httperror(url, timeout=None):
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


class TestFBTeam:
    """Represent TestFBTeam."""

    def setup_method(self):
        """Return setup method."""
        flexmock(Team).should_receive("_pull_team_page").and_return(None)
        flexmock(Schedule).should_receive("_pull_schedule").and_return(None)
        flexmock(Roster).should_receive("_pull_stats").and_return(None)
        self.team = Team("Tottenham Hotspur")

    def test_location_record_missing_result(self):
        """Return test location record missing result."""
        html = "Home Record: (5-0-0)"

        output = self.team._location_records(html)

        assert output == (None, None, None, None)

    def test_location_record_missing_points(self):
        """Return test location record missing points."""
        html = "Home Record: 15 points (5-0-0)"

        output = self.team._location_records(html)

        assert output == (None, None, None, None)

    def test_records_missing_result(self):
        """Return test records missing result."""
        html = "Record: 5-0-0, 15 points (3.0 per game)"

        output = self.team._records(html)

        assert output == (None, None, None, None)

    def test_records_missing_position(self):
        """Return test records missing position."""
        html = "Record: 5-0-0, 15 points (3.0 per game),  Premier League"

        output = self.team._records(html)

        assert output == ("5-0-0", "15", None, "Premier League")

    def test_goals_missing(self):
        """Return test goals missing."""
        html = "Goals: 20 (2.5 per game), Goals Against: 11 (1.38 per game)"

        output = self.team._goals(html)

        assert output == (None, None, None)

    def test_expected_goals(self):
        """Return test expected goals."""
        html = "xG: 19.3, xGA: 12.1"

        output = self.team._parse_expected_goals(html)

        assert output == (None, None, None)

    def test_missing_home_games_returns_none(self):
        """Return test missing home games returns none."""
        output = self.team.home_games

        assert not output

    def test_missing_away_games_returns_none(self):
        """Return test missing away games returns none."""
        output = self.team.away_games

        assert not output

    def test_invalid_home_wins_returns_none(self):
        """Return test invalid home wins returns none."""
        self.team._home_record = "a-0-0"

        output = self.team.home_wins

        assert not output

    def test_invalid_home_draws_returns_none(self):
        """Return test invalid home draws returns none."""
        self.team._home_record = "5-a-0"

        output = self.team.home_draws

        assert not output

    def test_missing_home_draws_returns_none(self):
        """Return test missing home draws returns none."""
        self.team._home_record = "5"

        output = self.team.home_draws

        assert not output

    def test_invalid_home_losses_returns_none(self):
        """Return test invalid home losses returns none."""
        self.team._home_record = "5-0-a"

        output = self.team.home_losses

        assert not output

    def test_missing_home_losses_returns_none(self):
        """Return test missing home losses returns none."""
        self.team._home_record = "5-0"

        output = self.team.home_losses

        assert not output

    def test_invalid_home_record_returns_none_for_losses(self):
        """Return test invalid home record returns none for losses."""
        self.team._home_record = None

        output = self.team.home_losses

        assert not output

    def test_invalid_away_wins_returns_none(self):
        """Return test invalid away wins returns none."""
        self.team._away_record = "a-0-0"

        output = self.team.away_wins

        assert not output

    def test_missing_away_draws_returns_none(self):
        """Return test missing away draws returns none."""
        self.team._away_record = "5"

        output = self.team.away_draws

        assert not output

    def test_invalid_away_draws_returns_none(self):
        """Return test invalid away draws returns none."""
        self.team._away_record = "5-a-0"

        output = self.team.away_draws

        assert not output

    def test_missing_away_losses_returns_none(self):
        """Return test missing away losses returns none."""
        self.team._away_record = "5-0"

        output = self.team.away_losses

        assert not output

    def test_invalid_away_losses_returns_none(self):
        """Return test invalid away losses returns none."""
        self.team._away_record = "5-0-a"

        output = self.team.away_losses

        assert not output

    def test_invalid_away_record_returns_none_for_losses(self):
        """Return test invalid away record returns none for losses."""
        self.team._away_record = None

        output = self.team.away_losses

        assert not output

    def test_fb_schedule_returns_schedule(self):
        """Return test fb schedule returns schedule."""
        self.team._doc = None

        assert len(self.team.schedule) == 0

    def test_fb_no_doc_returns_schedule(self):
        """Return test fb no doc returns schedule."""
        flexmock(Team).should_receive("__init__").and_return(None)

        team = Team("Tottenham Hotspur")
        team._squad_id = "361ca564"

        assert len(team.schedule) == 0

    def test_fb_roster_returns_roster(self):
        """Return test fb roster returns roster."""
        self.team._doc = None

        assert len(self.team.roster) == 0

    def test_fb_no_doc_returns_roster(self):
        """Return test fb no doc returns roster."""
        flexmock(Team).should_receive("__init__").and_return(None)

        team = Team("Tottenham Hotspur")
        team._squad_id = "361ca564"

        assert len(team.roster) == 0


class TestFBTeamInvalidPage:
    """Represent TestFBTeamInvalidPage."""

    @mock.patch("requests.get", side_effect=mock_httperror)
    def test_invalid_http_page_error(self, *args, **kwargs):
        """Return test invalid http page error."""
        flexmock(Team).should_receive("__init__").and_return(None)
        team = Team(None)
        team._squad_id = ""

        assert not team._pull_team_page()
