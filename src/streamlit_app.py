"""Streamlit UI for Playlist Chaos playlist organizer and recommendations."""

from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import random

import pandas as pd
import streamlit as st

try:
    from .recommender import load_songs, retrieve_and_rank
    from .logger import log_recommendation, log_feedback
except ImportError:
    from recommender import load_songs, retrieve_and_rank
    from logger import log_recommendation, log_feedback


DATA_PATH = "data/songs.json"
SCORING_MODES = ["balanced", "genre-first", "mood-first", "energy-focused"]


def _normalize_text(value: object) -> str:
    return str(value or "").strip()


def _to_rows(recommendations):
    rows = []
    for idx, rec in enumerate(recommendations, start=1):
        song, score, explanation = rec
        rows.append(
            {
                "Rank": idx,
                "Title": song.get("title", "Unknown"),
                "Artist": song.get("artist", "Unknown"),
                "Genre": song.get("genre", "Unknown"),
                "Mood": song.get("mood", "Unknown"),
                "Score": round(float(score), 2),
                "Why": explanation,
            }
        )
    return rows


def _init_session_state(default_songs):
    if "songs" not in st.session_state:
        st.session_state["songs"] = deepcopy(default_songs)

    if "history" not in st.session_state:
        st.session_state["history"] = []

    if "profile" not in st.session_state:
        st.session_state["profile"] = {
            "name": "Playlist Explorer",
            "favorite_genre": "pop",
            "hype_min_energy": 0.7,
            "chill_max_energy": 0.45,
            "include_mixed": True,
        }

    if "latest_recommendations" not in st.session_state:
        st.session_state["latest_recommendations"] = []

    if "latest_recommendation_event_id" not in st.session_state:
        st.session_state["latest_recommendation_event_id"] = None


def _classify_playlist(song, profile):
    favorite_genre = _normalize_text(profile.get("favorite_genre", "")).lower()
    hype_min = float(profile.get("hype_min_energy", 0.7))
    chill_max = float(profile.get("chill_max_energy", 0.45))

    title = _normalize_text(song.get("title", "")).lower()
    genre = _normalize_text(song.get("genre", "")).lower()
    tags = _normalize_text(song.get("mood_tags", "")).lower().replace("|", " ")
    energy = float(song.get("energy", 0.0))

    hype_keywords = {"party", "club", "adrenaline", "high-energy", "intense", "bold"}
    chill_keywords = {"chill", "calm", "peaceful", "serene", "lofi", "study", "acoustic"}
    token_source = f"{title} {genre} {tags}"

    if energy >= hype_min:
        return "Hype"
    if any(keyword in token_source for keyword in hype_keywords):
        return "Hype"
    if favorite_genre and genre == favorite_genre:
        return "Hype"
    if energy <= chill_max:
        return "Chill"
    if any(keyword in token_source for keyword in chill_keywords):
        return "Chill"
    return "Mixed"


def _build_playlists(songs, profile):
    playlists = {"Hype": [], "Chill": [], "Mixed": []}
    include_mixed = bool(profile.get("include_mixed", True))
    midpoint = (float(profile.get("hype_min_energy", 0.7)) + float(profile.get("chill_max_energy", 0.45))) / 2.0

    for song in songs:
        group = _classify_playlist(song, profile)
        if group == "Mixed" and not include_mixed:
            energy = float(song.get("energy", 0.0))
            group = "Hype" if energy >= midpoint else "Chill"
        playlists[group].append(song)

    return playlists


def _song_matches_query(song, query):
    q = _normalize_text(query).lower()
    if not q:
        return True

    searchable = " ".join(
        [
            _normalize_text(song.get("title", "")),
            _normalize_text(song.get("artist", "")),
            _normalize_text(song.get("genre", "")),
            _normalize_text(song.get("mood", "")),
            _normalize_text(song.get("mood_tags", "")).replace("|", " "),
        ]
    ).lower()
    return q in searchable


def _playlist_rows(songs, playlist_name):
    rows = []
    for song in songs:
        rows.append(
            {
                "Title": song.get("title", "Unknown"),
                "Artist": song.get("artist", "Unknown"),
                "Genre": song.get("genre", "Unknown"),
                "Mood": song.get("mood", "Unknown"),
                "Energy": round(float(song.get("energy", 0.0)), 2),
                "Playlist": playlist_name,
                "Tags": _normalize_text(song.get("mood_tags", "")).replace("|", ", "),
            }
        )
    return rows


