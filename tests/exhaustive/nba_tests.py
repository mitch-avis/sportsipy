"""Provide utilities for nba tests."""

import os
import sys
from typing import Any

sys.path.append(os.path.dirname(os.path.dirname(sys.path[0])))
from sportsipy.nba.teams import Teams

for team in Teams():
    team_obj: Any = team
    print(team_obj.name)
    for player in team_obj.roster.players:
        try:
            print(player.name)
        except UnicodeEncodeError:
            print(player.name.encode("utf-8"))
    for game in team_obj.schedule:
        print(game.dataframe)
        print(game.dataframe_extended)
