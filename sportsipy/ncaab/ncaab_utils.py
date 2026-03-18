"""Provide utilities for ncaab utils."""

from __future__ import annotations

from typing import Any

from sportsipy import utils
from sportsipy.ncaab.constants import (
    ADVANCED_OPPONENT_STATS_URL,
    ADVANCED_STATS_URL,
    BASIC_OPPONENT_STATS_URL,
    BASIC_STATS_URL,
    PARSING_SCHEME,
)


def _add_stats_data(
    teams_list: Any,
    team_data_dict: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Add a team's stats row to a dictionary.

    Pass table contents and a stats dictionary of all teams to accumulate all
    stats for each team in a single variable.

    Parameters
    ----------
    teams_list : generator
        A generator of all row items in a given table.
    team_data_dict : {str: {'data': str}} dictionary
        A dictionary where every key is the team's abbreviation and every value
        is another dictionary with a 'data' key which contains the string
        version of the row data for the matched team.

    Returns
    -------
    dictionary
        An updated version of the team_data_dict with the passed table row
        information included.

    """
    for team_data in teams_list:
        if 'class="over_header thead"' in str(team_data) or 'class="thead"' in str(team_data):
            continue
        abbr = utils.parse_field(PARSING_SCHEME, team_data, "abbreviation")
        if not isinstance(abbr, str):
            continue
        row_html = str(team_data)
        try:
            team_data_dict[abbr]["data"] += row_html
        except KeyError:
            team_data_dict[abbr] = {"data": row_html}
    return team_data_dict


def _retrieve_all_teams(
    year: int | str | None,
    basic_stats: str | None = None,
    basic_opp_stats: str | None = None,
    adv_stats: str | None = None,
    adv_opp_stats: str | None = None,
) -> tuple[dict[str, dict[str, Any]] | None, int | str | None]:
    """Find and create Team instances for all teams in the given season.

    For a given season, parses the specified NCAAB stats table and finds all
    requested stats. Each team then has a Team instance created which includes
    all requested stats and a few identifiers, such as the team's name and
    abbreviation. All of the individual Team instances are added to a list.

    Note that this method is called directly once Teams is invoked and does not
    need to be called manually.

    Parameters
    ----------
    year : string
        The requested year to pull stats from.
    basic_stats : string (optional)
        Link with filename to the local basic stats page.
    basic_opp_stats : string (optional)
        Link with filename to the local basic opponent stats page.
    adv_stats : string (optional)
        Link with filename to the local advanved stats page.
    adv_opp_stats : string (optional)
        Link with filename to the local advanced opponents stats page.

    Returns
    -------
    tuple
        Returns a ``tuple`` of the team_data_dict and year which represent all
        stats for all teams, and the given year that should be used to pull
        stats from, respectively.

    """
    team_data_dict = {}

    if not year:
        year = utils.find_year_for_season("ncaab")
        year = utils.resolve_year_for_url(year, lambda y: BASIC_STATS_URL % y)
    doc = utils.pull_page(BASIC_STATS_URL % year, basic_stats)
    teams_list = utils.get_stats_table(doc, "table#basic_school_stats")
    if not teams_list:
        teams_list = utils.get_stats_table(doc, "div#all_basic_school_stats")

    doc = utils.pull_page(BASIC_OPPONENT_STATS_URL % year, basic_opp_stats)
    opp_list = utils.get_stats_table(doc, "table#basic_opp_stats")
    if not opp_list:
        opp_list = utils.get_stats_table(doc, "div#all_basic_opp_stats")

    doc = utils.pull_page(ADVANCED_STATS_URL % year, adv_stats)
    adv_teams_list = utils.get_stats_table(doc, "table#adv_school_stats")
    if not adv_teams_list:
        adv_teams_list = utils.get_stats_table(doc, "div#all_adv_school_stats")

    doc = utils.pull_page(ADVANCED_OPPONENT_STATS_URL % year, adv_opp_stats)
    adv_opp_list = utils.get_stats_table(doc, "table#adv_opp_stats")
    if not adv_opp_list:
        adv_opp_list = utils.get_stats_table(doc, "div#all_adv_opp_stats")
    if not teams_list and not opp_list and not adv_teams_list and not adv_opp_list:
        utils.no_data_found()
        return None, None
    for stats_list in [teams_list, opp_list, adv_teams_list, adv_opp_list]:
        team_data_dict = _add_stats_data(stats_list, team_data_dict)
    return team_data_dict, year