def _compute_stats(playlists, songs):
    total = len(songs)
    hype_count = len(playlists.get("Hype", []))
    chill_count = len(playlists.get("Chill", []))
    mixed_count = len(playlists.get("Mixed", []))
    average_energy = sum(float(song.get("energy", 0.0)) for song in songs) / total if total else 0.0
    artist_counter = Counter(_normalize_text(song.get("artist", "Unknown")) for song in songs)
    top_artist = artist_counter.most_common(1)[0][0] if artist_counter else "Unknown"

    return {
        "total": total,
        "hype_count": hype_count,
        "chill_count": chill_count,
        "mixed_count": mixed_count,
        "hype_ratio": (hype_count / total) if total else 0.0,
        "average_energy": average_energy,
        "top_artist": top_artist,
    }


def _normalize_new_song(raw_song, next_id):
    title = _normalize_text(raw_song.get("title", "Untitled Song")) or "Untitled Song"
    artist = _normalize_text(raw_song.get("artist", "Unknown Artist")) or "Unknown Artist"
    genre = _normalize_text(raw_song.get("genre", "Unknown")) or "Unknown"
    mood = _normalize_text(raw_song.get("mood", "custom")) or "custom"
    tags = _normalize_text(raw_song.get("mood_tags", ""))
    tags = "|".join([tag.strip().lower() for tag in tags.replace("|", ",").split(",") if tag.strip()])

    return {
        "id": int(next_id),
        "title": title,
        "artist": artist,
        "genre": genre,
        "mood": mood,
        "energy": float(raw_song.get("energy", 0.5)),
        "tempo_bpm": float(raw_song.get("tempo_bpm", 100.0)),
        "valence": float(raw_song.get("valence", 0.5)),
        "danceability": float(raw_song.get("danceability", 0.5)),
        "acousticness": float(raw_song.get("acousticness", 0.5)),
        "popularity_0_100": int(raw_song.get("popularity_0_100", 50)),
        "release_decade": int(raw_song.get("release_decade", 2020)),
        "mood_tags": tags,
        "instrumentalness": float(raw_song.get("instrumentalness", 0.0)),
        "lyrical_density": float(raw_song.get("lyrical_density", 0.5)),
        "explicitness": float(raw_song.get("explicitness", 0.0)),
    }


def _choose_lucky_pool(playlists, songs, pool_name):
    if pool_name == "Hype":
        return playlists.get("Hype", [])
    if pool_name == "Chill":
        return playlists.get("Chill", [])
    if pool_name == "Mixed":
        return playlists.get("Mixed", [])
    return songs


