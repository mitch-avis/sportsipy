# Sportsipy: A free sports API for Python

## Development status

Started in early 2023, this project is an active fork of
[`roclark/sportsipy`](https://github.com/roclark/sportsipy), building on
the fixes introduced in
[`davidjkrause/sportsipy`](https://github.com/davidjkrause/sportsipy).
The current fork is maintained at
[`mitch-avis/sportsipy`](https://github.com/mitch-avis/sportsipy).

Note that not all existing functions work due to changes on the source site,
but fixes will be integrated as they are identified.

## Background

Sportsipy is a free Python API that pulls stats from
`www.sports-reference.com` and allows them to be used in Python-based
applications, especially ones involving data analytics and machine learning.

Sportsipy exposes a plethora of sports information from major sports leagues
in North America, such as the MLB, NBA, College Football and Basketball, NFL,
and NHL. Sportsipy also supports Professional Football (Soccer) for thousands
of teams from leagues around the world. Every sport has its own set of valid
API queries ranging from the list of teams in a league, to the date and time of
a game, to the total number of wins a team has secured during the season, and
many, many more metrics that paint a more detailed picture of how a team has
performed during a game or throughout a season.

## Installation

**Important**: This fork is not the reference on PyPI. To include this fork in
your requirements:

```bash
pip install git+https://github.com/mitch-avis/sportsipy@master
```

If the bleeding-edge source version of `sportsipy` is desired, clone this
repository using git and install all of the package requirements with pip:

```bash
git clone https://github.com/mitch-avis/sportsipy
cd sportsipy
pip install -r requirements.txt
```

Once complete, create a Python wheel for your default version of Python by
running the following command:

```bash
python -m build
```

This will create a `.whl` file in the `dist` directory which can be installed
with the following command:

```bash
pip install dist/*.whl
```

## Examples

The following are a few examples showcasing how easy it can be to collect an
abundance of metrics and information from all of the tracked leagues. The
examples below are only a miniscule subset of the total number of statistics
that can be pulled using sportsipy. Visit the documentation on
[Read The Docs](http://sportsipy.readthedocs.io/en/latest/) for a complete list
of all information exposed by the API.

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

### Get a Pandas DataFrame of all stats for a MLB game

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

## Documentation

Two blog posts detailing the creation and basic usage of `sportsipy` can be
found on Medium:

- [Part 1: Creating a public sports API](https://medium.com/clarktech-sports/python-sports-analytics-made-simple-part-1-14569d6e9a86)
- [Part 2: Pull any sports metric in 10 lines of Python](https://medium.com/clarktech-sports/python-sports-analytics-made-simple-part-2-40e591a7f3db)

The second post in particular is a great guide for getting started with
`sportsipy` and is highly recommended for anyone who is new to the package.

Complete documentation is hosted on
[Read The Docs](http://sportsipy.readthedocs.io/en/latest/). The documentation
is auto-generated using Sphinx based on the docstrings in the sportsipy package.

## Testing

Sportsipy contains a testing suite which aims to test all major portions of
code for proper functionality. To run the test suite against your environment,
ensure all of the requirements are installed by running:

```bash
pip install -r requirements.txt
```

Next, start the tests by running `pytest` while optionally including coverage
flags which identify the amount of production code covered by the testing
framework:

```bash
pytest --cov=sportsipy --cov-report term-missing tests/
```

If the tests are successful, it will return a green line with a message at the
end of the output similar to the following:

```text
======================= 380 passed in 245.56 seconds =======================
```

If a test fails, it will show the number of failed tests and what went wrong.
If that's the case, ensure you have the latest version of code and are in a
supported environment. Otherwise, create an issue on GitHub to attempt to get
the issue resolved.

## Responsible scraping

This project scrapes data from the sports-reference family of sites. Please
be respectful and stay within their limits. The default rate limiter enforces
at least 3 seconds between requests (20 requests per minute). You can
configure it via environment variables such as:

- `SPORTSIPY_RATE_LIMIT_SECONDS` (minimum enforced is 3.0)
- `SPORTSIPY_DISABLE_RATE_LIMIT=1` (only for testing or controlled use)

## Fork lineage and credits

- Original project: [`roclark/sportsipy`](https://github.com/roclark/sportsipy)
- Intermediate fork with fixes: [`davidjkrause/sportsipy`](https://github.com/davidjkrause/sportsipy)
- Current maintained fork: [`mitch-avis/sportsipy`](https://github.com/mitch-avis/sportsipy)
