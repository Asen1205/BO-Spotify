import io
from getpass import getpass
from pathlib import Path

import pandas as pd
import psycopg2

ROOT = Path(__file__).resolve().parent.parent
MUSIC_CSV = ROOT / "data" / "Music Info.csv"
HISTORY_CSV = ROOT / "data" / "User Listening History.csv"
SCHEMA = Path(__file__).resolve().parent / "schema.sql"

MAX_HISTORY_ROWS = 2_000_000   # raise later once everything works
CHUNK = 200_000

TRACK_COLS = [
    "track_id", "name", "artist", "spotify_preview_url", "spotify_id",
    "tags", "genre", "year", "duration_ms", "danceability", "energy",
    "key", "loudness", "mode", "speechiness", "acousticness",
    "instrumentalness", "liveness", "valence", "tempo", "time_signature",
]
HISTORY_COLS = ["track_id", "user_id", "playcount"]


def copy_df(cur, df, table, cols):
    buf = io.StringIO()
    df[cols].to_csv(buf, index=False, header=False)
    buf.seek(0)
    cur.copy_expert(
        f"COPY {table} ({', '.join(cols)}) FROM STDIN WITH (FORMAT csv)", buf
    )


def check_columns(actual, expected, name):
    missing = [c for c in expected if c not in actual]
    if missing:
        raise SystemExit(
            f"{name}: missing columns {missing}\nActual columns: {list(actual)}"
        )


def main():
    password = getpass("PostgreSQL password: ")
    conn = psycopg2.connect(
        dbname="music", user="postgres", password=password,
        host="localhost", port=5432,
    )
    cur = conn.cursor()

    cur.execute(SCHEMA.read_text(encoding="utf-8"))

    # --- tracks ---
    tracks = pd.read_csv(MUSIC_CSV)
    check_columns(tracks.columns, TRACK_COLS, "Music Info.csv")
    tracks = tracks.drop_duplicates(subset="track_id")
    for c in ["year", "duration_ms", "key", "mode", "time_signature"]:
        tracks[c] = tracks[c].astype("Int64")
    copy_df(cur, tracks, "tracks", TRACK_COLS)
    conn.commit()
    print(f"tracks loaded: {len(tracks)}")
    valid_ids = set(tracks["track_id"])

    # --- listening history (chunked) ---
    total = 0
    first = True
    for chunk in pd.read_csv(HISTORY_CSV, chunksize=CHUNK):
        if first:
            check_columns(chunk.columns, HISTORY_COLS, "User Listening History.csv")
            first = False
        chunk = chunk[chunk["track_id"].isin(valid_ids)]
        chunk = chunk.dropna(subset=HISTORY_COLS)
        copy_df(cur, chunk, "listening_history", HISTORY_COLS)
        conn.commit()
        total += len(chunk)
        print(f"history rows loaded: {total}")
        if total >= MAX_HISTORY_ROWS:
            break

    cur.execute("CREATE INDEX idx_hist_user ON listening_history (user_id);")
    cur.execute("CREATE INDEX idx_hist_track ON listening_history (track_id);")
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM tracks;")
    print("tracks in DB:", cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) FROM listening_history;")
    print("history rows in DB:", cur.fetchone()[0])
    conn.close()


if __name__ == "__main__":
    main()