"""Provide utilities for nfl tests."""

import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(sys.path[0])))
from sportsipy.nfl.teams import Teams

logging.basicConfig(level=logging.INFO, format="%(message)s")
LOGGER = logging.getLogger(__name__)

for team in Teams():
    LOGGER.info(team.name)
    for player in team.roster.players:
        LOGGER.info(player.name)
    for game in team.schedule:
        LOGGER.info(game.dataframe)
        LOGGER.info(game.dataframe_extended)
