"""Provide utilities for ncaab tests."""

import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(sys.path[0])))
from sportsipy.ncaab.conferences import Conferences
from sportsipy.ncaab.rankings import Rankings
from sportsipy.ncaab.teams import Teams

logging.basicConfig(level=logging.INFO, format="%(message)s")
LOGGER = logging.getLogger(__name__)

for team in Teams():
    LOGGER.info(team.name)
    for player in team.roster.players:
        LOGGER.info(player.name.encode("utf-8"))
    for game in team.schedule:
        LOGGER.info(game.dataframe)
        LOGGER.info(game.dataframe_extended)

conferences = Conferences()
LOGGER.info(conferences.conferences)
LOGGER.info(conferences.team_conference)

rankings = Rankings()
LOGGER.info(rankings.current)
LOGGER.info(rankings.current_extended)
LOGGER.info(rankings.complete)
