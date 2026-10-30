Midterm Project Work Log

Music Search and Recommendation System

Dataset: Million Song Dataset + Spotify + Last.fm
Name: 許安生
Student ID: C13151164
Course: Database
**Review date:** November 3, 2026 (ROC 115), periods 5-7

> **Before submission:** Replace the identity placeholders and review the verification notes and provisional dates in this document. The code and project metadata were inspected, but the database import and live API endpoints were not successfully tested during the recorded work session.

## 1. Project Overview

This project is a music search and recommendation application organized into three layers:

1. A PostgreSQL database for music metadata, audio features, and user listening history.
2. A FastAPI service that queries the database and provides search and recommendation endpoints.
3. A Streamlit interface that sends HTTP requests to the API and presents search results, popular tracks, and recommendations.

The repository contains two source CSV files under `data/`:

- `Music Info.csv` — approximately 15 MB. The file present in the workspace is 14,985,870 bytes and contains the catalog metadata and audio features used by the loader.
- `User Listening History.csv` — approximately 602 MB. The file present in the workspace is 602,515,573 bytes and contains user, track, and play-count records.

The `tracks` table combines the catalog and Spotify audio-feature fields; the current schema does not create a separate Spotify table.

### Tools and dependencies

The project metadata requires Python 3.13 or later and declares FastAPI, pandas, psycopg2-binary, requests, SQLAlchemy, Streamlit, and Uvicorn. The project uses uv and has a `uv.lock` lockfile. The application code is separated into `ch4_database/`, `ch5_api/`, and `ch6_ui/`.

The project was developed in a Windows and VS Code environment. PostgreSQL 17 and the other setup details below are included from my setup notes and should be confirmed against the installed machine before submission.

### AI assistance

An AI assistant using Copilot SDK in VS Code helped explain errors and prepare or revise project code and documentation. I reviewed the code and ran the checks recorded in this worklog. Database loading and live API behavior still require my own end-to-end verification. If I also used other AI tools, I will identify them accurately and follow the course's AI-use policy.

## 2. Progress Timeline

The following dates reflect the project notes and available repository evidence. Confirm the personal setup dates before treating them as a complete activity history.

- **October 26:** The project worklog folder was created. According to my setup notes, I read the assignment, prepared the project environment and dataset, and installed/configured PostgreSQL. Confirm exact setup activities and times.
- **October 26-27:** Worked on the database schema and CSV loader. The loader code is present, but the import result and completion date have not been independently verified.
- **October 27:** Project metadata and dependencies were recorded; the API and Streamlit code were present, and the Streamlit UI was restyled. A Git root commit, `afae379`, was created on this date.
- **October 28-29:** These dates appeared in my original draft for API testing, demo rehearsal, and worklog completion. They are later than the date of this worklog entry, so treat them as planned dates unless I update this entry after completing those activities.

## 3. Chapters 1-3: Environment Setup

The application is configured as a Python project in `pyproject.toml`. The project requires Python 3.13 or newer, lists the libraries needed by the database loader, API, and UI, and uses `uv.lock` to record the resolved dependency set. The `.gitignore` excludes the local `.venv/`, the large `data/` directory, Python `__pycache__/` directories, and compiled Python files.

My setup notes describe installing or configuring Git, uv, PostgreSQL, and VS Code, and downloading and extracting the dataset. They also mention initializing the project and adding its Python packages with uv. Confirm the exact installation commands and PostgreSQL version on the machine before submission.

## 4. Chapter 4: Database, Listening Records, and Spotify Audio Features

### Schema

`ch4_database/schema.sql` defines two PostgreSQL tables:

- **`tracks`** uses `track_id` as its primary key. It stores track and artist names; Spotify preview URL and ID; tags and genre; year and duration; and audio-feature fields including danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, and time signature.
- **`listening_history`** stores `track_id`, `user_id`, and `playcount` for listening records.

The schema begins by dropping `listening_history` and `tracks` before creating them. Running the loader against a populated database therefore erases the existing contents of those tables. Back up the database and confirm before running it if the tables contain data that must be retained.

### CSV loader

`ch4_database/load_data.py` reads both CSV files from the project-level `data/` directory. It checks for required columns, removes duplicate catalog rows by `track_id`, converts selected integer catalog columns to nullable integers, and uses PostgreSQL `COPY` to load rows.

The history file is processed in chunks of 200,000 rows. The loader retains records whose `track_id` exists in the loaded catalog, drops records with missing required history values, and stops when the accumulated loaded-row count reaches its configured maximum of 2,000,000. It then creates indexes on `listening_history.user_id` and `listening_history.track_id`, and prints database row counts.

### Load result and verification status

The original draft reports **50,683 tracks**, **2,000,000 listening-history rows**, and a most-active user with **384 records**. These figures are included as reported notes, not as verified results: I did not run `load_data.py` during the recorded session. I paused when I found that the schema drops and recreates both tables and did not receive approval to proceed with that destructive action. Before submitting these counts as results, load the data into the intended database and confirm them with SQL queries.

The two-million-row limit is controlled by `MAX_HISTORY_ROWS` in `load_data.py`; increasing it allows more history rows to be loaded. A performance comparison at higher limits has not been recorded.

## 5. Chapter 5: Search and Recommendation API

`ch5_api/main.py` defines a FastAPI application connected to the local PostgreSQL database named `music`, using the `postgres` role. It reads the database password from the `DB_PASSWORD` environment variable rather than embedding a password in the connection configuration. During application startup, it loads tracks with complete audio features and prepares normalized feature vectors for similarity calculations.

The implemented endpoints are:

