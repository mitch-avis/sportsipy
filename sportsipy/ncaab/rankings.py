"""Provide utilities for rankings."""

from __future__ import annotations

import re
from typing import Any
from urllib.error import HTTPError

from sportsipy import utils
from sportsipy.ncaab.constants import RANKINGS_URL


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
        return "NCAAB Rankings"

    def __repr__(self) -> str:
        """Return the string representation of the class."""
        return self.__str__()

    def _pull_rankings_page(self, year: int | str | None) -> Any | None:
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
            return utils.pq(page_source)
        except HTTPError:
            return None

    def _parse_table_columns(self, page: Any) -> dict[int, dict[str, str]]:
        """Build metadata for each week column in the rankings table."""
        header_rows = page("table#ap-polls thead tr")
        collapsed_header = header_rows.eq(2)
        columns = {}
        for th in collapsed_header("th").items():
            data_stat = th.attr("data-stat")
            if not data_stat or not data_stat.startswith("week"):
                continue
            try:
                week_number = int(data_stat.replace("week", ""))
            except ValueError:
                continue
            columns[week_number] = {
                "stat": data_stat,
                "date": th.text().strip() or "Final",
            }
        return dict(sorted(columns.items()))

    def _parse_team(self, row: Any) -> tuple[str | None, str | None]:
        link = row('th[data-stat="school"] a')
        if not link:
            return None, None
        href = link.attr("href") or ""
        abbreviation = re.sub(r".*/cbb/schools/", "", href)
        abbreviation = re.sub(r"/.*", "", abbreviation)
        name = link.text()
        return abbreviation, name

    def _parse_rank_cell(self, row: Any, data_stat: str) -> int | None:
        cell_text = row(f'td[data-stat="{data_stat}"]').text().strip()
        if not cell_text:
            return None
        try:
            return int(cell_text)
        except ValueError:
            return None

    def _previous_week(self, columns: dict[int, dict[str, str]], week_number: int) -> int | None:
        keys = sorted(columns.keys())
        try:
            index = keys.index(week_number)
        except ValueError:
            return None
        if index == 0:
            return None
        return keys[index - 1]

    def _build_entry(
        self,
        row: Any,
        week_number: int,
        columns: dict[int, dict[str, str]],
    ) -> dict[str, str | int] | None:
        abbreviation, name = self._parse_team(row)
        if not abbreviation or not name:
            return None
        rank = self._parse_rank_cell(row, columns[week_number]["stat"])
        if rank is None:
            return None
        prev_week = self._previous_week(columns, week_number)
        previous_rank = None
        if prev_week:
            previous_rank = self._parse_rank_cell(row, columns[prev_week]["stat"])
        change = 0
        if previous_rank is not None:
            change = previous_rank - rank
            previous_value = str(previous_rank)
        else:
            previous_value = ""
        return {
            "abbreviation": abbreviation,
            "name": name,
            "rank": rank,
            "week": week_number,
            "date": columns[week_number]["date"],
            "previous": previous_value,
            "change": change,
        }

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
            year = utils.find_year_for_season("ncaab")
            year = utils.resolve_year_for_url(year, lambda y: RANKINGS_URL % y)
        page = self._pull_rankings_page(year)
        if not page:
            output = (
                f"Can't pull rankings page. Ensure the following URL exists: {RANKINGS_URL % year}"
            )
            raise ValueError(output)

        columns = self._parse_table_columns(page)
        if not columns:
            return
        sorted_weeks = sorted(columns.keys())
        final_week = sorted_weeks[-1]
        previous_week = sorted_weeks[-2] if len(sorted_weeks) > 1 else None
        final_rankings = []
        previous_rankings = []
        rows = page("table#ap-polls tbody tr").items()
        for row in rows:
            final_entry = self._build_entry(row, final_week, columns)
            if final_entry:
                final_rankings.append(final_entry)
            if previous_week:
                previous_entry = self._build_entry(row, previous_week, columns)
                if previous_entry:
                    previous_rankings.append(previous_entry)
        if final_rankings:
            self._rankings[final_week] = sorted(final_rankings, key=lambda item: item["rank"])
        if previous_rankings:
            self._rankings[previous_week] = sorted(previous_rankings, key=lambda item: item["rank"])

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
                week number, ie 19 (int): [
                    {
                        'abbreviation': Team's abbreviation, such as 'PURDUE'
                                        (str),
                        'name': Team's full name, such as 'Purdue' (str),
                        'rank': Team's rank for the current week (int),
                        'week': Week number for the results, such as 19 (int),
                        'date': Date the rankings were released, such as
                                '2017-03-01'. Can also be 'Final' for the final
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
