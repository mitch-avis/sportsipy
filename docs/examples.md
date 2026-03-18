# Examples

Thanks to the broad range of metrics pulled from sports-reference.com, there
are multiple ways you can use the `sportsipy` package. This page has multiple
examples beyond those on the home page to demonstrate some of the things you
can do with the tool. In general, most examples shown for a specific sport are
applicable for all sports currently supported by `sportsipy`.

## Finding Tallest Players

For each team, find the tallest player on the roster and print their name and
height in inches.

```python
from sportsipy.nba.teams import Teams


def get_height_in_inches(height):
    feet, inches = height.split('-')
    return int(feet) * 12 + int(inches)


def print_tallest_player(team_heights):
    tallest_player = max(team_heights, key=team_heights.get)
    print('%s: %s in.' % (tallest_player, team_heights[tallest_player]))


for team in Teams():
    print('=' * 80)
    print(team.name)
    team_heights = {}
    for player in team.roster.players:
        height = get_height_in_inches(player.height)
        team_heights[player.name] = height
    print_tallest_player(team_heights)
```

## Saving Data with Polars

To avoid re-fetching data for completed games, save the Polars DataFrame to
the local filesystem. Two common formats are CSV and Parquet.

```python
from sportsipy.ncaab.teams import Teams

for team in Teams():
    # Save as CSV
    team.dataframe.write_csv('%s.csv' % team.abbreviation.lower())
    # Save as Parquet (faster, lossless)
    team.dataframe.write_parquet('%s.parquet' % team.abbreviation.lower())
```

## Finding Top Win Percentage by Year

For each year in a range, find the team with the most wins during the season
and print their name and win total.

```python
from sportsipy.mlb.teams import Teams


def print_most_wins(year, wins):
    most_wins = max(wins, key=wins.get)
    print('%s: %s - %s' % (year, wins[most_wins], most_wins))


for year in range(2000, 2023):
    wins = {}
    for team in Teams(year):
        wins[team.name] = team.wins
    print_most_wins(year, wins)
```

## Aggregating Stats Across a Season

Pull all game boxscores for every team in a league and build a combined
Polars DataFrame.

```python
import polars as pl
from sportsipy.nfl.teams import Teams

all_dfs = []
for team in Teams():
    df = team.schedule.dataframe_extended
    if df is not None:
        all_dfs.append(df)

combined = pl.concat(all_dfs)
print(combined.head())
```

## Using Squad IDs for Soccer Teams

Since there may be multiple teams with similar names across leagues, using
the unique 8-digit squad ID guarantees you get the right team.

```python
from sportsipy.fb.fb_utils import lookup_squad_id
from sportsipy.fb.team import Team

# Look up the squad ID for a team by name
squad_id = lookup_squad_id('Tottenham Hotspur')
print(squad_id)  # Prints '361ca564'

# Use the squad ID to instantiate the team
tottenham = Team('361ca564')
print(tottenham.goals_scored)
```
