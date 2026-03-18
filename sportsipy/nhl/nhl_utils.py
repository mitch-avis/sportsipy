"""Provide utilities for nhl utils."""

from __future__ import annotations

from typing import Any

from sportsipy import utils
from sportsipy.nhl.constants import SEASON_PAGE_URL


def _retrieve_all_teams(
    year: int | str | None,
    season_page: str | None = None,
) -> tuple[Any | None, int | str | None]:
    """Find and create Team instances for all teams in the given season.

    For a given season, parses the specified NHL stats table and finds all
    requested stats. Each team then has a Team instance created which includes
    all requested stats and a few identifiers, such as the team's name and
    abbreviation. All of the individual Team instances are added to a list.

    Note that this method is called directly once Teams is invoked and does not
    need to be called manually.

    Parameters
    ----------
    year : string
        The requested year to pull stats from.
    season_page : string (optional)
        Link with filename to the local season page.

    Returns
    -------
    tuple
        Returns a ``tuple`` in the format of (teams_list, year) where the
        teams_list is the PyQuery data for every team in the given season, and
        the year is the request year for the season.

    """
    if not year:
        year = utils.find_year_for_season("nhl")
        year = utils.resolve_year_for_url(year, lambda y: SEASON_PAGE_URL % y)
    doc = utils.pull_page(SEASON_PAGE_URL % year, season_page)
    teams_list = utils.get_stats_table(doc, "div#all_stats")
    if not teams_list:
        utils.no_data_found()
        return None, None
    return teams_list, year
