"""Provide utilities for nba tests."""

import logging
import os
import sys
from typing import Any

sys.path.append(os.path.dirname(os.path.dirname(sys.path[0])))
from sportsipy.nba.teams import Teams

logging.basicConfig(level=logging.INFO, format="%(message)s")
LOGGER = logging.getLogger(__name__)

for team in Teams():
    team_obj: Any = team
    LOGGER.info(team_obj.name)
    for player in team_obj.roster.players:
        try:
            LOGGER.info(player.name)
        except UnicodeEncodeError:
            LOGGER.info(player.name.encode("utf-8"))
    for game in team_obj.schedule:
        LOGGER.info(game.dataframe)
        LOGGER.info(game.dataframe_extended)
