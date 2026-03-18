# Sportsipy: A free sports API written for Python

Sportsipy is a free Python API that pulls stats from
[www.sports-reference.com](https://www.sports-reference.com) and makes them
easily available for Python-based applications, especially those involving data
analytics and machine learning.

Sportsipy exposes a plethora of sports information from major sports leagues in
North America, such as the MLB, NBA, College Football and Basketball, NFL, and
NHL. Every sport has its own set of valid API queries ranging from the list of
teams in a league, to the date and time of a game, to the total number of wins
a team has secured during the season, and many, many more metrics.

## Quick-start Examples

The following examples showcase how easy it can be to collect an abundance of
metrics and information from all of the tracked leagues. Visit the per-sport
documentation pages for a complete list of all information exposed by the API.

### Get instances of all NHL teams for the 2018 season

```python
from sportsipy.nhl.teams import Teams

teams = Teams(2018)
```

### Print every NBA team's name and abbreviation

```python
from sportsipy.nba.teams import Teams

teams = Teams()
for team in teams:
    print(team.name, team.abbreviation)
```

### Get a specific NFL team's season information

```python
from sportsipy.nfl.teams import Teams

teams = Teams()
lions = teams('DET')
```

### Print the date of every game for a NCAA Men's Basketball team

```python
from sportsipy.ncaab.schedule import Schedule

purdue_schedule = Schedule('purdue')
for game in purdue_schedule:
    print(game.date)
```

### Print the number of interceptions by the away team in a NCAA Football game

```python
from sportsipy.ncaaf.boxscore import Boxscore

championship_game = Boxscore('2018-01-08-georgia')
print(championship_game.away_interceptions)
```

### Get a Polars DataFrame of all stats for a MLB game

```python
from sportsipy.mlb.boxscore import Boxscore

game = Boxscore('BOS201806070')
df = game.dataframe
```

### Find the number of goals a football team has scored

```python
from sportsipy.fb.team import Team

tottenham = Team('Tottenham Hotspur')
print(tottenham.goals_scored)
```

## Contents

- [Installation](installation.md)
- [Examples](examples.md)
- [Testing](testing.md)
- [API Documentation](api.md)
  - [Football/Soccer (fb)](fb.md)
  - [MLB](mlb.md)
  - [NBA](nba.md)
  - [NCAAB](ncaab.md)
  - [NCAAF](ncaaf.md)
  - [NFL](nfl.md)
  - [NHL](nhl.md)
