"""Provide utilities for rankings."""

from __future__ import annotations

import re
from typing import Any
from urllib.error import HTTPError

from pyquery import PyQuery

from sportsipy import utils
from sportsipy.ncaaf.constants import (
    CFP_RANKINGS_URL,
    COACHES_RANKINGS_URL,
    RANKINGS_SCHEME,
    RANKINGS_URL,
)


class Rankings:
    """Get all Associated Press (AP) rankings on a week-by-week basis.

    Grab a list of the rankings published by the Associated Press to easily
    query the hierarchy of teams each week. The results expose the current and
    previous rankings as well as the movement for each team in the list.

    Parameters
    ----------
    year : string (optional)
        A string of the requested year to pull rankings from. Defaults to the
        most recent season.

    """

    def __init__(self, year: int | str | None = None) -> None:
        """Initialize the class instance."""
        self._rankings = {}

        self._find_rankings(year)

    def __str__(self) -> str:
        """Return the string representation of the class."""
        return "NCAAF Rankings"

    def __repr__(self) -> str:
        """Return the string representation of the class."""
        return self.__str__()

    def _pull_rankings_page(self, year: int | str | None) -> PyQuery | None:
        """Download the rankings page.

        Download the rankings page for the requested year and create a PyQuery
        object.

        Parameters
        ----------
        year : string
            A string of the requested year to pull rankings from.

        Returns
        -------
        PyQuery object
            Returns a PyQuery object of the rankings HTML page.

        """
        try:
            page_source = utils.get_page_source(url=RANKINGS_URL % year)
            if not page_source:
                return None
            url_data = utils.pq(page_source)
            return PyQuery(utils.remove_html_comment_tags(url_data))
        except HTTPError:
            return None

    def _get_team(self, team: PyQuery) -> tuple[str, str]:
        """Retrieve team's name and abbreviation.

        The team's name and abbreviation are embedded within the 'school_name'
        tag and, in the case of the abbreviation, require special parsing as it
        is located in the middle of a URI. The name and abbreviation are
        returned for the requested school.

        Parameters
        ----------
        team : PyQuery object
            A PyQuery object representing a single row in a table on the
            rankings page.

        Returns
        -------
        tuple (string, string)
            Returns a tuple of two strings where the first string is the team's
            abbreviation, such as 'PURDUE' and the second string is the team's
            name, such as 'Purdue'.

        """
        link = team('td[data-stat="school_name"] a')
        href = str(link.attr("href") or "")
        abbreviation = re.sub(r".*/cfb/schools/", "", href)
        abbreviation = re.sub(r"/.*", "", abbreviation)
        name = str(link.text() or "")
        return abbreviation, name

    def _find_rankings(self, year: int | str | None) -> None:
        """Retrieve the rankings for each week.

        Find and retrieve all AP rankings for the requested year and combine
        them on a per-week basis. Each week contains information about the
        name, abbreviation, rank, movement, and previous rank for each team
        as well as the date and week number the results were published on.

        Parameters
        ----------
        year : string
            A string of the requested year to pull rankings from.

        """
        if not year:
            year = utils.find_year_for_season("ncaaf")
            year = utils.resolve_year_for_url(year, lambda y: RANKINGS_URL % y)
        page = self._pull_rankings_page(year)
        if not page:
            output = (
                f"Can't pull rankings page. Ensure the following URL exists: {RANKINGS_URL % year}"
            )
            raise ValueError(output)

        def _safe_int(value, default=0):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        rankings = page("table#ap tbody tr").items()
        weekly_rankings = []
        week_value = 0
        for team in rankings:
            if 'class="thead"' in str(team):
                self._rankings[week_value] = weekly_rankings
                weekly_rankings = []
                continue
            abbreviation, name = self._get_team(team)
            rank = utils.parse_field(RANKINGS_SCHEME, team, "rank")
            week = utils.parse_field(RANKINGS_SCHEME, team, "week")
            date = utils.parse_field(RANKINGS_SCHEME, team, "date")
            previous = utils.parse_field(RANKINGS_SCHEME, team, "previous")
            change = utils.parse_field(RANKINGS_SCHEME, team, "change")
            week_value = _safe_int(week)
            rank_value = _safe_int(rank)
            change_value = _safe_int(change)
            if "decrease" in str(team(RANKINGS_SCHEME["change"])):
                change_value = change_value * -1
            elif "increase" in str(team(RANKINGS_SCHEME["change"])):
                change_value = change_value
            else:
                change_value = 0
            rank_details = {
                "abbreviation": abbreviation,
                "name": name,
                "rank": rank_value,
                "week": week_value,
                "date": date,
                "previous": previous,
                "change": change_value,
            }
            weekly_rankings.append(rank_details)
        # Add the final rankings which is not terminated with another header
        # row and hence will not hit the first if statement in the loop above.
        self._rankings[week_value] = weekly_rankings

    @property
    def current_extended(self) -> Any:
        """Return a ``list`` of ``dictionaries`` of the most recent AP rankings.

        The list is ordered in terms of the ranking so the #1 team will be in
        the first element and the #25 team will be the last element. Each
        dictionary has the following structure::

            {
                'abbreviation': Team's abbreviation, such as 'PURDUE' (str),
                'name': Team's full name, such as 'Purdue' (str),
                'rank': Team's rank for the current week (int),
                'week': Week number for the results, such as 19 (int),
                'date': Date the rankings were released, such as '2017-03-01'.
                        Can also be 'Final' for the final rankings or
                        'Preseason' for preseason rankings (str),
                'previous': The team's previous rank, if applicable (str),
                'change': The amount the team moved up or down the rankings.
                          Moves up the ladder have a positive number while
                          drops yield a negative number and teams that didn't
                          move have 0 (int)
            }
        """
        latest_week = max(self._rankings.keys())
        ordered_dict = sorted(self._rankings[latest_week], key=lambda k: k["rank"])
        return ordered_dict

    @property
    def current(self) -> Any:
        """Return a ``dictionary`` of the most recent rankings from the.

        Associated Press where each key is a ``string`` of the team's
        abbreviation and each value is an ``int`` of the team's rank for the
        current week.
        """
        rankings_dict = {}

        for team in self.current_extended:
            rankings_dict[team["abbreviation"]] = team["rank"]
        return rankings_dict

    @property
    def complete(self) -> Any:
        """Return a ``dictionary`` where each key is a week number as an ``int``.

        and each value is a ``list`` of ``dictionaries`` containing the AP
        rankings for each week. Within each list is a dictionary of team
        information such as name, abbreviation, rank, and more. Note that the
        list might not necessarily be in the same order as the rankings.

        The overall dictionary has the following structure::

            {
                week number, ie 16 (int): [
                    {
                        'abbreviation': Team's abbreviation, such as 'PURDUE'
                                        (str),
                        'name': Team's full name, such as 'Purdue' (str),
                        'rank': Team's rank for the current week (int),
                        'week': Week number for the results, such as 16 (int),
                        'date': Date the rankings were released, such as
                                '2017-12-03'. Can also be 'Final' for the final
                                rankings or 'Preseason' for preseason rankings
                                (str),
                        'previous': The team's previous rank, if applicable
                                    (str),
                        'change': The amount the team moved up or down the
                                  rankings. Moves up the ladder have a positive
                                  number while drops yield a negative number
                                  and teams that didn't move have 0 (int)
                    },
                    ...
                ],
                ...
            }
        """
        return self._rankings


