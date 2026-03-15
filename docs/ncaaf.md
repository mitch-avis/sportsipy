# NCAAF Package (`sportsipy.ncaaf`)

The NCAAF package offers multiple modules that can be used to retrieve
information and statistics for Division-I College Football, such as team names,
season stats, game schedules, and boxscore metrics.

> **API Reference:** Detailed property and method documentation is available
> inline via docstrings in the
> [source code](../sportsipy/ncaaf/).

## Boxscore

The `Boxscore` module retrieves information for a specific game. Metrics range
from points scored to pass yards, yards from penalties, and much more.

```python
from sportsipy.ncaaf.boxscore import Boxscore

game_data = Boxscore('2018-01-08-georgia')
print(game_data.home_points)  # Prints 23
print(game_data.away_points)  # Prints 26
df = game_data.dataframe      # Returns a Polars DataFrame of game metrics
```

The `Boxscores` class searches for all games on a particular day:

```python
from datetime import datetime
from sportsipy.ncaaf.boxscore import Boxscores

games_today = Boxscores(datetime.today())
print(games_today.games)

# Query a range of dates
games = Boxscores(datetime(2017, 8, 30), datetime(2017, 8, 31))
print(games.games)
```

## Conferences

The `Conferences` module allows conference data to be pulled for any season.

```python
from sportsipy.ncaaf.conferences import Conferences

conferences = Conferences()
# Dictionary mapping team abbreviation → conference abbreviation
print(conferences.team_conference)
# Detailed dictionary: conference abbreviation → {name, teams}
print(conferences.conferences)
```

## Player

The `Player` module contains `AbstractPlayer`, a base class inherited by both
`BoxscorePlayer` (from `Boxscore`) and `Player` (from `Roster`). All properties
on `AbstractPlayer` are available from either child class.

## Rankings

The `Rankings` class queries AP Division-I Football rankings week-by-week.
`CFPRankings` accesses College Football Playoff rankings and `CoachesRankings`
accesses USA Today Coaches Poll rankings.

```python
from sportsipy.ncaaf.rankings import Rankings, CFPRankings, CoachesRankings

rankings = Rankings()
print(rankings.current)           # Dict of team abbreviation → current rank
print(rankings.current_extended)  # Detailed info for all teams this week
print(rankings.complete)          # Detailed info for all teams all season

cfp = CFPRankings()
print(cfp.current)

coaches = CoachesRankings()
print(coaches.current)
```

## Roster

The `Roster` module provides detailed player information via the `Player` class.

```python
from sportsipy.ncaaf.roster import Player

blough = Player('david-blough-1')
print(blough.name)           # Prints 'David Blough'
print(blough.passing_yards)  # Career passing yards
print(blough.dataframe)      # Polars DataFrame of all stats per season
```

Request a specific season:

```python
blough = Player('david-blough-1')
print(blough.passing_yards)             # Career passing yards
print(blough('2017').passing_yards)     # 2017 season passing yards
print(blough.passing_touchdowns)        # TDs for 2017
print(blough('Career').passing_yards)   # Back to career stats
```

Pull a full team roster:

```python
from sportsipy.ncaaf.roster import Roster

boilermakers = Roster('PURDUE')
for player in boilermakers.players:
    print(player.name)
```

## Schedule

```python
from sportsipy.ncaaf.schedule import Schedule

purdue_schedule = Schedule('PURDUE')
for game in purdue_schedule:
    print(game.date)
    print(game.result)
    boxscore = game.boxscore
```

## Teams

```python
from sportsipy.ncaaf.teams import Teams

teams = Teams()
for team in teams:
    print(team.name)        # Team name
    print(team.pass_yards)  # Total passing yards for the season
```

Request a specific team using its abbreviation:

```python
from sportsipy.ncaaf.teams import Team

purdue = Team('PURDUE')
```

Each `Team` instance links to `Schedule` and `Roster`:

```python
teams = Teams()
for team in teams:
    df = team.schedule.dataframe_extended

    roster = team.roster
    for player in roster.players:
        print(player.name)
```
