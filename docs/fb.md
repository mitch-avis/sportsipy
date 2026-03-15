# Football/Soccer Package (`sportsipy.fb`)

The Football (soccer) package offers multiple modules that can be used to
retrieve information and statistics for thousands of football teams around the
world, such as team names, season stats, game schedules, and competition
results.

> **API Reference:** Detailed property and method documentation is available
> inline via docstrings in the
> [source code](../sportsipy/fb/).

## Team

The `Team` module is used to grab high-level stats and information for a
specific team. Information ranges from the team's primary competition, their
position and point value in the league, goals scored, and much more.

The easiest way to instantiate a team is to pass the squad's 8-digit ID number.
Squad IDs can be found in `sportsipy.fb.squad_ids` or by using
`lookup_squad_id()`. Alternatively, the team name can be passed and the
corresponding squad ID will be retrieved automatically.

```python
from sportsipy.fb.team import Team

tottenham = Team('Tottenham Hotspur')  # Equivalent to Team('361ca564')
print(tottenham.league)         # Prints 'Premier League'
print(tottenham.goals_scored)   # Prints 47
print(tottenham.home_record)    # Prints '8-2-4'
```

## Schedule

The `Schedule` module iterates over all games in a team's schedule to get
high-level game information such as the date, score, result, and more. Either
the full team name or, preferably, the team's 8-digit squad ID can be used.

```python
from sportsipy.fb.schedule import Schedule

tottenham_schedule = Schedule('Tottenham Hotspur')
print(len(tottenham_schedule))  # Prints the total number of games (e.g. 52)
for game in tottenham_schedule:
    print(game.datetime)       # Prints the datetime for each game
    print(game.goals_scored)   # Prints the number of goals the team scored
    print(game.captain)        # Prints the primary captain's name
```

The `Schedule` can also be accessed via the `Team` class:

```python
from sportsipy.fb.team import Team

tottenham = Team('Tottenham Hotspur')
for game in tottenham.schedule:
    print(game.datetime)
```

## Roster

The `Roster` module contains detailed player information for every player on a
team's roster. Each player instantiates the `SquadPlayer` class which includes
individual statistics such as goals, shots, assists, playtime, and much more.

```python
from sportsipy.fb.roster import Roster

tottenham = Roster('Tottenham Hotspur')
for player in tottenham:
    print(player.name)      # Prints the name of each player
    print(player.goals)     # Prints the number of goals the player scored
    print(player.assists)   # Prints the number of assists

# A specific player can be queried by name or player ID
harry_kane = tottenham('Harry Kane')
print(harry_kane.goals)
print(harry_kane.assists)
```

## Utility: Looking Up Squad IDs

Since multiple teams in different leagues may share similar names, use the
8-digit squad ID to guarantee the correct team is used.

```python
from sportsipy.fb.fb_utils import lookup_squad_id

# Returns the squad ID string if an exact match is found
squad_id = lookup_squad_id('Tottenham Hotspur')
print(squad_id)  # Prints '361ca564'

# Returns a dictionary of suggestions if no exact match is found
suggestions = lookup_squad_id('Tottenham')
print(suggestions)
```
