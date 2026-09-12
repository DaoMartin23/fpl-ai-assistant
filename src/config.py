# central place for paths and API keys used across the project
# added so that modules can be moved into src/ and app/ without breaking file paths

import os
import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # loads variables from a local .env file, if present

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = str(BASE_DIR / "data" / "full_player_lists.db")
MODELS_DIR = str(BASE_DIR / "models")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")

# the Premier League and Understat both identify a season by the year it starts in
# (e.g. 2025 for the 2025/26 season). Worked out from today's date, shared by both
# src/data_collection.py functions that need it, so it doesn't go stale

_today = datetime.date.today()
CURRENT_SEASON_START_YEAR = _today.year if _today.month >= 7 else _today.year - 1
