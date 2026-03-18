# NCAAB Package (`sportsipy.ncaab`)

The NCAAB package offers multiple modules that can be used to retrieve
information and statistics for Men's Division I College Basketball, such as team
names, season stats, game schedules, and boxscore metrics.

> **API Reference:** Detailed property and method documentation is available
> inline via docstrings in the
> [source code](../sportsipy/ncaab/).

## Boxscore

The `Boxscore` module retrieves information for a specific game. Metrics range
from points scored to blocked shots, assist percentage, and much more.

```python
from sportsipy.ncaab.boxscore import Boxscore

game_data = Boxscore('2018-04-02-21-villanova')
print(game_data.home_points)  # Prints 79
print(game_data.away_points)  # Prints 62
df = game_data.dataframe      # Returns a Polars DataFrame of game metrics
```

The `Boxscores` class searches for all games on a particular day:

```python
from datetime import datetime
from sportsipy.ncaab.boxscore import Boxscores

games_today = Boxscores(datetime.today())
print(games_today.games)

# Query a range of dates
games = Boxscores(datetime(2017, 11, 11), datetime(2017, 11, 12))
print(games.games)
```

## Conferences

The `Conferences` module allows conference data to be pulled for any season.

```python
from sportsipy.ncaab.conferences import Conferences

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

The `Rankings` class queries AP Men's Division-I Basketball rankings
week-by-week.

```python
from sportsipy.ncaab.rankings import Rankings

rankings = Rankings()
print(rankings.current)           # Dict of team abbreviation → current rank
print(rankings.current_extended)  # Detailed info for all teams this week
print(rankings.complete)          # Detailed info for all teams all season
```

## Roster

The `Roster` module provides detailed player information via the `Player` class.

```python
from sportsipy.ncaab.roster import Player

carsen_edwards = Player('carsen-edwards-1')
print(carsen_edwards.name)       # Prints 'Carsen Edwards'
print(carsen_edwards.points)     # Career points total
print(carsen_edwards.dataframe)  # Polars DataFrame of all stats per season
```

Request a specific season:

```python
carsen_edwards = Player('carsen-edwards-1')
print(carsen_edwards.points)              # Career points
print(carsen_edwards('2017-18').points)   # 2017-18 season points
print(carsen_edwards.games_played)        # Games played in 2017-18
print(carsen_edwards('Career').points)    # Back to career stats
```

Pull a full team roster:

```python
from sportsipy.ncaab.roster import Roster

purdue = Roster('PURDUE')
for player in purdue.players:
    print(player.name)
```

## Schedule

```python
from sportsipy.ncaab.schedule import Schedule

purdue_schedule = Schedule('PURDUE')
for game in purdue_schedule:
    print(game.date)
    print(game.result)
    boxscore = game.boxscore
```

## Teams

```python
from sportsipy.ncaab.teams import Teams

teams = Teams()
for team in teams:
    print(team.name)    # Team name
    print(team.blocks)  # Total blocked shots for the season
```

Request a specific team using its abbreviation:

```python
from sportsipy.ncaab.teams import Team

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
