# NFL Package (`sportsipy.nfl`)

The NFL package offers multiple modules that can be used to retrieve information
and statistics for the National Football League, such as team names, season
stats, game schedules, and boxscore metrics.

> **API Reference:** Detailed property and method documentation is available
> inline via docstrings in the
> [source code](../sportsipy/nfl/).

## Boxscore

The `Boxscore` module retrieves information for a specific game. Metrics range
from points scored to passing yards, yards lost from sacks, and much more.

```python
from sportsipy.nfl.boxscore import Boxscore

game_data = Boxscore('201802040nwe')
print(game_data.home_points)  # Prints 33
print(game_data.away_points)  # Prints 41
df = game_data.dataframe      # Returns a Polars DataFrame of game metrics
```

The `Boxscores` class searches for all games during a particular week:

```python
from sportsipy.nfl.boxscore import Boxscores

# All games in week 1 of 2017
games_week1 = Boxscores(1, 2017)
print(games_week1.games)

# All games from weeks 7 and 8 of 2017
games = Boxscores(7, 2017, 8)
print(games.games)
```

## Player

The `Player` module contains `AbstractPlayer`, a base class inherited by both
`BoxscorePlayer` (from `Boxscore`) and `Player` (from `Roster`). All properties
on `AbstractPlayer` are available from either child class.

## Roster

The `Roster` module provides detailed player information via the `Player` class,
including career touchdowns, passing yards, single-season stats, and player
height, weight, and nationality.

```python
from sportsipy.nfl.roster import Player

brees = Player('BreeDr00')
print(brees.name)           # Prints 'Drew Brees'
print(brees.passing_yards)  # Career passing yards
print(brees.dataframe)      # Polars DataFrame of all stats per season
```

Request a specific season:

```python
brees = Player('BreeDr00')
print(brees.passing_yards)              # Career passing yards
print(brees('2017').passing_yards)      # 2017 season passing yards
print(brees.passing_touchdowns)         # TDs for 2017
print(brees('Career').passing_yards)    # Back to career stats
```

Pull a full team roster:

```python
from sportsipy.nfl.roster import Roster

saints = Roster('NOR')
for player in saints.players:
    print(player.name)
```

## Schedule

```python
from sportsipy.nfl.schedule import Schedule

houston_schedule = Schedule('HTX')
for game in houston_schedule:
    print(game.date)
    print(game.result)
    boxscore = game.boxscore
```

## Teams

```python
from sportsipy.nfl.teams import Teams

teams = Teams()
for team in teams:
    print(team.name)               # Team name
    print(team.margin_of_victory)  # Average margin of victory
```

Request a specific team using its 3-letter abbreviation:

```python
from sportsipy.nfl.teams import Team

kansas = Team('KAN')
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
