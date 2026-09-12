# Fantasy Premier League AI Assistant

## Overview

A Python application that collects Fantasy Premier League (FPL) and Premier League data from multiple sources, combines it into a single SQLite database, trains Random Forest models to predict each player's fantasy points for their next gameweek, and exposes the whole thing through a Streamlit chatbot that can answer natural-language questions about players, clubs and predictions.

Originally developed and tested during the 2024/25 Premier League season. The repository has been reorganised and documented for portfolio purposes; some components may require updates to work with current external APIs and dependencies. It always targets whichever Premier League season is currently live (worked out from today's date), so running it against a season also requires that season to be far enough along — see [Running the Application](#running-the-application).

## Features

- Collects live player data from the official FPL API (season totals, price, minutes, recent gameweek history).
- Fetches advanced attacking metrics (xG, xA, shots, key passes) from Understat's data endpoint.
- Fetches club standings, past results and upcoming fixtures from the football-data.org API.
- Cleans and fuzzy-matches player names across data sources (FPL and Understat format player names differently) using FuzzyWuzzy.
- Stores everything in a relational SQLite database (`player_stats` and `club_stats` tables, linked by club name).
- Trains four separate Random Forest Regressor models (goalkeepers, defenders, midfielders, attackers) to predict next-gameweek fantasy points, and writes predictions back into the database.
- A Streamlit chatbot that answers FPL questions either via a LangChain SQL agent (for questions about the data) or directly via the LLM (for general questions).

## Technologies

- Python
- Pandas / NumPy
- SQLite (via the `sqlite3` standard library module)
- Scikit-learn (`RandomForestRegressor`, `train_test_split`, MSE/R² evaluation)
- Joblib (model persistence)
- LangChain + LangChain-OpenAI (SQL agent)
- OpenAI API (`gpt-4o`)
- Streamlit (web interface)
- Requests (web scraping / API calls)
- FuzzyWuzzy (fuzzy string matching)
- python-dotenv (environment variable loading)

## Architecture

```
FPL API ─┐
Understat ├─► data collection ─► name matching / merge ─► SQLite database ─► Random Forest models ─► predictions written back to DB
football-data.org ─┘                                              │
                                                                    ▼
                                                          Streamlit chatbot (LangChain SQL agent + gpt-4o)
```

`build_database.py` runs the full data collection → merge → database → training → prediction pipeline. `app/chatbot.py` is the Streamlit application that reads from the resulting database. `run.py` runs the pipeline once and then launches the chatbot, matching how the project was originally used.

## Machine Learning

- **Target:** a player's fantasy points in their most recent completed gameweek.
- **Model:** `RandomForestRegressor` (scikit-learn) — one model per position (GK / DEF / MID / ATT), each with its own hand-tuned hyperparameters (number of trees, max depth, min samples per split/leaf), since different positions are scored on different criteria (e.g. clean sheets and saves matter for goalkeepers/defenders, goals/assists/xG for attacking players).
- **Features:** a player's season totals, points from the preceding gameweeks, minutes played, and (position-dependent) goals, assists, xG, xA, shots, key passes, goals conceded and expected goals conceded, combined with their club's goals scored/conceded, league points and next opponent.
- **Training:** each model is trained on a held-out test split (10–30% depending on position) using `train_test_split`, and evaluated with **Mean Squared Error** and **R² score**, printed to the console during training. These are exploratory metrics from a single train/test split rather than a rigorously validated benchmark — see Limitations below.
- Trained models are saved with `joblib` (`models/<POSITION>_Prediction.pkl`) so they don't need to be retrained on every prediction.

## Data Sources

- [Fantasy Premier League API](https://fantasy.premierleague.com/api/bootstrap-static/) — player prices, points, minutes, positions, per-gameweek history.
- [Understat](https://understat.com/) — xG, xA, shots, key passes, fetched from its internal `getLeagueData` JSON endpoint for the current season (worked out from today's date).
- [football-data.org API](https://www.football-data.org/) — league standings, results and fixtures (requires a free API key).

## Installation

```bash
git clone <this-repo-url>
cd FPL-AI-Assistant
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your own keys:

```
OPENAI_API_KEY=your-openai-key
FOOTBALL_DATA_API_KEY=your-football-data-org-key
```

- Get an OpenAI API key from https://platform.openai.com/.
- Get a free football-data.org API key from https://www.football-data.org/.

## Running the Application

```bash
python run.py
```

This rebuilds the database and prediction models from live data, then launches the Streamlit chatbot at `http://localhost:8501`.

**Note:** this requires the current Premier League season to have at least 5 finished gameweeks *and* still have upcoming fixtures scheduled (i.e. it must be genuinely mid-season, not right at the start or after it's finished) — the feature set needs a club's last 5 results as well as its next 3 fixtures. This matches how the project was originally developed and tested, well into the 2024/25 season; if you run it very early in a new season, `build_database.py` will fail with an `IndexError` until enough gameweeks have been played.

To only rebuild the database/models without launching the chatbot:

```bash
python build_database.py
```

To launch the chatbot against an already-built database, without rebuilding:

```bash
streamlit run app/chatbot.py
```

## Project Structure

```
FPL-AI-Assistant/
├── run.py                   # builds the database, then launches the chatbot
├── build_database.py        # data collection → merge → database → model training pipeline
├── app/
│   └── chatbot.py           # Streamlit chatbot (LangChain SQL agent + gpt-4o)
├── src/
│   ├── config.py            # paths and environment variables
│   ├── data_collection.py   # FPL API / Understat / football-data.org scraping
│   ├── data_processing.py   # name normalisation and fuzzy-matching / dataframe merging
│   ├── database.py          # SQLite schema creation and object loading
│   ├── entities.py          # Player, Goalkeeper, Club classes and prediction logic
│   └── train_models.py      # Random Forest training per position
├── data/                    # generated SQLite database (not committed)
├── models/                  # generated .pkl model files (not committed)
├── requirements.txt
└── .env.example
```

## Limitations / Future Improvements

- The pipeline needs the current season to be mid-way through — at least 5 finished gameweeks, with fixtures still remaining — since it was originally built and tested during the 2024/25 season under that assumption. It doesn't work at the very start of a season (not enough finished matches yet) or once a season has ended (no fixtures left to predict against). See the note under [Running the Application](#running-the-application).
- Rebuilding the database (`build_database.py`) creates the SQLite tables from scratch, so an existing `data/full_player_lists.db` needs to be deleted before re-running the pipeline.
- Fetching club fixtures/results from football-data.org is rate-limited to one request every 15 seconds per team, so a full rebuild takes several minutes.
- Model evaluation currently relies on a single train/test split (MSE and R² printed at training time) rather than cross-validation, so reported scores should be treated as indicative rather than a rigorous benchmark.
- Name-matching between FPL and Understat uses a fixed 86% fuzzy-match threshold, which can occasionally mismatch or miss players with very similar names.
- The chatbot decides between the SQL agent and a plain LLM response using a fixed keyword list, rather than a more general intent classifier.
- Understat's `getLeagueData` endpoint is an internal, undocumented API rather than a public one, so it could change or be removed without notice, as happened to the previous HTML-embedded approach it replaced.

## Author

Martin Dao
