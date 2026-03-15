# MLB Package (`sportsipy.mlb`)

The MLB package offers multiple modules that can be used to retrieve information
and statistics for Major League Baseball, such as team names, season stats, game
schedules, and boxscore metrics.

> **API Reference:** Detailed property and method documentation is available
> inline via docstrings in the
> [source code](../sportsipy/mlb/).

## Boxscore

The `Boxscore` module retrieves information for a specific game. Metrics range
from runs scored to sacrifice flies, slugging percentage, and much more. Pass a
boxscore URI from sports-reference.com (retrievable from `Schedule`) to
instantiate.

```python
from sportsipy.mlb.boxscore import Boxscore

game_data = Boxscore('BOS/BOS201808020')
print(game_data.home_runs)   # Prints 15
print(game_data.away_runs)   # Prints 7
df = game_data.dataframe     # Returns a Polars DataFrame of game metrics
```

The `Boxscores` class searches for all games played on a particular day and
returns a dictionary of matchups.

```python
from datetime import datetime
from sportsipy.mlb.boxscore import Boxscores

games_today = Boxscores(datetime.today())
print(games_today.games)     # Prints a dictionary of all matchups for today

# Query a range of dates
games = Boxscores(datetime(2017, 7, 17), datetime(2017, 7, 20))
print(games.games)
```

## Player

The `Player` module contains `AbstractPlayer`, a base class inherited by both
`BoxscorePlayer` (from `Boxscore`) and `Player` (from `Roster`). All properties
on `AbstractPlayer` are available from either child class.

## Roster

The `Roster` module provides detailed player information via the `Player` class,
including career statistics, height, weight, nationality, and season-by-season
breakdowns.

```python
from sportsipy.mlb.roster import Player

altuve = Player('altuvjo01')
print(altuve.name)       # Prints 'José Altuve'
print(altuve.hits)       # Prints Altuve's career hits total
print(altuve.dataframe)  # Polars DataFrame of all stats per season
```

By default, career stats are returned. To request a specific season, call the
instance with the season string:

```python
altuve = Player('altuvjo01')
print(altuve.hits)             # Career hits
print(altuve('2017').hits)     # 2017 season hits
print(altuve.home_runs)        # Home runs for 2017 (last requested season)
print(altuve('Career').hits)   # Back to career stats
```

The `Roster` class pulls all players on a team's roster for a given season:

```python
from sportsipy.mlb.roster import Roster

astros = Roster('HOU')
for player in astros.players:
    print(player.name)
```

## Schedule

The `Schedule` module iterates over all games in a team's schedule.

```python
from sportsipy.mlb.schedule import Schedule

houston_schedule = Schedule('HOU')
for game in houston_schedule:
    print(game.date)     # Date the game was played
    print(game.result)   # Win or loss
    boxscore = game.boxscore  # Boxscore instance for this game
```

## Teams

The `Teams` module exposes season-level information for all MLB teams, including
team name, abbreviation, wins, stolen bases, batting average, and much more.

```python
from sportsipy.mlb.teams import Teams

teams = Teams()
for team in teams:
    print(team.name)             # Team name
    print(team.batting_average)  # Team batting average for the season
```

Request a specific team directly using its 3-letter abbreviation:

```python
from sportsipy.mlb.teams import Team

houston = Team('HOU')
```

Each `Team` instance links to `Schedule` and `Roster`:

```python
teams = Teams()
for team in teams:
    schedule = team.schedule             # Schedule instance
    df = team.schedule.dataframe_extended  # Polars DataFrame of all game boxscores

    roster = team.roster
    for player in roster.players:
        print(player.name)
```
