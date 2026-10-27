import os
from contextlib import asynccontextmanager

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

engine = create_engine(
    URL.create(
        "postgresql+psycopg2",
        username="postgres",
        password=os.environ["DB_PASSWORD"],
        host="localhost",
        port=5432,
        database="music",
    )
)

FEATURES = [
    "danceability", "energy", "loudness", "speechiness",
    "acousticness", "instrumentalness", "liveness", "valence", "tempo",
]
state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load audio features once and prepare normalized vectors for similarity.
    df = pd.read_sql(
        f"SELECT track_id, name, artist, {', '.join(FEATURES)} FROM tracks", engine
    )
    df = df.dropna(subset=FEATURES).reset_index(drop=True)
    X = df[FEATURES].to_numpy(dtype=float)
    X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-9)
    X = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-9)
    state["df"] = df
    state["X"] = X
    state["index"] = {tid: i for i, tid in enumerate(df["track_id"])}
    yield


app = FastAPI(title="Music Search & Recommendation API", lifespan=lifespan)

@app.get("/")
def root():
    return {"message": "Music API is running. See /docs for endpoints."}

def query(sql, **params):
    with engine.connect() as conn:
        return [dict(r) for r in conn.execute(text(sql), params).mappings()]


@app.get("/search")
def search(q: str = Query(..., min_length=1), limit: int = Query(20, le=100)):
    """Search tracks by name or artist (case-insensitive, partial match)."""
    return query(
        """SELECT track_id, name, artist, year, genre FROM tracks
           WHERE name ILIKE :q OR artist ILIKE :q
           ORDER BY name LIMIT :limit""",
        q=f"%{q}%", limit=limit,
    )


@app.get("/tracks/{track_id}")
def get_track(track_id: str):
    rows = query("SELECT * FROM tracks WHERE track_id = :t", t=track_id)
    if not rows:
        raise HTTPException(404, "Track not found")
    return rows[0]


@app.get("/popular")
def popular(limit: int = Query(20, le=100)):
    """Most-played tracks overall."""
    return query(
        """SELECT t.track_id, t.name, t.artist, SUM(h.playcount) AS total_plays
           FROM listening_history h JOIN tracks t USING (track_id)
           GROUP BY t.track_id, t.name, t.artist
           ORDER BY total_plays DESC LIMIT :limit""",
        limit=limit,
    )


@app.get("/recommend/similar/{track_id}")
def recommend_similar(track_id: str, limit: int = Query(10, le=50)):
    """Content-based: tracks with similar audio features."""
    idx = state["index"].get(track_id)
    if idx is None:
        raise HTTPException(404, "Track not found (or missing audio features)")
    sims = state["X"] @ state["X"][idx]
    order = np.argsort(-sims)
    results = []
    for i in order:
        if i == idx:
            continue
        row = state["df"].iloc[i]
        results.append({
            "track_id": row["track_id"],
            "name": row["name"],
            "artist": row["artist"],
            "similarity": round(float(sims[i]), 4),
        })
        if len(results) >= limit:
            break
    return results


@app.get("/recommend/user/{user_id}")
def recommend_for_user(user_id: str, limit: int = Query(10, le=50)):
    """Collaborative filtering: tracks played by users with similar taste."""
    exists = query(
        "SELECT 1 FROM listening_history WHERE user_id = :u LIMIT 1", u=user_id
    )
    if not exists:
        raise HTTPException(404, "User not found")
    return query(
        """WITH mine AS (
               SELECT track_id FROM listening_history WHERE user_id = :u
           ),
           peers AS (
               SELECT user_id, COUNT(*) AS overlap
               FROM listening_history
               WHERE track_id IN (SELECT track_id FROM mine) AND user_id <> :u
               GROUP BY user_id ORDER BY overlap DESC LIMIT 50
           )
           SELECT t.track_id, t.name, t.artist,
                  SUM(p.overlap * h.playcount) AS score
           FROM peers p
           JOIN listening_history h ON h.user_id = p.user_id
           JOIN tracks t ON t.track_id = h.track_id
           WHERE h.track_id NOT IN (SELECT track_id FROM mine)
           GROUP BY t.track_id, t.name, t.artist
           ORDER BY score DESC LIMIT :limit""",
        u=user_id, limit=limit,
    )


@app.get("/users/{user_id}/history")
def user_history(user_id: str, limit: int = Query(20, le=100)):
    return query(
        """SELECT t.track_id, t.name, t.artist, h.playcount
           FROM listening_history h JOIN tracks t USING (track_id)
           WHERE h.user_id = :u ORDER BY h.playcount DESC LIMIT :limit""",
        u=user_id, limit=limit,
    )