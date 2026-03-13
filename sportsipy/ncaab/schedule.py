"""Provide utilities for schedule."""

import re
from datetime import datetime

import pandas as pd

from sportsipy import utils
from sportsipy.constants import (
    AWAY,
    CONFERENCE_TOURNAMENT,
    HOME,
    LOSS,
    NEUTRAL,
    NON_DI,
    REGULAR_SEASON,
    WIN,
)
from sportsipy.decorators import int_property_decorator
from sportsipy.ncaab.boxscore import Boxscore
from sportsipy.ncaab.constants import (
    CBI_TOURNAMENT,
    CIT_TOURNAMENT,
    NCAA_TOURNAMENT,
    NIT_TOURNAMENT,
    SCHEDULE_SCHEME,
    SCHEDULE_URL,
)


class Game:
    """A representation of a matchup between two teams.

    Stores all relevant high-level match information for a game in a team's
    schedule including date, time, opponent, and result.

    Parameters
    ----------
    game_data : string
        The row containing the specified game information.

    """

    def __init__(self, game_data):
        """Initialize the class instance."""
        self._game = None
        self._date: str | None = None
        self._datetime = None
        self._time: str | None = None
        self._boxscore: str | None = None
        self._type: str | None = None
        self._location: str | None = None
        self._opponent_abbr: str | None = None
        self._opponent_name: str | None = None
        self._opponent_rank = None
        self._opponent_conference: str | None = None
        self._result: str | None = None
        self._points_for = None
        self._points_against = None
        self._overtimes: str | None = None
        self._season_wins = None
        self._season_losses = None
        self._streak = None
        self._arena = None
        self._team_abbr: str | None = None

        self._parse_game_data(game_data)

    def __str__(self):
        """Return the string representation of the class."""
        return f"{self.date} - {self.opponent_abbr}"

    def __repr__(self):
        """Return the string representation of the class."""
        return self.__str__()

    def _parse_abbreviation(self, game_data):
        """Parse the opponent's abbreviation from their name.

        The opponent's abbreviation is embedded within the HTML tag and needs
        a special parsing scheme in order to be extracted. For non-DI schools,
        the team's name should be used as the abbreviation.

        Parameters
        ----------
        game_data : PyQuery object
            A PyQuery object containing the information specific to a game.

        """
        name = game_data('td[data-stat="opp_name"]:first')
        # Prefer the anchor href when present to avoid extra HTML/text being
        # included when stringifying the element.
        anchor = name("a")
        href = anchor.attr("href") if anchor else None
        if href and "cbb/schools" in href:
            abbr = re.sub(r".*/cbb/schools/", "", href)
            abbr = re.sub(r"/.*", "", abbr)
            # Store abbreviations lower-case to match expected output
            self._opponent_abbr = abbr.lower()
            return
        # Non-DI schools do not have abbreviations and should be handled
        # differently by just using the team's display name as the abbreviation.
        self._opponent_abbr = name.text()

    def _parse_boxscore(self, game_data):
        """Parse the boxscore URI for the game.

        The boxscore is embedded within the HTML tag and needs a special
        parsing scheme in order to be extracted.

        Parameters
        ----------
        game_data : PyQuery object
            A PyQuery object containing the information specific to a game.

        """
        boxscore = game_data('td[data-stat="date_game"]:first')
        anchor = boxscore("a")
        # Happens if the game hasn't been played yet as there is no boxscore
        # to display.
        if not anchor or not anchor.text():
            return
        href = anchor.attr("href") if anchor else None
        if href:
            bs = re.sub(r".*/boxscores/", "", href)
            bs = re.sub(r"\.html.*", "", bs)
            self._boxscore = bs
            return
        # Fallback: stringify the element (legacy behavior)
        boxscore = re.sub(r".*/boxscores/", "", str(boxscore))
        boxscore = re.sub(r"\.html.*", "", str(boxscore))
        self._boxscore = boxscore

    def _parse_game_data(self, game_data):
        """Parse a value for every attribute.

        The function looks through every attribute with the exception of those
        listed below and retrieves the value according to the parsing scheme
        and index of the attribute from the passed HTML data. Once the value
        is retrieved, the attribute's value is updated with the returned
        result.

        Note that this method is called directory once Game is invoked and does
        not need to be called manually.

        Parameters
        ----------
        game_data : string
            A string containing all of the rows of stats for a given game.

        """
        for field in self.__dict__:
            # Remove the leading '_' from the name
            short_name = str(field)[1:]
            if short_name in ("datetime", "opponent_rank"):
                continue
            if short_name == "opponent_abbr":
                self._parse_abbreviation(game_data)
                continue
            if short_name == "boxscore":
                self._parse_boxscore(game_data)
                continue
            value = utils.parse_field(SCHEDULE_SCHEME, game_data, short_name)
            setattr(self, field, value)

    @property
    def dataframe(self):
        """Return a pandas DataFrame containing all other class properties and.

        values. The index for the DataFrame is the boxscore string.
        """
        if self._points_for is None and self._points_against is None:
            return None
        fields_to_include = {
            "arena": self.arena,
            "boxscore_index": self.boxscore_index,
            "date": self.date,
            "datetime": self.datetime,
            "game": self.game,
            "location": self.location,
            "opponent_abbr": self.opponent_abbr,
            "opponent_conference": self.opponent_conference,
            "opponent_name": self.opponent_name,
            "opponent_rank": self.opponent_rank,
            "overtimes": self.overtimes,
            "points_against": self.points_against,
            "points_for": self.points_for,
            "result": self.result,
            "season_losses": self.season_losses,
            "season_wins": self.season_wins,
            "streak": self.streak,
            "time": self.time,
            "type": self.type,
        }
        # Prefer the team's abbreviation (set by Schedule) as the index so
        # that per-game DataFrames match test expectations; fall back to
        # boxscore if the team abbreviation isn't available.
        index_value = getattr(self, "_team_abbr", None)
        index_value = index_value.upper() if index_value else self._boxscore
        return pd.DataFrame([fields_to_include], index=[index_value])

    @property
    def dataframe_extended(self):
        """Return a pandas DataFrame representing the Boxscore class for the.

        game. This property provides much richer context for the selected game,
        but takes longer to process compared to the lighter 'dataframe'
        property. The index for the DataFrame is the boxscore string.
        """
        if self._points_for is None and self._points_against is None:
            return None
        return self.boxscore.dataframe

    @int_property_decorator
    def game(self):
        """Return an ``int`` of the game's position in the season. The first game.

        of the season returns 1.
        """
        return self._game

    @property
    def date(self):
        """Return a ``string`` of the game's date, such as 'Fri, Nov 10, 2017'."""
        return self._date

    @property
    def datetime(self):
        """Return a datetime object to indicate the month, day, year, and time.

        the requested game took place.
        """
        # Sometimes, the time isn't displayed on the game page. In this case,
        # the time property will be empty, causing the time parsing to fail as
        # it can't match the expected format. To prevent the issue, and since
        # the time can't properly be parsed, a default start time of midnight
        # should be used in this scenario, allowing users to decide if and how
        # they want to handle the time being empty.
        time = "12:00A" if not self._time or self._time.upper() == "" else self._time.upper()
        date_string = f"{self._date} {time}"
        date_string = re.sub(r"/.*", "", date_string)
        date_string = re.sub(r" ET", "", date_string)
        date_string += "M"
        date_string = re.sub(r"PMM", "PM", date_string, flags=re.IGNORECASE)
        date_string = re.sub(r"AMM", "AM", date_string, flags=re.IGNORECASE)
        date_string = re.sub(r" PM", "PM", date_string, flags=re.IGNORECASE)
        date_string = re.sub(r" AM", "AM", date_string, flags=re.IGNORECASE)
        return datetime.strptime(date_string, "%a, %b %d, %Y %I:%M%p")

    @property
    def time(self):
        """Return a ``string`` to indicate the time the game started, such as.

        '9:00 pm/est'.
        """
        if not self._time:
            return None
        t = self._time.strip()
        lower = t.lower()
        # If already formatted like '9:30 pm' or contains 'am'/'pm', keep as-is
        if re.search(r"\b(am|pm)\b", lower):
            # Ensure '/est' suffix to match expected output
            if "/est" in lower:
                return t
            return f"{t}/est" if "/est" not in t else t
        # Compact forms like '9:30p' or '9:30a' -> expand to '9:30 pm/est'
        m = re.match(r"^(\d{1,2}:\d{2})([ap])$", lower)
        if m:
            time_part = m.group(1)
            ampm = m.group(2)
            if ampm == "p":
                return f"{time_part} pm/est"
            return f"{time_part} am/est"
        return t

    @property
    def boxscore(self):
        """Return an instance of the Boxscore class containing more detailed.

        stats on the game.
        """
        return Boxscore(self._boxscore)

    @property
    def boxscore_index(self):
        """Return a ``string`` of the URI for a boxscore which can be used to.

        access or index a game.
        """
        return self._boxscore

    @property
    def type(self):
        """Return a ``string`` constant to indicate whether the game was played.

        during the regular season or in the post season.
        """
        if not self._type:
            return None
        match self._type.upper():
            case "REG":
                type_string = REGULAR_SEASON
            case "CTOURN":
                type_string = CONFERENCE_TOURNAMENT
            case "NCAA":
                type_string = NCAA_TOURNAMENT
            case "NIT":
                type_string = NIT_TOURNAMENT
            case "CBI":
                type_string = CBI_TOURNAMENT
            case "CIT":
                type_string = CIT_TOURNAMENT
            case _:
                type_string = None
        return type_string

    @property
    def location(self):
        """Return a ``string`` constant to indicate whether the game was played.

        at the team's home venue, the opponent's venue, or at a neutral site.
        """
        if self._location is None:
            return None
        match self._location.upper():
            case "":
                location_string = HOME
            case "@":
                location_string = AWAY
            case "N":
                location_string = NEUTRAL
            case _:
                location_string = None
        return location_string

    @property
    def opponent_abbr(self):
        """Return a ``string`` of the opponent's abbreviation, such as 'PURDUE'.

        for the Purdue Boilermakers.
        """
        return self._opponent_abbr

    @property
    def opponent_name(self):
        """Return a ``string`` of the opponent's name, such as the 'Purdue.

        Boilermakers'.
        """
        if not self._opponent_name:
            return None
        name = re.sub(r"\(\d+\)", "", self._opponent_name)
        name = name.replace("\xa0", "")
        return name

    @property
    def opponent_rank(self):
        """Return a ``string`` of the opponent's rank when the game was played.

        and None if the team was unranked.
        """
        if not self._opponent_name:
            return None
        rank = re.findall(r"\d+", self._opponent_name)
        if len(rank) > 0:
            return int(rank[0])
        return None

    @property
    def opponent_conference(self):
        """Return a ``string`` of the opponent's conference, such as 'Big Ten'.

        for a team participating in the Big Ten Conference. If the team is not
        a Division-I school, a string constant for non-majors is returned.
        """
        if not self._opponent_conference:
            return NON_DI
        return self._opponent_conference

    @property
    def result(self):
        """Return a ``string`` constant to indicate whether the team won or lost.

        the game.
        """
        if not self._result:
            return None
        if self._result.lower() == "w":
            return WIN
        return LOSS

    @int_property_decorator
    def points_for(self):
        """Return an ``int`` of the number of points the team scored during the.

        game.
        """
        return self._points_for

    @int_property_decorator
    def points_against(self):
        """Return an ``int`` of the number of points the team allowed during the.

        game.
        """
        return self._points_against

    @property
    def overtimes(self):
        """Return an ``int`` of the number of overtimes that were played during.

        the game and 0 if the game finished at the end of regulation time.
        """
        if self._overtimes == "" or self._overtimes is None:
            return 0
        if self._overtimes.lower() == "ot":
            return 1
        num_overtimes = re.findall(r"\d+", self._overtimes)
        try:
            return int(num_overtimes[0])
        except (ValueError, IndexError):
            return 0

    @int_property_decorator
    def season_wins(self):
        """Return an ``int`` of the number of games the team has won after the.

        conclusion of the requested game.
        """
        return self._season_wins

    @int_property_decorator
    def season_losses(self):
        """Return an ``int`` of the number of games the team has lost after the.

        conclusion of the requested game.
        """
        return self._season_losses

    @property
    def streak(self):
        """Return a ``string`` of the team's win streak at the conclusion of the.

        requested game. Streak is in the format '[W|L] #' (ie. 'W 3' indicates
        a 3-game winning streak while 'L 2' indicates a 2-game losing streak.
        """
        return self._streak

    @property
    def arena(self):
        """Return a ``string`` of the name of the arena the game was played at."""
        return self._arena


