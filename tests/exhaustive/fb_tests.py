"""Provide utilities for fb tests."""

import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(sys.path[0])))
from sportsipy.fb.squad_ids import SQUAD_IDS
from sportsipy.fb.team import Team

logging.basicConfig(level=logging.INFO, format="%(message)s")
LOGGER = logging.getLogger(__name__)

for team in list(set(SQUAD_IDS.values())):
    squad = Team(team)
    if squad.name:
        LOGGER.info(squad.name.encode("utf-8"))
    for game in squad.schedule:
        LOGGER.info(game.date)
    for player in squad.roster:
        if player.name:
            LOGGER.info(player.name.encode("utf-8"))