- **`/search`** — searches track names and artists using a case-insensitive partial match.
- **`/tracks/{track_id}`** — returns a track's stored fields or a 404 response if the track is not found.
- **`/popular`** — ranks tracks by the sum of their listening-history play counts.
- **`/users/{user_id}/history`** — returns a listener's most-played tracks.
- **`/recommend/similar/{track_id}`** — computes similarities from nine audio features. The code standardizes each feature across the loaded catalog, normalizes each track vector, and ranks other tracks by vector dot product.
- **`/recommend/user/{user_id}`** — finds up to 50 other users with the largest shared-history row counts, then scores tracks they played that the target user has not played. The score weights play counts by the peer-overlap count.

FastAPI provides an interactive endpoint page at `http://127.0.0.1:8000/docs` when the service starts successfully.

### API test status

The original draft says every endpoint was tested from `/docs`, including a search for “Creep.” That test result has not been confirmed in the recorded session. When I attempted to start Uvicorn, the application stopped during import with `KeyError: 'DB_PASSWORD'` because that environment variable was not set in the terminal. Set it before starting the API, verify that PostgreSQL is running and accessible, and then exercise each endpoint before recording successful API tests.

## 6. Chapter 6: User Interface

`ch6_ui/app.py` is the Streamlit front end. It calls the API using HTTP requests and presents three main tabs:

1. **Discover** — searches the catalog and offers similar-track recommendations for a selected result.
2. **Popular tracks** — displays a play-count bar chart and a track list.
3. **For a listener** — displays a user's listening history and recommendations based on other listeners' overlapping histories.

The UI was styled as a dark, green-accented music-discovery experience with a sidebar, a discovery banner, responsive spacing, and track cards. Track names and other displayed metadata are HTML-escaped before being inserted into the card markup. The interface displays messages for missing results and API connection errors.

The UI's Python syntax check passed, and Streamlit's `AppTest` completed without unhandled exceptions. During that test the API was unavailable, so the app displayed its connection-error message instead of real catalog data. A local Streamlit server returned HTTP 200 during a smoke test. A browser visual check could not be completed because the Playwright browser executable was unavailable.

## 7. Problems Encountered and How I Solved Them

The following incident descriptions are from my original setup notes. Confirm and adjust their wording to match the actual events and fixes.

1. **PostgreSQL installer download failed:** My notes report error `0x80190193` / HTTP 403 while using winget to download PostgreSQL, followed by installing PostgreSQL 17 with the installer from postgresql.org. Confirm the final installed version.
2. **`psql` and `uv` were not recognized in PowerShell:** My notes say uv was installed with winget and VS Code was restarted. For `psql`, PostgreSQL was installed to a custom directory, noted as `D:\PortgreSQL\17\bin`; locating `psql.exe` and adding its directory to `PATH` resolved the command lookup. Confirm whether the PATH change was session-only or permanent.
3. **Typo in `uv init`:** My notes report typing `uv innit`, so initialization and package setup did not run and Python reported a missing pandas module. Correcting the command and adding the project dependencies resolved the setup issue.
4. **PostgreSQL password configuration:** My original notes describe an authentication failure caused by leaving placeholder text in `DB_PASSWORD`, followed by setting the actual password in an environment variable. In a later recorded startup attempt, `DB_PASSWORD` was absent and Uvicorn stopped with `KeyError`. Verify the current environment variable and successful database connection before describing this issue as fully resolved.
5. **`{"detail":"Not Found"}` at the API root:** The API does not define a homepage route at `/`. Use `/docs` for FastAPI's interactive endpoint page once the server is running.
6. **“Cannot reach the API” in Streamlit:** The UI needs the API to be running at `http://127.0.0.1:8000`. Run the API and Streamlit in separate terminals. The recorded UI smoke test displayed this message because the API was unavailable.
7. **Git command and repository errors:** My notes mention omitting the space in `git add .` and running Git commands before initializing a repository. The project is now a Git repository, and the initial project commit is `afae379`. The `.gitignore` excludes the dataset and virtual environment; Python cache files are also ignored.

## 8. How to Run the Project

These commands assume the project dependencies are installed and PostgreSQL is running with a database named `music` containing the two tables.

1. Open a PowerShell terminal in the project root.
2. Set the database password for the current terminal session. Replace the placeholder locally; do not commit a real password:

   ```powershell
   $env:DB_PASSWORD = "<your PostgreSQL password>"
   ```

3. In Terminal 1, start the API:

   ```powershell
   uv run uvicorn main:app --app-dir ch5_api --reload
   ```

4. In Terminal 2, from the project root, start Streamlit:

   ```powershell
   uv run streamlit run ch6_ui/app.py
   ```

5. Open the API documentation at `http://127.0.0.1:8000/docs` and the UI at `http://localhost:8501`.

To load the data for a new or disposable database, run the loader from the project root:

```powershell
uv run python ch4_database/load_data.py
```

The loader prompts for the PostgreSQL password. **It drops and recreates the `tracks` and `listening_history` tables before loading. Back up existing data and confirm the target database before running it.**

## 9. Reflection and Possible Improvements

### Reflection

**Personalize this draft in your own words before submission:** This project helped me understand how a database, an API, and a user interface can be separated while still working together. The data loader's chunked approach is intended to handle a large listening-history file without reading the whole file into memory at once. I also learned to read startup errors carefully: a missing database environment variable can stop the API before any endpoint is available, which in turn causes the UI to report that it cannot reach the API. I still need to complete and record an end-to-end run against PostgreSQL.

### Possible improvements

- Load a larger portion of the listening-history dataset and measure the effect on load time and recommendation performance.
- Verify and tune indexes for the popular-track, user-history, and collaborative recommendation queries.
- Add audio-preview playback using the stored Spotify preview URL, subject to availability and applicable service terms.
- Add automated API tests for normal responses, empty results, and 404 cases.
- Add a reproducible deployment setup, such as Docker, after documenting database initialization and environment-variable handling.
