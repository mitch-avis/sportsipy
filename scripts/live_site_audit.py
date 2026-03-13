#!/usr/bin/env python3
"""Run a live, rate-limited audit against representative sports-reference pages.

This script is intended for manual verification only. It exercises the same
high-level entry points used by the integration suite, but against the live
sports-reference family of sites instead of offline fixtures.

The audit intentionally uses stable historical IDs, teams, and dates sourced
from the integration tests. That avoids false negatives caused by incomplete
current-season data while still validating that the live HTML structure remains
compatible with the library's parsers.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from collections.abc import Callable, Sized
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast


class AuditError(RuntimeError):
    """Represent a failed audit assertion."""


@dataclass(frozen=True)
class AuditCase:
    """Describe a single live audit case."""

    case_id: str
    sport: str
    area: str
    description: str
    runner: Callable[[], tuple[str, dict[str, Any]]]


@dataclass
class AuditResult:
    """Capture the outcome of a single audit case."""

    case_id: str
    sport: str
    area: str
    description: str
    status: str
    elapsed_seconds: float
    summary: str
    details: dict[str, Any] = field(default_factory=dict)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def _load_runtime() -> dict[str, Any]:
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from sportsipy import utils
    from sportsipy.fb.roster import Roster as FBRoster
    from sportsipy.fb.schedule import Schedule as FBSchedule
    from sportsipy.fb.team import Team as FBTeam
    from sportsipy.mlb.boxscore import Boxscore as MLBBoxscore
    from sportsipy.mlb.boxscore import Boxscores as MLBBoxscores
    from sportsipy.mlb.roster import Player as MLBPlayer
    from sportsipy.mlb.roster import Roster as MLBRoster
    from sportsipy.mlb.schedule import Schedule as MLBSchedule
    from sportsipy.mlb.teams import Team as MLBTeam
    from sportsipy.mlb.teams import Teams as MLBTeams
    from sportsipy.nba.boxscore import Boxscore as NBABoxscore
    from sportsipy.nba.boxscore import Boxscores as NBABoxscores
    from sportsipy.nba.roster import Player as NBAPlayer
    from sportsipy.nba.roster import Roster as NBARoster
    from sportsipy.nba.schedule import Schedule as NBASchedule
    from sportsipy.nba.teams import Team as NBATeam
    from sportsipy.nba.teams import Teams as NBATeams
    from sportsipy.ncaab.boxscore import Boxscore as NCAABBoxscore
    from sportsipy.ncaab.boxscore import Boxscores as NCAABBoxscores
    from sportsipy.ncaab.conferences import Conference as NCAABConference
    from sportsipy.ncaab.conferences import Conferences as NCAABConferences
    from sportsipy.ncaab.rankings import Rankings as NCAABRankings
    from sportsipy.ncaab.roster import Player as NCAABPlayer
    from sportsipy.ncaab.roster import Roster as NCAABRoster
    from sportsipy.ncaab.schedule import Schedule as NCAABSchedule
    from sportsipy.ncaab.teams import Team as NCAABTeam
    from sportsipy.ncaab.teams import Teams as NCAABTeams
    from sportsipy.ncaaf.boxscore import Boxscore as NCAAFBoxscore
    from sportsipy.ncaaf.boxscore import Boxscores as NCAAFBoxscores
    from sportsipy.ncaaf.conferences import Conference as NCAAFConference
    from sportsipy.ncaaf.conferences import Conferences as NCAAFConferences
    from sportsipy.ncaaf.rankings import CFPRankings, CoachesRankings
    from sportsipy.ncaaf.rankings import Rankings as NCAAFRankings
    from sportsipy.ncaaf.roster import Player as NCAAFPlayer
    from sportsipy.ncaaf.roster import Roster as NCAAFRoster
    from sportsipy.ncaaf.schedule import Schedule as NCAAFSchedule
    from sportsipy.ncaaf.teams import Team as NCAAFTeam
    from sportsipy.ncaaf.teams import Teams as NCAAFTeams
    from sportsipy.nfl.boxscore import Boxscore as NFLBoxscore
    from sportsipy.nfl.boxscore import Boxscores as NFLBoxscores
    from sportsipy.nfl.roster import Player as NFLPlayer
    from sportsipy.nfl.roster import Roster as NFLRoster
    from sportsipy.nfl.schedule import Schedule as NFLSchedule
    from sportsipy.nfl.teams import Team as NFLTeam
    from sportsipy.nfl.teams import Teams as NFLTeams
    from sportsipy.nhl.boxscore import Boxscore as NHLBoxscore
    from sportsipy.nhl.boxscore import Boxscores as NHLBoxscores
    from sportsipy.nhl.roster import Player as NHLPlayer
    from sportsipy.nhl.roster import Roster as NHLRoster
    from sportsipy.nhl.schedule import Schedule as NHLSchedule
    from sportsipy.nhl.teams import Team as NHLTeam
    from sportsipy.nhl.teams import Teams as NHLTeams

    return {
        "utils": utils,
        "FBRoster": FBRoster,
        "FBSchedule": FBSchedule,
        "FBTeam": FBTeam,
        "MLBBoxscore": MLBBoxscore,
        "MLBBoxscores": MLBBoxscores,
        "MLBPlayer": MLBPlayer,
        "MLBRoster": MLBRoster,
        "MLBSchedule": MLBSchedule,
        "MLBTeam": MLBTeam,
        "MLBTeams": MLBTeams,
        "NBABoxscore": NBABoxscore,
        "NBABoxscores": NBABoxscores,
        "NBAPlayer": NBAPlayer,
        "NBARoster": NBARoster,
        "NBASchedule": NBASchedule,
        "NBATeam": NBATeam,
        "NBATeams": NBATeams,
        "NCAABBoxscore": NCAABBoxscore,
        "NCAABBoxscores": NCAABBoxscores,
        "NCAABConference": NCAABConference,
        "NCAABConferences": NCAABConferences,
        "NCAABPlayer": NCAABPlayer,
        "NCAABRankings": NCAABRankings,
        "NCAABRoster": NCAABRoster,
        "NCAABSchedule": NCAABSchedule,
        "NCAABTeam": NCAABTeam,
        "NCAABTeams": NCAABTeams,
        "NCAAFBoxscore": NCAAFBoxscore,
        "NCAAFBoxscores": NCAAFBoxscores,
        "NCAAFConference": NCAAFConference,
        "NCAAFConferences": NCAAFConferences,
        "NCAAFPlayer": NCAAFPlayer,
        "NCAAFRankings": NCAAFRankings,
        "NCAAFRoster": NCAAFRoster,
        "NCAAFSchedule": NCAAFSchedule,
        "NCAAFTeam": NCAAFTeam,
        "NCAAFTeams": NCAAFTeams,
        "CFPRankings": CFPRankings,
        "CoachesRankings": CoachesRankings,
        "NFLBoxscore": NFLBoxscore,
        "NFLBoxscores": NFLBoxscores,
        "NFLPlayer": NFLPlayer,
        "NFLRoster": NFLRoster,
        "NFLSchedule": NFLSchedule,
        "NFLTeam": NFLTeam,
        "NFLTeams": NFLTeams,
        "NHLBoxscore": NHLBoxscore,
        "NHLBoxscores": NHLBoxscores,
        "NHLPlayer": NHLPlayer,
        "NHLRoster": NHLRoster,
        "NHLSchedule": NHLSchedule,
        "NHLTeam": NHLTeam,
        "NHLTeams": NHLTeams,
    }


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _count_games(games: dict[str, list[dict[str, Any]]]) -> int:
    return sum(len(entries) for entries in games.values())


def _first_from_players(players: Any) -> Any:
    if isinstance(players, dict):
        _require(bool(players), "players dictionary is empty")
        return next(iter(players.values()))
    _require(len(players) > 0, "players collection is empty")
    return players[0]


def _named_summary(entity: Any) -> str:
    for attribute in ("name", "short_name", "abbreviation"):
        value = _as_text(getattr(entity, attribute, None))
        if value:
            return value
    return entity.__class__.__name__


def _run_teams(constructor: Any) -> tuple[str, dict[str, Any]]:
    teams = constructor()
    entries = list(teams)
    _require(bool(entries), "teams collection is empty")
    first_team = entries[0]
    summary = _named_summary(first_team)
    return summary, {"count": len(entries), "sample": summary}


def _run_team(constructor: Any) -> tuple[str, dict[str, Any]]:
    team = constructor()
    name = (
        _as_text(getattr(team, "name", None))
        or _as_text(getattr(team, "short_name", None))
        or _as_text(getattr(team, "abbreviation", None))
    )
    _require(bool(name), "team name is empty")
    return name, {"sample": name}


def _run_schedule(constructor: Any) -> tuple[str, dict[str, Any]]:
    schedule = constructor()
    total_games = len(schedule)
    _require(total_games > 0, "schedule is empty")
    game = schedule[0]
    # FBRef uses 'opponent'; all other sport schedules use 'opponent_abbr'.
    opponent = _as_text(getattr(game, "opponent", None)) or _as_text(
        getattr(game, "opponent_abbr", None)
    )
    date_value = _as_text(getattr(game, "date", None))
    _require(bool(opponent), "first game is missing opponent")
    _require(bool(date_value), "first game is missing date")
    return f"{date_value} vs {opponent}", {
        "count": total_games,
        "sample_date": date_value,
        "sample_opponent": opponent,
    }


def _run_roster(constructor: Any) -> tuple[str, dict[str, Any]]:
    roster = constructor()
    players = roster.players
    count = len(players)
    _require(count > 0, "roster has no players")
    first_player = _first_from_players(players)
    summary = _named_summary(first_player)
    return summary, {"count": count, "sample": summary}


def _run_player(constructor: Any) -> tuple[str, dict[str, Any]]:
    player = constructor()
    name = _named_summary(player)
    _require(bool(name), "player name is empty")
    dataframe = getattr(player, "dataframe", None)
    _require(dataframe is not None, "player dataframe is missing")
    return name, {"sample": name}


def _run_boxscore(constructor: Any) -> tuple[str, dict[str, Any]]:
    boxscore = constructor()
    home_players = getattr(boxscore, "home_players", None)
    away_players = getattr(boxscore, "away_players", None)
    _require(home_players is not None and len(home_players) > 0, "home players are empty")
    _require(away_players is not None and len(away_players) > 0, "away players are empty")
    home_players_list = cast(Sized, home_players)
    away_players_list = cast(Sized, away_players)
    date_value = _as_text(getattr(boxscore, "date", None))
    return date_value or boxscore.__class__.__name__, {
        "home_players": len(home_players_list),
        "away_players": len(away_players_list),
        "date": date_value,
    }


def _run_boxscores(constructor: Any) -> tuple[str, dict[str, Any]]:
    boxscores = constructor()
    games = boxscores.games
    total_games = _count_games(games)
    _require(total_games > 0, "boxscores listing is empty")
    return f"{total_games} games", {"dates": len(games), "games": total_games}


def _run_conferences(constructor: Any) -> tuple[str, dict[str, Any]]:
    conferences = constructor()
    mapping = conferences.conferences
    _require(bool(mapping), "conference mapping is empty")
    first_key = next(iter(mapping))
    first_name = mapping[first_key]["name"]
    return first_name, {"count": len(mapping), "sample": first_key}


def _run_conference(constructor: Any) -> tuple[str, dict[str, Any]]:
    conference = constructor()
    teams = conference.teams
    _require(bool(teams), "conference teams are empty")
    first_team = next(iter(teams))
    return conference._conference_abbreviation, {
        "count": len(teams),
        "sample": first_team,
    }


def _run_rankings(constructor: Any) -> tuple[str, dict[str, Any]]:
    rankings = constructor()
    current = rankings.current
    complete = rankings.complete
    _require(bool(current), "current rankings are empty")
    _require(bool(complete), "complete rankings are empty")
    top_team = next(iter(current))
    return top_team, {"current_count": len(current), "weeks": len(complete)}


def _teams_runner(
    factory: Any, *args: Any, **kwargs: Any
) -> Callable[[], tuple[str, dict[str, Any]]]:
    return lambda: _run_teams(lambda: factory(*args, **kwargs))


def _team_runner(
    factory: Any, *args: Any, **kwargs: Any
) -> Callable[[], tuple[str, dict[str, Any]]]:
    return lambda: _run_team(lambda: factory(*args, **kwargs))


def _schedule_runner(
    factory: Any,
    *args: Any,
    **kwargs: Any,
) -> Callable[[], tuple[str, dict[str, Any]]]:
    return lambda: _run_schedule(lambda: factory(*args, **kwargs))


def _roster_runner(
    factory: Any, *args: Any, **kwargs: Any
) -> Callable[[], tuple[str, dict[str, Any]]]:
    return lambda: _run_roster(lambda: factory(*args, **kwargs))


def _player_runner(
    factory: Any,
    player_id: str,
    season: str,
) -> Callable[[], tuple[str, dict[str, Any]]]:
    return lambda: _run_player(lambda: factory(player_id)(season) if season else factory(player_id))


def _boxscore_runner(
    factory: Any,
    *args: Any,
    **kwargs: Any,
) -> Callable[[], tuple[str, dict[str, Any]]]:
    return lambda: _run_boxscore(lambda: factory(*args, **kwargs))


def _boxscores_runner(
    factory: Any,
    *args: Any,
    **kwargs: Any,
) -> Callable[[], tuple[str, dict[str, Any]]]:
    return lambda: _run_boxscores(lambda: factory(*args, **kwargs))


def _conferences_runner(
    factory: Any,
    *args: Any,
    **kwargs: Any,
) -> Callable[[], tuple[str, dict[str, Any]]]:
    return lambda: _run_conferences(lambda: factory(*args, **kwargs))


def _conference_runner(
    factory: Any,
    *args: Any,
    **kwargs: Any,
) -> Callable[[], tuple[str, dict[str, Any]]]:
    return lambda: _run_conference(lambda: factory(*args, **kwargs))


def _rankings_runner(
    factory: Any,
    *args: Any,
    **kwargs: Any,
) -> Callable[[], tuple[str, dict[str, Any]]]:
    return lambda: _run_rankings(lambda: factory(*args, **kwargs))


def _cases(runtime: dict[str, Any]) -> list[AuditCase]:
    mlb_boxscore = runtime["MLBBoxscore"]
    mlb_boxscores = runtime["MLBBoxscores"]
    mlb_player = runtime["MLBPlayer"]
    mlb_roster = runtime["MLBRoster"]
    mlb_schedule = runtime["MLBSchedule"]
    mlb_team = runtime["MLBTeam"]
    mlb_teams = runtime["MLBTeams"]
    nba_boxscore = runtime["NBABoxscore"]
    nba_boxscores = runtime["NBABoxscores"]
    nba_player = runtime["NBAPlayer"]
    nba_roster = runtime["NBARoster"]
    nba_schedule = runtime["NBASchedule"]
    nba_team = runtime["NBATeam"]
    nba_teams = runtime["NBATeams"]
    nfl_boxscore = runtime["NFLBoxscore"]
    nfl_boxscores = runtime["NFLBoxscores"]
    nfl_player = runtime["NFLPlayer"]
    nfl_roster = runtime["NFLRoster"]
    nfl_schedule = runtime["NFLSchedule"]
    nfl_team = runtime["NFLTeam"]
    nfl_teams = runtime["NFLTeams"]
    nhl_boxscore = runtime["NHLBoxscore"]
    nhl_boxscores = runtime["NHLBoxscores"]
    nhl_player = runtime["NHLPlayer"]
    nhl_roster = runtime["NHLRoster"]
    nhl_schedule = runtime["NHLSchedule"]
    nhl_team = runtime["NHLTeam"]
    nhl_teams = runtime["NHLTeams"]
    ncaab_boxscore = runtime["NCAABBoxscore"]
    ncaab_boxscores = runtime["NCAABBoxscores"]
    ncaab_conference = runtime["NCAABConference"]
    ncaab_conferences = runtime["NCAABConferences"]
    ncaab_player = runtime["NCAABPlayer"]
    ncaab_rankings = runtime["NCAABRankings"]
    ncaab_roster = runtime["NCAABRoster"]
    ncaab_schedule = runtime["NCAABSchedule"]
    ncaab_team = runtime["NCAABTeam"]
    ncaab_teams = runtime["NCAABTeams"]
    ncaaf_boxscore = runtime["NCAAFBoxscore"]
    ncaaf_boxscores = runtime["NCAAFBoxscores"]
    ncaaf_conference = runtime["NCAAFConference"]
    ncaaf_conferences = runtime["NCAAFConferences"]
    ncaaf_player = runtime["NCAAFPlayer"]
    ncaaf_rankings = runtime["NCAAFRankings"]
    ncaaf_roster = runtime["NCAAFRoster"]
    ncaaf_schedule = runtime["NCAAFSchedule"]
    ncaaf_team = runtime["NCAAFTeam"]
    ncaaf_teams = runtime["NCAAFTeams"]
    cfp_rankings = runtime["CFPRankings"]
    coaches_rankings = runtime["CoachesRankings"]
    fb_team = runtime["FBTeam"]
    fb_schedule = runtime["FBSchedule"]
    fb_roster = runtime["FBRoster"]

    return [
        AuditCase(
            "mlb-teams",
            "mlb",
            "teams",
            "MLB team index page",
            _teams_runner(mlb_teams, 2021),
        ),
        AuditCase(
            "mlb-team",
            "mlb",
            "team",
            "MLB team page",
            _team_runner(mlb_team, "HOU", year=2021),
        ),
        AuditCase(
            "mlb-schedule",
            "mlb",
            "schedule",
            "MLB team schedule page",
            _schedule_runner(mlb_schedule, "NYY", year=2017),
        ),
        AuditCase(
            "mlb-boxscore",
            "mlb",
            "boxscore",
            "MLB single boxscore page",
            _boxscore_runner(mlb_boxscore, "ANA/ANA202008170"),
        ),
        AuditCase(
            "mlb-boxscores",
            "mlb",
            "boxscores",
            "MLB daily boxscores index",
            _boxscores_runner(mlb_boxscores, datetime(2020, 8, 17)),
        ),
        AuditCase(
            "mlb-roster",
            "mlb",
            "roster",
            "MLB team roster page",
            _roster_runner(mlb_roster, "HOU", year=2017),
        ),
        AuditCase(
            "mlb-player",
            "mlb",
            "player",
            "MLB player page",
            _player_runner(mlb_player, "altuvjo01", ""),
        ),
        AuditCase(
            "nba-teams",
            "nba",
            "teams",
            "NBA team index page",
            _teams_runner(nba_teams, 2021),
        ),
        AuditCase(
            "nba-team",
            "nba",
            "team",
            "NBA team page",
            _team_runner(nba_team, "DET", year=2021),
        ),
        AuditCase(
            "nba-schedule",
            "nba",
            "schedule",
            "NBA team schedule page",
            _schedule_runner(nba_schedule, "GSW", year=2017),
        ),
        AuditCase(
            "nba-boxscore",
            "nba",
            "boxscore",
            "NBA single boxscore page",
            _boxscore_runner(nba_boxscore, "202002220UTA"),
        ),
        AuditCase(
            "nba-boxscores",
            "nba",
            "boxscores",
            "NBA daily boxscores index",
            _boxscores_runner(nba_boxscores, datetime(2020, 2, 22)),
        ),
        AuditCase(
            "nba-roster",
            "nba",
            "roster",
            "NBA team roster page",
            _roster_runner(nba_roster, "HOU", year=2018),
        ),
        AuditCase(
            "nba-player",
            "nba",
            "player",
            "NBA player page",
            _player_runner(nba_player, "hardeja01", ""),
        ),
        AuditCase(
            "nfl-teams",
            "nfl",
            "teams",
            "NFL team index page",
            _teams_runner(nfl_teams, 2017),
        ),
        AuditCase(
            "nfl-team",
            "nfl",
            "team",
            "NFL team page",
            _team_runner(nfl_team, "NWE", year=2017),
        ),
        AuditCase(
            "nfl-schedule",
            "nfl",
            "schedule",
            "NFL team schedule page",
            _schedule_runner(nfl_schedule, "NWE", year=2017),
        ),
        AuditCase(
            "nfl-boxscore",
            "nfl",
            "boxscore",
            "NFL single boxscore page",
            _boxscore_runner(nfl_boxscore, "202009100kan"),
        ),
        AuditCase(
            "nfl-boxscores",
            "nfl",
            "boxscores",
            "NFL weekly boxscores index",
            _boxscores_runner(nfl_boxscores, 1, 2020),
        ),
        AuditCase(
            "nfl-roster",
            "nfl",
            "roster",
            "NFL team roster page",
            _roster_runner(nfl_roster, "NOR", year=2018),
        ),
        AuditCase(
            "nfl-player",
            "nfl",
            "player",
            "NFL player page",
            _player_runner(nfl_player, "BreeDr00", "2017"),
        ),
        AuditCase(
            "nhl-teams",
            "nhl",
            "teams",
            "NHL team index page",
            _teams_runner(nhl_teams, 2017),
        ),
        AuditCase(
            "nhl-team",
            "nhl",
            "team",
            "NHL team page",
            _team_runner(nhl_team, "DET", year=2017),
        ),
        AuditCase(
            "nhl-schedule",
            "nhl",
            "schedule",
            "NHL team schedule page",
            _schedule_runner(nhl_schedule, "NYR", year=2017),
        ),
        AuditCase(
            "nhl-boxscore",
            "nhl",
            "boxscore",
            "NHL single boxscore page",
            _boxscore_runner(nhl_boxscore, "202003040VAN"),
        ),
        AuditCase(
            "nhl-boxscores",
            "nhl",
            "boxscores",
            "NHL daily boxscores index",
            _boxscores_runner(nhl_boxscores, datetime(2020, 3, 4)),
        ),
        AuditCase(
            "nhl-roster",
            "nhl",
            "roster",
            "NHL team roster page",
            _roster_runner(nhl_roster, "DET", year=2018),
        ),
        AuditCase(
            "nhl-player",
            "nhl",
            "player",
            "NHL player page",
            _player_runner(nhl_player, "zettehe01", "2017-18"),
        ),
        AuditCase(
            "ncaab-teams",
            "ncaab",
            "teams",
            "NCAAB team index page",
            _teams_runner(ncaab_teams, 2018),
        ),
        AuditCase(
            "ncaab-team",
            "ncaab",
            "team",
            "NCAAB team page",
            _team_runner(ncaab_team, "PURDUE", year=2018),
        ),
        AuditCase(
            "ncaab-schedule",
            "ncaab",
            "schedule",
            "NCAAB team schedule page",
            _schedule_runner(ncaab_schedule, "KANSAS", year=2017),
        ),
        AuditCase(
            "ncaab-boxscore",
            "ncaab",
            "boxscore",
            "NCAAB single boxscore page",
            _boxscore_runner(ncaab_boxscore, "2020-01-22-19-louisville"),
        ),
        AuditCase(
            "ncaab-boxscores",
            "ncaab",
            "boxscores",
            "NCAAB daily boxscores index",
            _boxscores_runner(ncaab_boxscores, datetime(2020, 1, 5)),
        ),
        AuditCase(
            "ncaab-roster",
            "ncaab",
            "roster",
            "NCAAB team roster page",
            _roster_runner(ncaab_roster, "PURDUE", year=2018),
        ),
        AuditCase(
            "ncaab-player",
            "ncaab",
            "player",
            "NCAAB player page",
            _player_runner(ncaab_player, "carsen-edwards-1", ""),
        ),
        AuditCase(
            "ncaab-conferences",
            "ncaab",
            "conferences",
            "NCAAB conferences index page",
            _conferences_runner(ncaab_conferences, 2018),
        ),
        AuditCase(
            "ncaab-conference",
            "ncaab",
            "conference",
            "NCAAB conference detail page",
            _conference_runner(ncaab_conference, "big-12", 2018),
        ),
        AuditCase(
            "ncaab-rankings",
            "ncaab",
            "rankings",
            "NCAAB rankings page",
            _rankings_runner(ncaab_rankings, 2018),
        ),
        AuditCase(
            "ncaaf-teams",
            "ncaaf",
            "teams",
            "NCAAF team index page",
            _teams_runner(ncaaf_teams, 2017),
        ),
        AuditCase(
            "ncaaf-team",
            "ncaaf",
            "team",
            "NCAAF team page",
            _team_runner(ncaaf_team, "PURDUE", year=2017),
        ),
        AuditCase(
            "ncaaf-schedule",
            "ncaaf",
            "schedule",
            "NCAAF team schedule page",
            _schedule_runner(ncaaf_schedule, "PURDUE", year=2017),
        ),
        AuditCase(
            "ncaaf-boxscore",
            "ncaaf",
            "boxscore",
            "NCAAF single boxscore page",
            _boxscore_runner(ncaaf_boxscore, "2020-09-12-wake-forest"),
        ),
        AuditCase(
            "ncaaf-boxscores",
            "ncaaf",
            "boxscores",
            "NCAAF daily boxscores index",
            _boxscores_runner(ncaaf_boxscores, datetime(2020, 9, 12)),
        ),
        AuditCase(
            "ncaaf-roster",
            "ncaaf",
            "roster",
            "NCAAF team roster page",
            _roster_runner(ncaaf_roster, "PURDUE", year=2017),
        ),
        AuditCase(
            "ncaaf-player",
            "ncaaf",
            "player",
            "NCAAF player page",
            _player_runner(ncaaf_player, "david-blough-1", "2017"),
        ),
        AuditCase(
            "ncaaf-conferences",
            "ncaaf",
            "conferences",
            "NCAAF conferences index page",
            _conferences_runner(ncaaf_conferences, 2018),
        ),
        AuditCase(
            "ncaaf-conference",
            "ncaaf",
            "conference",
            "NCAAF conference detail page",
            _conference_runner(ncaaf_conference, "acc", 2018),
        ),
        AuditCase(
            "ncaaf-rankings",
            "ncaaf",
            "rankings",
            "NCAAF AP rankings page",
            _rankings_runner(ncaaf_rankings, 2017),
        ),
        AuditCase(
            "ncaaf-cfp-rankings",
            "ncaaf",
            "rankings",
            "NCAAF CFP rankings page",
            _rankings_runner(cfp_rankings, 2017),
        ),
        AuditCase(
            "ncaaf-coaches-rankings",
            "ncaaf",
            "rankings",
            "NCAAF Coaches rankings page",
            _rankings_runner(coaches_rankings, 2017),
        ),
        AuditCase(
            "fb-team",
            "fb",
            "team",
            "FBref team page",
            _team_runner(fb_team, "Tottenham Hotspur"),
        ),
        AuditCase(
            "fb-schedule",
            "fb",
            "schedule",
            "FBref schedule page",
            _schedule_runner(fb_schedule, "Tottenham Hotspur"),
        ),
        AuditCase(
            "fb-roster",
            "fb",
            "roster",
            "FBref roster page",
            _roster_runner(fb_roster, "Tottenham Hotspur"),
        ),
    ]


def _configure_environment(
    utils_module: Any,
    rate_limit_seconds: float,
    timeout_seconds: float,
    max_retries: int,
) -> None:
    for variable in (
        "SPORTSIPY_OFFLINE",
        "SPORTSIPY_FIXTURE_DIR",
        "SPORTSIPY_FIXTURE_MAP",
        "SPORTSIPY_CACHE_DIR",
        "SPORTSIPY_CACHE_TTL_SECONDS",
        "SPORTSIPY_DISABLE_RATE_LIMIT",
        "PYTEST_CURRENT_TEST",
    ):
        os.environ.pop(variable, None)
    os.environ["SPORTSIPY_FORCE_RATE_LIMIT"] = "1"
    os.environ["SPORTSIPY_RATE_LIMIT_SECONDS"] = str(rate_limit_seconds)
    os.environ["SPORTSIPY_MAX_RETRIES"] = str(max_retries)
    os.environ["SPORTSIPY_REQUEST_TIMEOUT_SECONDS"] = str(timeout_seconds)
    utils_module._FIXTURE_MAP = None


def _select_cases(args: argparse.Namespace, runtime: dict[str, Any]) -> list[AuditCase]:
    requested_sports = set(args.sport or [])
    requested_areas = set(args.area or [])
    selected = []
    for case in _cases(runtime):
        if requested_sports and case.sport not in requested_sports:
            continue
        if requested_areas and case.area not in requested_areas:
            continue
        if args.case and args.case not in case.case_id:
            continue
        selected.append(case)
    return selected


def _run_case(case: AuditCase) -> AuditResult:
    start = time.perf_counter()
    try:
        summary, details = case.runner()
        return AuditResult(
            case_id=case.case_id,
            sport=case.sport,
            area=case.area,
            description=case.description,
            status="pass",
            elapsed_seconds=time.perf_counter() - start,
            summary=summary,
            details=details,
        )
    except Exception as exc:
        return AuditResult(
            case_id=case.case_id,
            sport=case.sport,
            area=case.area,
            description=case.description,
            status="fail",
            elapsed_seconds=time.perf_counter() - start,
            summary=str(exc),
            details={"traceback": traceback.format_exc(limit=5)},
        )


def _print_case_list(cases: list[AuditCase]) -> None:
    for case in cases:
        print(f"{case.case_id:24} {case.sport:6} {case.area:12} {case.description}")


def _print_results(results: list[AuditResult]) -> None:
    for result in results:
        print(
            f"[{result.status.upper():4}] {result.case_id:24} "
            f"{result.elapsed_seconds:6.2f}s  {result.summary}"
        )


def _write_json(path: Path, results: list[AuditResult]) -> None:
    payload = {
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "results": [asdict(result) for result in results],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sport", action="append", help="Limit to a sport, e.g. mlb or ncaaf.")
    parser.add_argument(
        "--area",
        action="append",
        help="Limit to a page family, e.g. team, schedule, roster, player, boxscore.",
    )
    parser.add_argument("--case", help="Run only cases whose id contains this substring.")
    parser.add_argument("--list-cases", action="store_true", help="List audit cases and exit.")
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop after the first failed case.",
    )
    parser.add_argument(
        "--rate-limit-seconds",
        type=float,
        default=3.2,
        help="Minimum delay between live HTTP requests. Defaults to 3.2 seconds.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=20.0,
        help="Reserved request timeout hint for future extension. Defaults to 20 seconds.",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=1,
        help="Number of retries for transient HTTP failures. Defaults to 1.",
    )
    parser.add_argument("--json-out", type=Path, help="Write a machine-readable JSON report.")
    return parser


def main() -> int:
    """Run the requested live audit cases and report pass or fail status."""
    parser = _build_parser()
    args = parser.parse_args()
    runtime = _load_runtime()
    cases = _select_cases(args, runtime)
    if args.list_cases:
        _print_case_list(cases)
        return 0
    if not cases:
        parser.error("No audit cases matched the requested filters.")

    _configure_environment(
        runtime["utils"],
        args.rate_limit_seconds,
        args.timeout_seconds,
        args.max_retries,
    )

    print(
        f"Running {len(cases)} live audit cases with {args.rate_limit_seconds:.1f}s request spacing"
    )
    results: list[AuditResult] = []
    for case in cases:
        result = _run_case(case)
        results.append(result)
        print(
            f"[{result.status.upper():4}] {case.case_id:24} "
            f"{result.elapsed_seconds:6.2f}s  {result.summary}"
        )
        if args.fail_fast and result.status == "fail":
            break

    if args.json_out:
        _write_json(args.json_out, results)

    failures = [result for result in results if result.status == "fail"]
    print()
    print(
        f"Completed {len(results)} cases: "
        f"{len(results) - len(failures)} passed, {len(failures)} failed"
    )
    if failures:
        print("Failed cases:")
        _print_results(failures)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
