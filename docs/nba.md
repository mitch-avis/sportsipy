# NBA Package (`sportsipy.nba`)

The NBA package offers multiple modules that can be used to retrieve information
and statistics for the National Basketball Association, such as team names,
season stats, game schedules, and boxscore metrics.

> **API Reference:** Detailed property and method documentation is available
> inline via docstrings in the
> [source code](../sportsipy/nba/).

## Boxscore

The `Boxscore` module retrieves information for a specific game. Metrics range
from points scored to free throws made, assist rates, and much more. Pass a
boxscore URI from sports-reference.com (retrievable from `Schedule`) to
instantiate.

```python
from sportsipy.nba.boxscore import Boxscore

game_data = Boxscore('201806080CLE')
print(game_data.away_points)  # Prints 108
print(game_data.home_points)  # Prints 85
df = game_data.dataframe      # Returns a Polars DataFrame of game metrics
```

The `Boxscores` class searches for all games on a particular day:

```python
from datetime import datetime
from sportsipy.nba.boxscore import Boxscores

games_today = Boxscores(datetime.today())
print(games_today.games)  # Dictionary of all matchups for today

# Query a range of dates
games = Boxscores(datetime(2018, 1, 1), datetime(2018, 1, 5))
print(games.games)
```

## Player

The `Player` module contains `AbstractPlayer`, a base class inherited by both
`BoxscorePlayer` (from `Boxscore`) and `Player` (from `Roster`). All properties
on `AbstractPlayer` are available from either child class.

## Roster

The `Roster` module provides detailed player information via the `Player` class.

```python
from sportsipy.nba.roster import Player

james_harden = Player('hardeja01')
print(james_harden.name)      # Prints 'James Harden'
print(james_harden.points)    # Career points total
print(james_harden.dataframe) # Polars DataFrame of all stats per season
print(james_harden.salary)    # Career earnings
print(james_harden.contract)  # Contract by yearly wages
```

Request a specific season by calling the instance with the season string:

```python
james_harden = Player('hardeja01')
print(james_harden.points)              # Career points
print(james_harden('2017-18').points)   # 2017-18 season points
print(james_harden.games_played)        # Games played in 2017-18
print(james_harden('Career').points)    # Back to career stats
```

The `Roster` class pulls all players on a team's roster:

```python
from sportsipy.nba.roster import Roster

houston = Roster('HOU')
for player in houston.players:
    print(player.name)
```

## Schedule

The `Schedule` module iterates over all games in a team's schedule.

```python
from sportsipy.nba.schedule import Schedule

houston_schedule = Schedule('HOU')
for game in houston_schedule:
    print(game.date)    # Date the game was played
    print(game.result)  # Win or loss
    boxscore = game.boxscore  # Boxscore instance for this game
```

## Teams

The `Teams` module exposes season-level information for all NBA teams.

```python
from sportsipy.nba.teams import Teams

teams = Teams()
for team in teams:
    print(team.name)    # Team name
    print(team.blocks)  # Total blocked shots for the season
```

Request a specific team using its 3-letter abbreviation:

```python
from sportsipy.nba.teams import Team

houston = Team('HOU')
```

Each `Team` instance links to `Schedule` and `Roster`:

```python
teams = Teams()
for team in teams:
    schedule = team.schedule
    df = team.schedule.dataframe_extended  # Polars DataFrame of all game boxscores

    roster = team.roster
    for player in roster.players:
        print(player.name)
```
