# orchestration script that rebuilds the player/club database and retrains the
# Random Forest prediction models. This is the equivalent of the module-level
# code that used to run automatically at the bottom of FPL_Database.py.
#
# Note: this recreates the database tables from scratch, so an existing
# data/full_player_lists.db must be removed before re-running (this matches
# the original project's behaviour).

import os

from src.config import DB_PATH, MODELS_DIR
from src.data_collection import get_fplData, get_understatData, get_premier_league_data
from src.data_processing import merge_dataframes
from src.database import create_database, player_into_objects, clubs_into_objects, prediction_into_database
from src import entities
from src.train_models import (
    train_random_forest_defender,
    train_random_forest_midfielder,
    train_random_forest_attacker,
    train_random_forest_goalkeeper,
)


def main():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)

    # dataframe creation functions are used
    understat_df = get_understatData()
    fpl_df = get_fplData()
    teams_df = get_premier_league_data()
    merged_df = merge_dataframes(understat_df, fpl_df)

    # the dataframes are used to create the database
    create_database(merged_df, teams_df, DB_PATH)

    # the database is used to create the classes
    players = player_into_objects(DB_PATH)
    clubs = clubs_into_objects(DB_PATH)
    entities.clubs = clubs  # exposed at module level for Player/Goalkeeper.get_prediction()

    # the prediction models are trained
    train_random_forest_defender(players, clubs, MODELS_DIR)
    train_random_forest_midfielder(players, clubs, MODELS_DIR)
    train_random_forest_attacker(players, clubs, MODELS_DIR)
    train_random_forest_goalkeeper(players, clubs, MODELS_DIR)

    # the prediction is stored back within the database
    prediction_into_database(DB_PATH, players)


if __name__ == "__main__":
    main()
