DROP TABLE IF EXISTS listening_history;
DROP TABLE IF EXISTS tracks;

CREATE TABLE tracks (
    track_id          TEXT PRIMARY KEY,
    name              TEXT,
    artist            TEXT,
    spotify_preview_url TEXT,
    spotify_id        TEXT,
    tags              TEXT,
    genre             TEXT,
    year              INTEGER,
    duration_ms       INTEGER,
    danceability      DOUBLE PRECISION,
    energy            DOUBLE PRECISION,
    key               INTEGER,
    loudness          DOUBLE PRECISION,
    mode              INTEGER,
    speechiness       DOUBLE PRECISION,
    acousticness      DOUBLE PRECISION,
    instrumentalness  DOUBLE PRECISION,
    liveness          DOUBLE PRECISION,
    valence           DOUBLE PRECISION,
    tempo             DOUBLE PRECISION,
    time_signature    INTEGER
);

CREATE TABLE listening_history (
    track_id  TEXT,
    user_id   TEXT,
    playcount INTEGER
);