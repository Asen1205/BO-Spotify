import html
import re
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

API = "http://127.0.0.1:8000"
EXAMPLE_USER = "4e11f45d732f4861772b2906f81a7d384552ad12"
MP3_DIR = Path(__file__).resolve().parent.parent / "data" / "MP3-Example"
ID_RE = re.compile(r"TR[A-Z0-9]{16}")

st.set_page_config(
    page_title="Soundwave | Music discovery",
    page_icon="♫",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

    :root {
        --canvas: #090b0a;
        --panel: #121513;
        --panel-raised: #1b201d;
        --text: #f5f7f5;
        --muted: #a7b0aa;
        --green: #1ed760;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    .stApp {
        background:
            radial-gradient(ellipse at 78% 0%, rgba(30, 215, 96, .12), transparent 34%),
            var(--canvas);
        color: var(--text);
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] {
        background: #050706;
        border-right: 1px solid rgba(255,255,255,.07);
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }
    [data-testid="stMain"] .block-container {
        max-width: 1440px;
        padding: 2rem 3.5rem 4rem;
    }
    h1, h2, h3 { color: var(--text); letter-spacing: -.035em; }
    p, label, [data-testid="stMarkdownContainer"] { color: var(--text); }
    [data-testid="stCaptionContainer"] { color: var(--muted); }

    .brand {
        display: flex;
        align-items: center;
        gap: 11px;
        padding: 0 0 1.5rem;
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: -.04em;
    }
    .brand-mark {
        width: 35px;
        height: 35px;
        display: grid;
        place-items: center;
        border-radius: 50%;
        background: var(--green);
        color: #071109;
        font-size: 1.35rem;
    }
    .side-label {
        color: #87918a;
        text-transform: uppercase;
        letter-spacing: .12em;
        font-size: .68rem;
        font-weight: 700;
        margin: .4rem 0 .7rem;
    }
    .side-link {
        color: #c4cbc6;
        padding: .5rem 0;
        font-weight: 600;
        font-size: .9rem;
    }
    .side-note {
        color: #909a93;
        font-size: .82rem;
        line-height: 1.55;
        background: #111512;
        border: 1px solid rgba(255,255,255,.06);
        border-radius: 12px;
        padding: 14px;
        margin-top: 1.4rem;
    }
    .hero {
        position: relative;
        overflow: hidden;
        padding: 2.4rem 2.5rem;
        margin: .2rem 0 1.6rem;
        min-height: 210px;
        border-radius: 18px;
        background: linear-gradient(112deg, #173b27 0%, #176338 48%, #10271a 100%);
        box-shadow: 0 20px 60px rgba(0,0,0,.2);
    }
    .hero:after {
        content: '♫';
        position: absolute;
        right: 6%;
        top: -70px;
        color: rgba(255,255,255,.08);
        font-size: 19rem;
        line-height: 1;
        transform: rotate(12deg);
    }
    .eyebrow {
        color: #b7efc9;
        font-size: .72rem;
        text-transform: uppercase;
        letter-spacing: .16em;
        font-weight: 700;
    }
    .hero h1 {
        margin: .55rem 0;
        color: white;
        font-size: clamp(2rem, 4vw, 3.4rem);
        line-height: 1.05;
        font-weight: 800;
    }
    .hero p {
        margin: .6rem 0 0;
        color: #d3e6d9;
        font-size: 1rem;
    }
    [data-testid="stTabs"] [role="tablist"] {
        gap: 8px;
        border-bottom: 1px solid rgba(255,255,255,.09);
    }
    [data-testid="stTabs"] button[role="tab"] {
        color: #aab3ad;
        border-radius: 999px;
        padding: .65rem 1.15rem;
        font-weight: 700;
    }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background: #202722;
        color: white;
    }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] p {
        color: white;
    }
    [data-testid="stTextInput"] input {
        background: #202522;
        border: 1px solid transparent;
        border-radius: 999px;
        color: white;
        min-height: 48px;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: var(--green);
        box-shadow: 0 0 0 1px var(--green);
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    [data-testid="stNumberInput"] input {
        background: #202522;
        color: white;
        border-color: rgba(255,255,255,.08);
        border-radius: 10px;
    }
    [data-testid="stSlider"] [role="slider"] {
        background: var(--green);
        border-color: var(--green);
    }
    .stButton > button {
        background: var(--green);
        color: #071109;
        border: 0;
        border-radius: 999px;
        min-height: 44px;
        padding: 0 1.4rem;
        font-weight: 800;
        transition: transform .15s ease, background .15s ease;
    }
    .stButton > button:hover {
        background: #42e477;
        color: #071109;
        transform: scale(1.03);
    }
    .section-heading {
        margin: 1.5rem 0 .25rem;
        font-size: 1.35rem;
        font-weight: 800;
    }
    .section-subtitle {
        color: var(--muted);
        margin: 0 0 1rem;
        font-size: .9rem;
    }
    .track-card {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 12px 15px;
        margin: 8px 0;
        min-height: 72px;
        border: 1px solid rgba(255,255,255,.045);
        border-radius: 12px;
        background: rgba(23,27,24,.88);
        transition: background .15s ease, transform .15s ease;
    }
    .track-card:hover {
        background: #252c27;
        transform: translateY(-1px);
    }
    .album-art {
        flex: 0 0 46px;
        width: 46px;
        height: 46px;
        display: grid;
        place-items: center;
        border-radius: 7px;
        color: #071109;
        font-size: 1.35rem;
        font-weight: 800;
        background: linear-gradient(145deg, #56e88a, #148443);
    }
    .track-copy { min-width: 0; flex: 1; }
    .track-name {
        color: #f6f8f6;
        font-size: .93rem;
        font-weight: 700;
        overflow-wrap: anywhere;
    }
    .track-artist {
        color: #a5aea8;
        font-size: .8rem;
        margin-top: 3px;
        overflow-wrap: anywhere;
    }
    .track-meta {
        color: #b5c0b8;
        font-size: .78rem;
        text-align: right;
        white-space: nowrap;
    }
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 12px;
        overflow: hidden;
    }
    [data-testid="stAlert"] { border-radius: 12px; }
    @media (max-width: 800px) {
        [data-testid="stMain"] .block-container { padding: 1.2rem 1rem 3rem; }
        .hero { padding: 1.7rem 1.4rem; }
        .hero:after { right: -14%; font-size: 14rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(
        '<div class="brand"><span class="brand-mark">♫</span> soundwave</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="side-label">Your space</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-link">⌕ &nbsp; Discover music</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-link">♫ &nbsp; Your listening trends</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="side-note">
            <strong>Made for music fans</strong><br>
            Search the catalog, explore popular tracks, and find your next favorite.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Your next favorite is waiting</div>
        <h1>Find your sound.</h1>
        <p>Search the catalog, follow the listening trends, and discover something new.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


def call(path, **params):
    """GET from the API. Returns JSON, or None if the item was not found."""
    try:
        response = requests.get(f"{API}{path}", params=params, timeout=60)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the API. Is uvicorn running on port 8000?")
        st.stop()
    except requests.RequestException as error:
        st.error(f"API error: {error}")
        st.stop()


def lookup_tracks(track_ids):
    try:
        response = requests.post(
            f"{API}/tracks/lookup",
            json=track_ids,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the API. Is uvicorn running on port 8000?")
        st.stop()
    except requests.RequestException as error:
        st.error(f"API error: {error}")
        st.stop()


@st.cache_data
def mp3_index():
    """Map track IDs to sample paths based on the names of MP3 files."""
    index = {}
    for path in MP3_DIR.rglob("*.mp3"):
        match = ID_RE.search(path.stem)
        if match:
            index[match.group(0)] = str(path)
    return index


def play(track_id):
    if track_id not in mp3_index():
        st.caption("No audio sample for this track.")
        return
    audio = audio_sample(track_id)
    if audio is not None:
        st.audio(audio, format="audio/mpeg")


@st.cache_data
def audio_sample(track_id):
    """Fetch an MP3 sample from the API, or return None when it is unavailable."""
    try:
        response = requests.get(f"{API}/tracks/{track_id}/audio", timeout=60)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.content
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the API. Is uvicorn running on port 8000?")
        st.stop()
    except requests.RequestException as error:
        st.error(f"Audio playback error: {error}")
        st.stop()


def show_tracks(rows, metric=None):
    for row in rows:
        title = html.escape(str(row.get("name") or "Unknown track"))
        artist = html.escape(str(row.get("artist") or "Unknown artist"))
        details = []
        for field in ("year", "genre"):
            value = row.get(field)
            if pd.notna(value) and value != "":
                details.append(html.escape(str(value)))
        subtitle = " · ".join([artist, *details])
        metric_html = ""
        if metric and row.get(metric) is not None:
            value = row[metric]
            if metric == "similarity":
                value = f"{float(value):.0%} match"
            elif metric in ("total_plays", "playcount"):
                value = f"{int(value):,} plays"
            else:
                value = f"Score {float(value):,.0f}"
            metric_html = f'<div class="track-meta">{html.escape(str(value))}</div>'
        st.markdown(
            f"""
            <div class="track-card">
                <div class="album-art">♫</div>
                <div class="track-copy">
                    <div class="track-name">{title}</div>
                    <div class="track-artist">{subtitle}</div>
                </div>
                {metric_html}
            </div>
            """,
            unsafe_allow_html=True,
        )


def show_tracks_with_audio(rows, metric=None):
    show_tracks(rows, metric=metric)
    files = mp3_index()
    playable = [row for row in rows if row.get("track_id") in files]
    if playable:
        st.markdown("**🎧 Tracks with audio samples**")
        for row in playable:
            st.write(f"{row['name']} — {row['artist']}")
            play(row["track_id"])


tab_search, tab_popular, tab_user, tab_audio = st.tabs(
    ["⌕  Discover", "♫  Popular tracks", "✦  For a listener", "🎧  Audio samples"]
)

with tab_search:
    st.markdown('<div class="section-heading">Search the catalog</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Find a track or artist, then explore songs with a similar sound.</div>',
        unsafe_allow_html=True,
    )
    q = st.text_input(
        "Search by song or artist",
        placeholder="Try a song title or artist name",
        label_visibility="collapsed",
    )
    if q:
        results = call("/search", q=q, limit=30)
        if not results:
            st.warning("No songs found. Try a different title or artist.")
        else:
            st.markdown(f'<div class="section-heading">{len(results)} tracks found</div>', unsafe_allow_html=True)
            show_tracks_with_audio(results)

            labels = {
                f"{row['name']} — {row['artist']}": row["track_id"]
                for row in results
            }
            choice = st.selectbox("Choose a track for similar recommendations", list(labels))
            play(labels[choice])
            n = st.slider("Recommendations", 5, 30, 10, key="n_similar")
            if st.button("Find similar tracks"):
                recs = call(f"/recommend/similar/{labels[choice]}", limit=n)
                if recs is None:
                    st.warning("This track has no audio features, so it can't be compared.")
                elif recs:
                    st.markdown(
                        f'<div class="section-heading">Because you picked {html.escape(choice)}</div>',
                        unsafe_allow_html=True,
                    )
                    show_tracks_with_audio(recs, metric="similarity")
                else:
                    st.info("No similar tracks were found.")

with tab_popular:
    st.markdown('<div class="section-heading">Popular right now</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">The most-played tracks across listener history.</div>',
        unsafe_allow_html=True,
    )
    n = st.slider("Tracks to show", 5, 50, 20, key="n_popular")
    popular = call("/popular", limit=n)
    if popular:
        chart_data = pd.DataFrame(popular)
        chart_data["label"] = chart_data["name"] + " — " + chart_data["artist"]
        st.bar_chart(chart_data.set_index("label")["total_plays"], color="#1ed760")
        show_tracks_with_audio(popular, metric="total_plays")
    else:
        st.info("No listening history is available yet.")

with tab_user:
    st.markdown('<div class="section-heading">A mix made for you</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Enter a listener ID to see their favorites and discover similar artists.</div>',
        unsafe_allow_html=True,
    )
    user_id = st.text_input("User ID", value=EXAMPLE_USER)
    n = st.slider("Recommendations", 5, 30, 10, key="n_user")
    if st.button("Build my mix"):
        history = call(f"/users/{user_id}/history", limit=10)
        if not history:
            st.warning("No listening history found for that user ID.")
        else:
            st.markdown('<div class="section-heading">On repeat</div>', unsafe_allow_html=True)
            show_tracks_with_audio(history, metric="playcount")
            with st.spinner("Finding listeners with a similar taste..."):
                recs = call(f"/recommend/user/{user_id}", limit=n)
            if recs:
                st.markdown('<div class="section-heading">Picked for you</div>', unsafe_allow_html=True)
                show_tracks_with_audio(recs, metric="score")
            else:
                st.info("We couldn't find recommendations for this listener yet.")

with tab_audio:
    files = mp3_index()
    if not files:
        st.warning(f"No MP3 files found in {MP3_DIR}")
    else:
        genres = sorted(path.name for path in MP3_DIR.iterdir() if path.is_dir())
        if not genres:
            st.warning(f"No genre folders found in {MP3_DIR}")
        else:
            genre = st.selectbox("Genre folder", genres)
            ids = sorted(
                track_id
                for track_id, path in files.items()
                if Path(path).parent.name == genre
            )
            st.caption(f"{len(ids)} audio samples in {genre}")
            count = st.slider("How many to show", 1, 20, 5, key="n_audio")
            tracks = lookup_tracks(ids[:200])
            info = {track["track_id"]: track for track in tracks}
            displayed = 0
            for track_id in ids[:200]:
                track = info.get(track_id)
                if track is not None and displayed < count:
                    st.write(f"**{track['name']}** — {track['artist']}")
                    play(track_id)
                    displayed += 1