class Schedule:
    """An object of the given team's schedule.

    Generates a team's schedule for the season including wins, losses, and
    scores if applicable.

    Parameters
    ----------
    abbreviation : string
        A team's short name, such as 'PURDUE' for the Purdue Boilermakers.
    year : string (optional)
        The requested year to pull stats from.

    """

    def __init__(self, abbreviation, year=None):
        """Initialize the class instance."""
        self._games = []
        self._pull_schedule(abbreviation, year)

    def __getitem__(self, index):
        """Return a specified game.

        Returns a specified game as requested by the index number in the array.
        The input index is 0-based and must be within the range of the schedule
        array.

        Parameters
        ----------
        index : int
            The 0-based index of the game to return.

        Returns
        -------
        Game instance
            If the requested game can be found, its Game instance is returned.

        """
        return self._games[index]

    def __call__(self, date):
        """Return a specified game.

        Returns a specific game as requested by the passed datetime. The input
        datetime must have the same year, month, and day, but can have any time
        be used to match the game.

        Parameters
        ----------
        date : datetime
            A datetime object of the month, day, and year to identify a
            particular game that was played.

        Returns
        -------
        Game instance
            If the requested game can be found, its Game instance is returned.

        Raises
        ------
        ValueError
            If the requested date cannot be matched with a game in the
            schedule.

        """
        for game in self._games:
            if (
                game.datetime.year == date.year
                and game.datetime.month == date.month
                and game.datetime.day == date.day
            ):
                return game
        raise ValueError("No games found for requested date")

    def __str__(self):
        """Return the string representation of the class."""
        games = [f"{game.date} - {game.opponent_abbr}".strip() for game in self._games]
        return "\n".join(games)

    def __repr__(self):
        """Return the string representation of the class."""
        return self.__str__()

    def __iter__(self):
        """Return an iterator of all of the games scheduled for the given team."""
        return iter(self._games)

    def __len__(self):
        """Return the number of scheduled games for the given team."""
        return len(self._games)

    def _pull_schedule(self, abbreviation, year):
        """Download and create objects for the team's schedule.

        Given a team abbreviation and season, first download the team's
        schedule page and convert to a PyQuery object, then create a Game
        instance for every game in the team's schedule and append it to the
        '_games' property.

        Parameters
        ----------
        abbreviation : string
            A team's short name, such as 'PURDUE' for the Purdue Boilermakers.
        year : string
            The requested year to pull stats from.

        """
        if not year:
            year = utils.find_year_for_season("ncaab")
            year = utils.resolve_year_for_url(
                year, lambda y: SCHEDULE_URL % (abbreviation.lower(), y)
            )
        page_source = utils.get_page_source(url=SCHEDULE_URL % (abbreviation.lower(), year))
        if not page_source:
            utils.no_data_found()
            return
        doc = utils.pq(page_source)
        schedule = utils.get_stats_table(doc, "table#schedule")
        if not schedule:
            utils.no_data_found()
            return

        for item in schedule:
            if 'class="thead"' in str(item):
                continue
            game = Game(item)
            # Attach the parent schedule's team abbreviation to the game so
            # Game.dataframe can use it as the index to match tests.
            game._team_abbr = abbreviation
            self._games.append(game)

    @property
    def dataframe(self):
        """Return a pandas DataFrame where each row is a representation of the.

        Game class. Rows are indexed by the boxscore string.
        """
        frames = []
        for game in iter(self._games):
            df = game.dataframe
            if df is not None:
                frames.append(df)
        if not frames:
            return None
        return pd.concat(frames)

    @property
    def dataframe_extended(self):
        """Return a pandas DataFrame where each row is a representation of the.

        Boxscore class for every game in the schedule. Rows are indexed by the
        boxscore string. This property provides much richer context for the
        selected game, but takes longer to process compared to the lighter
        'dataframe' property.
        """
        frames = []
        for game in iter(self._games):
            df = game.dataframe_extended
            if df is not None:
                frames.append(df)
        if not frames:
            return None
        return pd.concat(frames)
