"""Streamlit UI for MoodMatch recommendations."""

import streamlit as st
import pandas as pd

try:
    from .recommender import load_songs, retrieve_and_rank
except ImportError:
    from recommender import load_songs, retrieve_and_rank


DATA_PATH = "data/songs.json"


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


def main() -> None:
    st.set_page_config(page_title="MoodMatch", page_icon="🎵", layout="wide")
    st.title("MoodMatch")
    st.caption("RAG-based music recommendations with transparent scoring.")

    songs = load_songs(DATA_PATH)

    genres = sorted({str(song.get("genre", "")).strip() for song in songs if song.get("genre")})
    moods = sorted({str(song.get("mood", "")).strip() for song in songs if song.get("mood")})

    st.sidebar.header("Your Preferences")
    genre = st.sidebar.selectbox("Genre", genres, index=genres.index("pop") if "pop" in genres else 0)
    mood = st.sidebar.selectbox("Mood", moods, index=moods.index("euphoric") if "euphoric" in moods else 0)
    energy = st.sidebar.slider("Target Energy", min_value=0.0, max_value=1.0, value=0.75, step=0.01)
    top_k = st.sidebar.slider("Recommendations", min_value=1, max_value=10, value=5)

    scoring_mode = st.sidebar.selectbox(
        "Scoring Mode",
        ["balanced", "genre-first", "mood-first", "energy-focused"],
        index=0,
    )

    mood_tags_text = st.sidebar.text_input(
        "Preferred Mood Tags (comma-separated)",
        value="party,bold",
    )
    preferred_tags = [tag.strip() for tag in mood_tags_text.split(",") if tag.strip()]

    user_prefs = {
        "genre": genre,
        "mood": mood,
        "energy": float(energy),
        "preferred_mood_tags": preferred_tags,
        "scoring_mode": scoring_mode,
    }

    if st.sidebar.button("Get Recommendations", type="primary"):
        retrieved, recommendations = retrieve_and_rank(
            user_prefs=user_prefs,
            songs=songs,
            k=top_k,
            mode=scoring_mode,
            retrieve_k=min(len(songs), max(top_k * 2, 8)),
        )

        st.subheader("Results")
        st.write(f"Retrieved **{len(retrieved)}** candidates from **{len(songs)}** songs.")

        rows = _to_rows(recommendations)
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        with st.expander("Show Request Payload"):
            st.json(user_prefs)
    else:
        st.info("Set your preferences in the sidebar and click Get Recommendations.")


if __name__ == "__main__":
    main()
