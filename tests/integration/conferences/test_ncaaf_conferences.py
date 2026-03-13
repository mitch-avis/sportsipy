"""Provide utilities for test ncaaf conferences."""

from os.path import dirname, join

import pytest
from flexmock import flexmock

from sportsipy import utils
from sportsipy.ncaaf.conferences import Conference, Conferences

YEAR = 2018


def read_file(filename):
    """Return read file."""
    filepath = join(dirname(__file__), "ncaaf", filename)
    return open(filepath, encoding="utf8").read()


def mock_pyquery(url, timeout=None):
    """Return mock pyquery."""

    class MockPQ:
        def __init__(self, html_contents, status_code=200):
            self.url = url
            self.reason = "Bad URL"  # Used when throwing HTTPErrors
            self.headers = {}  # Used when throwing HTTPErrors
            self.status_code = status_code
            self.html_contents = html_contents
            self.text = html_contents

        def __call__(self, div):
            return read_file(None)

    if "BAD" in url:
        return MockPQ("", 404)
    if "acc" in url:
        html_contents = read_file(f"{YEAR}-acc.html")
        return MockPQ(html_contents)
    if "sec" in url:
        html_contents = read_file(f"{YEAR}-sec.html")
        return MockPQ(html_contents)
    html_contents = read_file(f"{YEAR}.html")
    return MockPQ(html_contents)


def mock_request(url, timeout=None):
    """Return mock request."""

    class MockRequest:
        def __init__(self, html_contents, status_code=200):
            self.status_code = status_code
            self.html_contents = html_contents
            self.text = html_contents

    if str(YEAR) in url:
        return MockRequest("good")
    return MockRequest("bad", status_code=404)


class TestNCAAFConferences:
    """Represent TestNCAAFConferences."""

    def setup_method(self):
        """Return setup method."""
        team_conference = {
            "florida-state": "acc",
            "boston-college": "acc",
            "clemson": "acc",
            "north-carolina-state": "acc",
            "syracuse": "acc",
            "wake-forest": "acc",
            "louisville": "acc",
            "virginia-tech": "acc",
            "duke": "acc",
            "georgia-tech": "acc",
            "pittsburgh": "acc",
            "virginia": "acc",
            "miami-fl": "acc",
            "north-carolina": "acc",
            "florida": "sec",
            "georgia": "sec",
            "kentucky": "sec",
            "missouri": "sec",
            "south-carolina": "sec",
            "vanderbilt": "sec",
            "tennessee": "sec",
            "alabama": "sec",
            "arkansas": "sec",
            "auburn": "sec",
            "louisiana-state": "sec",
            "mississippi-state": "sec",
            "mississippi": "sec",
            "texas-am": "sec",
        }
        conferences_result = {
            "acc": {
                "name": "Atlantic Coast Conference",
                "teams": {
                    "florida-state": "Florida State",
                    "boston-college": "Boston College",
                    "clemson": "Clemson",
                    "north-carolina-state": "North Carolina State",
                    "syracuse": "Syracuse",
                    "wake-forest": "Wake Forest",
                    "louisville": "Louisville",
                    "virginia-tech": "Virginia Tech",
                    "duke": "Duke",
                    "georgia-tech": "Georgia Tech",
                    "pittsburgh": "Pitt",
                    "virginia": "Virginia",
                    "miami-fl": "Miami (FL)",
                    "north-carolina": "North Carolina",
                },
            },
            "sec": {
                "name": "Southeastern Conference",
                "teams": {
                    "florida": "Florida",
                    "georgia": "Georgia",
                    "kentucky": "Kentucky",
                    "missouri": "Missouri",
                    "south-carolina": "South Carolina",
                    "vanderbilt": "Vanderbilt",
                    "tennessee": "Tennessee",
                    "alabama": "Alabama",
                    "arkansas": "Arkansas",
                    "auburn": "Auburn",
                    "louisiana-state": "LSU",
                    "mississippi-state": "Mississippi State",
                    "mississippi": "Ole Miss",
                    "texas-am": "Texas A&M",
                },
            },
        }
        self.team_conference = team_conference
        self.conferences_result = conferences_result

    def test_conferences_integration(self, *args, **kwargs):
        """Return test conferences integration."""
        flexmock(utils).should_receive("find_year_for_season").and_return(YEAR)

        conferences = Conferences()

        assert conferences.team_conference == self.team_conference
        assert conferences.conferences == self.conferences_result

    def test_conferences_integration_bad_url(self, *args, **kwargs):
        """Return test conferences integration bad url."""
        with pytest.raises(ValueError):
            Conferences("BAD")

    def test_conference_integration_bad_url(self, *args, **kwargs):
        """Return test conference integration bad url."""
        with pytest.raises(ValueError):
            Conference("BAD")

    def test_conference_with_no_names_is_empty(self, *args, **kwargs):
        """Return test conference with no names is empty."""
        flexmock(Conference).should_receive("_get_team_abbreviation").and_return("")

        conference = Conference("acc")

        assert len(conference._teams) == 0

    def test_invalid_default_year_reverts_to_previous_year(self, *args, **kwargs):
        """Return test invalid default year reverts to previous year."""
        flexmock(utils).should_receive("find_year_for_season").and_return(2019)

        conferences = Conferences()

        assert conferences.team_conference == self.team_conference
        assert conferences.conferences == self.conferences_result

    def test_invalid_conference_year_reverts_to_previous_year(self, *args, **kwargs):
        """Return test invalid conference year reverts to previous year."""
        flexmock(utils).should_receive("find_year_for_season").and_return(2019)

        conference = Conference("acc")

        assert len(conference._teams) == 14

    def test_invalid_conference_page_skips_error(self, *args, **kwargs):
        """Return test invalid conference page skips error."""
        Conference("BAD", ignore_missing=True)

    def test_conferences_string_representation(self, *args, **kwargs):
        """Return test conferences string representation."""
        conferences = Conferences()

        assert repr(conferences) == "NCAAF Conferences"

    def test_conference_string_representation(self, *args, **kwargs):
        """Return test conference string representation."""
        conference = Conference("acc")

        assert repr(conference) == "acc - NCAAF"