class CFPRankings:
    """Get all College Football Playoff (CFP) rankings on a week-by-week basis.

    Grab a list of the official College Football Playoff rankings once
    available to easily determine the latest standings in the race to the
    College Football Playoffs. The results expose the current and previous
    rankings as well as the movement for each team in the list.

    Parameters
    ----------
    year : string (optional)
        A string of the requested year to pull rankings from. Defaults to the
        most recent season.

    """

    def __init__(self, year: int | str | None = None) -> None:
        """Initialize the class instance."""
        self._rankings = {}

        self._find_rankings(year)

    def __str__(self) -> str:
        """Return the string representation of the class."""
        return "NCAAF CFP Rankings"

    def __repr__(self) -> str:
        """Return the string representation of the class."""
        return self.__str__()

    def _pull_rankings_page(self, year: int | str | None) -> PyQuery | None:
        """Download the rankings page.

        Download the rankings page for the requested year and create a PyQuery
        object.

        Parameters
        ----------
        year : string
            A string of the requested year to pull rankings from.

        Returns
        -------
        PyQuery object
            Returns a PyQuery object of the rankings HTML page.

        """
        try:
            page_source = utils.get_page_source(url=CFP_RANKINGS_URL % year)
            if not page_source:
                return None
            url_data = utils.pq(page_source)
            return PyQuery(utils.remove_html_comment_tags(url_data))
        except HTTPError:
            return None

    def _get_team(self, team: PyQuery) -> tuple[str, str]:
        """Retrieve team's name and abbreviation.

        The team's name and abbreviation are embedded within the 'school_name'
        tag and, in the case of the abbreviation, require special parsing as it
        is located in the middle of a URI. The name and abbreviation are
        returned for the requested school.

        Parameters
        ----------
        team : PyQuery object
            A PyQuery object representing a single row in a table on the
            rankings page.

        Returns
        -------
        tuple (string, string)
            Returns a tuple of two strings where the first string is the team's
            abbreviation, such as 'PURDUE' and the second string is the team's
            name, such as 'Purdue'.

        """
        link = team('td[data-stat="school_name"] a')
        href = str(link.attr("href") or "")
        abbreviation = re.sub(r".*/cfb/schools/", "", href)
        abbreviation = re.sub(r"/.*", "", abbreviation)
        name = str(link.text() or "")
        return abbreviation, name

    def _find_rankings(self, year: int | str | None) -> None:
        """Retrieve the rankings for each week.

        Find and retrieve all CFP rankings for the requested year and combine
        them on a per-week basis. Each week contains information about the
        name, abbreviation, rank, movement, and previous rank for each team
        as well as the date and week number the results were published on.

        Parameters
        ----------
        year : string
            A string of the requested year to pull rankings from.

        """
        if not year:
            year = utils.find_year_for_season("ncaaf")
            year = utils.resolve_year_for_url(year, lambda y: CFP_RANKINGS_URL % y)
        page = self._pull_rankings_page(year)
        if not page:
            output = (
                "Can't pull rankings page. Ensure the following URL exists: "
                f"{CFP_RANKINGS_URL % year}"
            )
            raise ValueError(output)

        def _safe_int(value, default=0):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        rankings = page("table#cfbplayoff tbody tr").items()
        weekly_rankings = []
        week_value = 0
        for team in rankings:
            if 'class="thead"' in str(team):
                self._rankings[week_value] = weekly_rankings
                weekly_rankings = []
                continue
            abbreviation, name = self._get_team(team)
            rank = utils.parse_field(RANKINGS_SCHEME, team, "rank")
            week = utils.parse_field(RANKINGS_SCHEME, team, "week")
            date = utils.parse_field(RANKINGS_SCHEME, team, "date")
            previous = utils.parse_field(RANKINGS_SCHEME, team, "previous")
            change = utils.parse_field(RANKINGS_SCHEME, team, "change")
            week_value = _safe_int(week)
            rank_value = _safe_int(rank)
            change_value = _safe_int(change)
            if "decrease" in str(team(RANKINGS_SCHEME["change"])):
                change_value = change_value * -1
            elif "increase" in str(team(RANKINGS_SCHEME["change"])):
                change_value = change_value
            else:
                change_value = 0
            rank_details = {
                "abbreviation": abbreviation,
                "name": name,
                "rank": rank_value,
                "week": week_value,
                "date": date,
                "previous": previous,
                "change": change_value,
            }
            weekly_rankings.append(rank_details)
        # Add the final rankings which is not terminated with another header
        # row and hence will not hit the first if statement in the loop above.
        self._rankings[week_value] = weekly_rankings

    @property
    def current_extended(self) -> Any:
        """Return a ``list`` of ``dictionaries`` of the most recent CFP rankings.

        The list is ordered in terms of the ranking so the #1 team will be in
        the first element and the #25 team will be the last element. Each
        dictionary has the following structure::

            {
                'abbreviation': Team's abbreviation, such as 'PURDUE' (str),
                'name': Team's full name, such as 'Purdue' (str),
                'rank': Team's rank for the current week (int),
                'week': Week number for the results, such as 19 (int),
                'date': Date the rankings were released, such as '2017-03-01'.
                        Can also be 'Final' for the final rankings or
                        'Preseason' for preseason rankings (str),
                'previous': The team's previous rank, if applicable (str),
                'change': The amount the team moved up or down the rankings.
                          Moves up the ladder have a positive number while
                          drops yield a negative number and teams that didn't
                          move have 0 (int)
            }
        """
        latest_week = max(self._rankings.keys())
        ordered_dict = sorted(self._rankings[latest_week], key=lambda k: k["rank"])
        return ordered_dict

    @property
    def current(self) -> Any:
        """Return a ``dictionary`` of the most recent CFP rankings where.

        each key is a ``string`` of the team's abbreviation and each
        value is an ``int`` of the team's rank for the current week.
        """
        rankings_dict = {}

        for team in self.current_extended:
            rankings_dict[team["abbreviation"]] = team["rank"]
        return rankings_dict

    @property
    def complete(self) -> Any:
        """Return a ``dictionary`` where each key is a week number as an ``int``.

        and each value is a ``list`` of ``dictionaries`` containing the CFP
        rankings for each week. Within each list is a dictionary of team
        information such as name, abbreviation, rank, and more. Note that the
        list might not necessarily be in the same order as the rankings.

        The overall dictionary has the following structure::

            {
                week number, ie 16 (int): [
                    {
                        'abbreviation': Team's abbreviation, such as 'PURDUE'
                                        (str),
                        'name': Team's full name, such as 'Purdue' (str),
                        'rank': Team's rank for the current week (int),
                        'week': Week number for the results, such as 16 (int),
                        'date': Date the rankings were released, such as
                                '2017-12-03'. Can also be 'Final' for the final
                                rankings or 'Preseason' for preseason rankings
                                (str),
                        'previous': The team's previous rank, if applicable
                                    (str),
                        'change': The amount the team moved up or down the
                                  rankings. Moves up the ladder have a positive
                                  number while drops yield a negative number
                                  and teams that didn't move have 0 (int)
                    },
                    ...
                ],
                ...
            }
        """
        return self._rankings


