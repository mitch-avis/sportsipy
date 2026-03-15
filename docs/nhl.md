# NHL Package (`sportsipy.nhl`)

The NHL package offers multiple modules that can be used to retrieve information
and statistics for the National Hockey League, such as team names, season stats,
game schedules, and boxscore metrics.

> **API Reference:** Detailed property and method documentation is available
> inline via docstrings in the
> [source code](../sportsipy/nhl/).

## Boxscore

The `Boxscore` module retrieves information for a specific game. Metrics range
from goals and shots on goal to power play goals and penalty minutes.

```python
from sportsipy.nhl.boxscore import Boxscore

game_data = Boxscore('201806070VEG')
print(game_data.home_goals)   # Prints 3
print(game_data.away_goals)   # Prints 4
df = game_data.dataframe      # Returns a Polars DataFrame of game metrics
```

The `Boxscores` class searches for all games on a given date or within a range
of dates:

```python
from datetime import datetime
from sportsipy.nhl.boxscore import Boxscores

# All games played today
games_today = Boxscores(datetime.today())
print(games_today.games)

# All games between Feb 4 and Feb 5 2017
games = Boxscores(datetime(2017, 2, 4), datetime(2017, 2, 5))
print(games.games)
```

## Player

The `Player` module contains `AbstractPlayer`, a base class inherited by both
`BoxscorePlayer` (from `Boxscore`) and `Player` (from `Roster`). All properties
on `AbstractPlayer` are available from either child class.

## Roster

The `Roster` module provides detailed player information via the `Player` class,
including career goals, assists, plus/minus, and single-season breakdowns.

```python
from sportsipy.nhl.roster import Player

zetterberg = Player('zettehe01')
print(zetterberg.name)   # Prints 'Henrik Zetterberg'
print(zetterberg.goals)  # Career goals
print(zetterberg.dataframe)  # Polars DataFrame of all stats per season
```

Request a specific season:

```python
zetterberg = Player('zettehe01')
print(zetterberg.goals)              # Career goals
print(zetterberg('2018').goals)      # 2017-18 season goals
print(zetterberg.assists)            # Assists for 2017-18
print(zetterberg('Career').goals)    # Back to career goals
```

Pull a full team roster:

```python
from sportsipy.nhl.roster import Roster

detroit = Roster('DET')
for player in detroit.players:
    print(player.name)
```

## Schedule

```python
from sportsipy.nhl.schedule import Schedule

detroit_schedule = Schedule('DET')
for game in detroit_schedule:
    print(game.date)
    print(game.result)
    boxscore = game.boxscore
```

## Teams

```python
from sportsipy.nhl.teams import Teams

teams = Teams()
for team in teams:
    print(team.name)           # Team name
    print(team.shots_on_goal)  # Shots on goal this season
```

Request a specific team using its 3-letter abbreviation:

```python
from sportsipy.nhl.teams import Team

detroit = Team('DET')
```

Each `Team` instance links to `Schedule` and `Roster`:

```python
teams = Teams()
for team in teams:
    schedule = team.schedule
    df = team.schedule.dataframe_extended

    roster = team.roster
    for player in roster.players:
        print(player.name)
```