def main() -> None:
    st.set_page_config(page_title="Playlist Chaos", page_icon="🎵", layout="wide")
    st.title("Playlist Chaos")
    st.caption("AI-assisted music recommendation and playlist organizer.")

    default_songs = load_songs(DATA_PATH)
    _init_session_state(default_songs)

    songs = st.session_state["songs"]
    history = st.session_state["history"]
    profile = st.session_state["profile"]

    all_genres = sorted({_normalize_text(song.get("genre", "")).lower() for song in songs if song.get("genre")})
    all_moods = sorted({_normalize_text(song.get("mood", "")).lower() for song in songs if song.get("mood")})
    if not all_genres:
        all_genres = ["pop"]
    if not all_moods:
        all_moods = ["euphoric"]

    st.sidebar.header("Profile")
    profile_name = st.sidebar.text_input("Profile Name", value=_normalize_text(profile.get("name", "Playlist Explorer")))
    favorite_genre = st.sidebar.text_input(
        "Favorite Genre",
        value=_normalize_text(profile.get("favorite_genre", "pop")),
        help="Used by playlist classification to personalize Hype grouping.",
    )
    hype_min_energy = st.sidebar.slider(
        "Hype Min Energy",
        min_value=0.0,
        max_value=1.0,
        value=float(profile.get("hype_min_energy", 0.7)),
        step=0.01,
    )
    chill_max_energy = st.sidebar.slider(
        "Chill Max Energy",
        min_value=0.0,
        max_value=1.0,
        value=float(profile.get("chill_max_energy", 0.45)),
        step=0.01,
    )
    include_mixed = st.sidebar.checkbox(
        "Show Mixed Playlist",
        value=bool(profile.get("include_mixed", True)),
    )

    st.session_state["profile"] = {
        "name": profile_name,
        "favorite_genre": favorite_genre,
        "hype_min_energy": hype_min_energy,
        "chill_max_energy": chill_max_energy,
        "include_mixed": include_mixed,
    }
    profile = st.session_state["profile"]

    st.sidebar.divider()
    st.sidebar.subheader("State Controls")
    if st.sidebar.button("Reset Song Library"):
        st.session_state["songs"] = deepcopy(default_songs)
        st.success("Song library reset to default data.")
        st.rerun()
    if st.sidebar.button("Clear Pick History"):
        st.session_state["history"] = []
        st.success("Pick history cleared.")
        st.rerun()

    st.subheader("Add Song")
    with st.form("add_song_form"):
        col1, col2 = st.columns(2)
        title = col1.text_input("Title")
        artist = col2.text_input("Artist")
        genre = col1.text_input("Genre")
        mood = col2.text_input("Mood", value="custom")
        energy = col1.slider("Energy", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
        mood_tags = col2.text_input("Tags (comma-separated)")
        submitted = st.form_submit_button("Add Song")

        if submitted:
            existing_ids = [int(song.get("id", 0)) for song in st.session_state["songs"]]
            next_id = max(existing_ids, default=0) + 1
            normalized_song = _normalize_new_song(
                {
                    "title": title,
                    "artist": artist,
                    "genre": genre,
                    "mood": mood,
                    "energy": energy,
                    "mood_tags": mood_tags,
                },
                next_id,
            )
            st.session_state["songs"].append(normalized_song)
            st.success(f"Added '{normalized_song['title']}' by {normalized_song['artist']}.")
            st.rerun()

    songs = st.session_state["songs"]
    playlists = _build_playlists(songs, profile)

    st.subheader("Playlist Browser")
    search_query = st.text_input("Search playlists", placeholder="Filter by title, artist, genre, mood, or tags")

    tab_names = ["Hype", "Chill"]
    if include_mixed:
        tab_names.append("Mixed")

    tabs = st.tabs(tab_names)
    for idx, tab_name in enumerate(tab_names):
        with tabs[idx]:
            filtered = [song for song in playlists.get(tab_name, []) if _song_matches_query(song, search_query)]
            st.caption(f"{len(filtered)} songs shown")
            rows = _playlist_rows(filtered, tab_name)
            if rows:
                st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
            else:
                st.info("No songs match this filter.")

    st.subheader("Feeling Lucky")
    lucky_pool_options = ["Any"] + tab_names
    lucky_pool_name = st.selectbox("Lucky pick pool", lucky_pool_options, index=0)
    lucky_pool = _choose_lucky_pool(playlists, songs, lucky_pool_name)

    if st.button("Pick Random Song"):
        if not lucky_pool:
            st.warning("No songs available in this pool. Try another playlist.")
        else:
            lucky_song = random.choice(lucky_pool)
            lucky_playlist = _classify_playlist(lucky_song, profile)
            st.session_state["history"].append(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "title": lucky_song.get("title", "Unknown"),
                    "artist": lucky_song.get("artist", "Unknown"),
                    "genre": lucky_song.get("genre", "Unknown"),
                    "energy": float(lucky_song.get("energy", 0.0)),
                    "playlist": lucky_playlist,
                }
            )
            st.success("Here is your lucky pick!")
            st.write(f"**{lucky_song.get('title', 'Unknown')}** by **{lucky_song.get('artist', 'Unknown')}**")
            st.caption(
                f"Playlist: {lucky_playlist} | Genre: {lucky_song.get('genre', 'Unknown')} | "
                f"Mood: {lucky_song.get('mood', 'Unknown')} | Energy: {float(lucky_song.get('energy', 0.0)):.2f}"
            )

    st.subheader("Playlist Statistics")
    stats = _compute_stats(playlists, songs)
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Total Songs", stats["total"])
    col_b.metric("Hype Count", stats["hype_count"])
    col_c.metric("Chill Count", stats["chill_count"])
    col_d.metric("Mixed Count", stats["mixed_count"])

    col_e, col_f, col_g = st.columns(3)
    col_e.metric("Hype Ratio", f"{stats['hype_ratio']:.1%}")
    col_f.metric("Average Energy", f"{stats['average_energy']:.2f}")
    col_g.metric("Top Artist", stats["top_artist"])

    st.subheader("Listening History")
    if history:
        history_df = pd.DataFrame(history[::-1])
        st.dataframe(history_df, width="stretch", hide_index=True)
        mood_counts = Counter(item.get("playlist", "Unknown") for item in history)
        st.caption(
            "Recent picks by playlist: "
            + ", ".join([f"{key}={value}" for key, value in mood_counts.items()])
        )
    else:
        st.info("No lucky picks yet. Use Feeling Lucky to start building history.")

    st.subheader("Recommendations")
    rec_genre = st.selectbox("Recommendation Genre", all_genres, index=0)
    rec_mood = st.selectbox("Recommendation Mood", all_moods, index=0)
    rec_energy = st.slider("Recommendation Target Energy", min_value=0.0, max_value=1.0, value=0.75, step=0.01)
    top_k = st.slider("Recommendations Count", min_value=1, max_value=10, value=5)
    scoring_mode = st.selectbox("Scoring Mode", SCORING_MODES, index=0)
    mood_tags_text = st.text_input("Preferred Mood Tags (comma-separated)", value="party,bold")
    preferred_tags = [tag.strip() for tag in mood_tags_text.split(",") if tag.strip()]

    user_prefs = {
        "genre": rec_genre,
        "mood": rec_mood,
        "energy": float(rec_energy),
        "preferred_mood_tags": preferred_tags,
        "scoring_mode": scoring_mode,
    }

    if st.button("Get Recommendations", type="primary"):
        retrieved, recommendations = retrieve_and_rank(
            user_prefs=user_prefs,
            songs=songs,
            k=top_k,
            mode=scoring_mode,
            retrieve_k=min(len(songs), max(top_k * 2, 8)),
        )
        recommendation_event_id = log_recommendation(
            user_prefs=user_prefs,
            query="streamlit-ui",
            retrieved=retrieved,
            final_recommendations=recommendations,
            mode=scoring_mode,
            confidence="medium",
        )
        st.session_state["latest_recommendations"] = recommendations
        st.session_state["latest_recommendation_event_id"] = recommendation_event_id
        st.write(f"Retrieved **{len(retrieved)}** candidates from **{len(songs)}** songs.")
        rows = _to_rows(recommendations)
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
        with st.expander("Show Request Payload"):
            st.json(user_prefs)

    if st.session_state.get("latest_recommendations") and st.session_state.get("latest_recommendation_event_id"):
        st.subheader("Recommendation Feedback")
        st.caption("Mark each recommendation as liked or skipped to improve future learned weights.")

        recommendation_event_id = st.session_state["latest_recommendation_event_id"]
        for idx, rec in enumerate(st.session_state["latest_recommendations"], start=1):
            song, score, _ = rec
            song_id = song.get("id")
            title = song.get("title", "Unknown")
            artist = song.get("artist", "Unknown")
            score_text = f"{float(score):.2f}"

            col_info, col_like, col_skip = st.columns([6, 1, 1])
            col_info.write(f"{idx}. **{title}** by **{artist}** (score: {score_text})")

            like_clicked = col_like.button("Like", key=f"like_{recommendation_event_id}_{song_id}_{idx}")
            skip_clicked = col_skip.button("Skip", key=f"skip_{recommendation_event_id}_{song_id}_{idx}")

            if like_clicked:
                log_feedback(
                    recommendation_event_id=recommendation_event_id,
                    song_id=song_id,
                    feedback="liked",
                    rank=idx,
                    score=float(score),
                    metadata={"source": "streamlit"},
                )
                st.success(f"Feedback saved: liked '{title}'.")

            if skip_clicked:
                log_feedback(
                    recommendation_event_id=recommendation_event_id,
                    song_id=song_id,
                    feedback="skipped",
                    rank=idx,
                    score=float(score),
                    metadata={"source": "streamlit"},
                )
                st.success(f"Feedback saved: skipped '{title}'.")


if __name__ == "__main__":
    main()