class CoachesRankings:
    """Get all Coaches Poll (USA Today) rankings on a week-by-week basis.

    Grab a list of the rankings published by USA Today to easily query
    the hierarchy of teams each week. The results expose the current and
    previous rankings as well as the movement for each team in the list.

    Parameters
    ----------
    year : string (optional)
        A string of the requested year to pull rankings from. Defaults to the
        most recent season.

    """

    def __init__(self, year: int | str | None = None) -> None:
        """Initialize the class instance."""
        self._rankings = {}

        self._find_rankings(year)

    def __str__(self) -> str:
        """Return the string representation of the class."""
        return "NCAAF Coaches Rankings"

    def __repr__(self) -> str:
        """Return the string representation of the class."""
        return self.__str__()

    def _pull_rankings_page(self, year: int | str | None) -> PyQuery | None:
        """Download the rankings page.

        Download the rankings page for the requested year and create a PyQuery
        object.

        Parameters
        ----------
        year : string
            A string of the requested year to pull rankings from.

        Returns
        -------
        PyQuery object
            Returns a PyQuery object of the rankings HTML page.

        """
        try:
            page_source = utils.get_page_source(url=COACHES_RANKINGS_URL % year)
            if not page_source:
                return None
            url_data = utils.pq(page_source)
            return PyQuery(utils.remove_html_comment_tags(url_data))
        except HTTPError:
            return None

    def _get_team(self, team: PyQuery) -> tuple[str, str]:
        """Retrieve team's name and abbreviation.

        The team's name and abbreviation are embedded within the 'school_name'
        tag and, in the case of the abbreviation, require special parsing as it
        is located in the middle of a URI. The name and abbreviation are
        returned for the requested school.

        Parameters
        ----------
        team : PyQuery object
            A PyQuery object representing a single row in a table on the
            rankings page.

        Returns
        -------
        tuple (string, string)
            Returns a tuple of two strings where the first string is the team's
            abbreviation, such as 'PURDUE' and the second string is the team's
            name, such as 'Purdue'.

        """
        link = team('td[data-stat="school_name"] a')
        href = str(link.attr("href") or "")
        abbreviation = re.sub(r".*/cfb/schools/", "", href)
        abbreviation = re.sub(r"/.*", "", abbreviation)
        name = str(link.text() or "")
        return abbreviation, name

    def _find_rankings(self, year: int | str | None) -> None:
        """Retrieve the rankings for each week.

        Find and retrieve all Coaches Poll rankings for the requested year and
        combine them on a per-week basis. Each week contains information about
        the name, abbreviation, rank, movement, and previous rank for each team
        as well as the date and week number the results were published on.

        Parameters
        ----------
        year : string
            A string of the requested year to pull rankings from.

        """
        if not year:
            year = utils.find_year_for_season("ncaaf")
            year = utils.resolve_year_for_url(year, lambda y: COACHES_RANKINGS_URL % y)
        page = self._pull_rankings_page(year)
        if not page:
            output = (
                "Can't pull rankings page. Ensure the following URL exists: "
                f"{COACHES_RANKINGS_URL % year}"
            )
            raise ValueError(output)

        def _safe_int(value, default=0):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        rankings = page("table#usatoday tbody tr").items()
        weekly_rankings = []
        week_value = 0
        for team in rankings:
            if 'class="thead"' in str(team):
                self._rankings[week_value] = weekly_rankings
                weekly_rankings = []
                continue
            abbreviation, name = self._get_team(team)
            rank = utils.parse_field(RANKINGS_SCHEME, team, "rank")
            week = utils.parse_field(RANKINGS_SCHEME, team, "week")
            date = utils.parse_field(RANKINGS_SCHEME, team, "date")
            previous = utils.parse_field(RANKINGS_SCHEME, team, "previous")
            change = utils.parse_field(RANKINGS_SCHEME, team, "change")
            week_value = _safe_int(week)
            rank_value = _safe_int(rank)
            change_value = _safe_int(change)
            if "decrease" in str(team(RANKINGS_SCHEME["change"])):
                change_value = change_value * -1
            elif "increase" in str(team(RANKINGS_SCHEME["change"])):
                change_value = change_value
            else:
                change_value = 0
            rank_details = {
                "abbreviation": abbreviation,
                "name": name,
                "rank": rank_value,
                "week": week_value,
                "date": date,
                "previous": previous,
                "change": change_value,
            }
            weekly_rankings.append(rank_details)
        # Add the final rankings which is not terminated with another header
        # row and hence will not hit the first if statement in the loop above.
        self._rankings[week_value] = weekly_rankings

    @property
    def current_extended(self) -> Any:
        """Return a ``list`` of ``dictionaries`` of the most recent Coaches Poll.

        rankings. The list is ordered in terms of the ranking so the #1 team
        will be in the first element and the #25 team will be the last element.
        Each dictionary has the following structure::

            {
                'abbreviation': Team's abbreviation, such as 'PURDUE' (str),
                'name': Team's full name, such as 'Purdue' (str),
                'rank': Team's rank for the current week (int),
                'week': Week number for the results, such as 19 (int),
                'date': Date the rankings were released, such as '2017-03-01'.
                        Can also be 'Final' for the final rankings or
                        'Preseason' for preseason rankings (str),
                'previous': The team's previous rank, if applicable (str),
                'change': The amount the team moved up or down the rankings.
                          Moves up the ladder have a positive number while
                          drops yield a negative number and teams that didn't
                          move have 0 (int)
            }
        """
        latest_week = max(self._rankings.keys())
        ordered_dict = sorted(self._rankings[latest_week], key=lambda k: k["rank"])
        return ordered_dict

    @property
    def current(self) -> Any:
        """Return a ``dictionary`` of the most recent Coaches Poll.

        rankings where each key is a ``string`` of the team's
        abbreviation and each value is an ``int`` of the team's
        rank for the current week.
        """
        rankings_dict = {}

        for team in self.current_extended:
            rankings_dict[team["abbreviation"]] = team["rank"]
        return rankings_dict

    @property
    def complete(self) -> Any:
        """Return a ``dictionary`` where each key is a week number as an ``int``.

        and each value is a ``list`` of ``dictionaries`` containing the Coaches
        Poll rankings for each week. Within each list is a dictionary of team
        information such as name, abbreviation, rank, and more. Note that the
        list might not necessarily be in the same order as the rankings.

        The overall dictionary has the following structure::

            {
                week number, ie 16 (int): [
                    {
                        'abbreviation': Team's abbreviation, such as 'PURDUE'
                                        (str),
                        'name': Team's full name, such as 'Purdue' (str),
                        'rank': Team's rank for the current week (int),
                        'week': Week number for the results, such as 16 (int),
                        'date': Date the rankings were released, such as
                                '2017-12-03'. Can also be 'Final' for the final
                                rankings or 'Preseason' for preseason rankings
                                (str),
                        'previous': The team's previous rank, if applicable
                                    (str),
                        'change': The amount the team moved up or down the
                                  rankings. Moves up the ladder have a positive
                                  number while drops yield a negative number
                                  and teams that didn't move have 0 (int)
                    },
                    ...
                ],
                ...
            }
        """
        return self._rankings
