"""Provide utilities for test fb utils."""

import pytest

from sportsipy.fb.fb_utils import _lookup_team, _parse_squad_name, lookup_squad_id


class TestFBUtils:
    """Represent TestFBUtils."""

    def test_squad_name_parsing(self):
        """Return test squad name parsing."""
        test_names = {
            "FC Barcelona": "barcelona",
            "Tottenham Hotspur": "tottenham hotspur",
            "Inter Miami CF": "inter miami",
        }

        for input_name, expected_name in test_names.items():
            result = _parse_squad_name(input_name)
            assert result == expected_name

    def test_squad_lookup_doesnt_suppress(self):
        """Return test squad lookup doesnt suppress."""
        output = lookup_squad_id("madeup city")

        assert isinstance(output, dict)

    def test_team_name_lookup(self):
        """Return test team name lookup."""
        test_names = {
            "Tottenham Hotspur": "361ca564",
            "tottenham hotspur": "361ca564",
            "361ca564": "361ca564",
            "361CA564": "361ca564",
        }

        for input_name, squad_id in test_names.items():
            result = _lookup_team(input_name)
            assert result == squad_id

    def test_team_name_lookup_no_match(self):
        """Return test team name lookup no match."""
        with pytest.raises(ValueError):
            _ = _lookup_team("noteamname")
