# 🎵 Playlist Chaos: AI-Assisted Music Recommendation and Playlist Organizer

## Project Summary

This project implements a **Streamlit-based playlist organizer** that helps users explore a music library, classify songs into mood-based playlists, and get lightweight recommendation behavior from profile settings and song attributes.

The system helps users discover songs that match their mood, genre preferences, and energy levels. Instead of treating recommendations as a black box, it:

1. **Classifies** songs into Hype, Chill, or Mixed playlists using profile thresholds and song metadata
2. **Searches** playlist views so users can filter songs by title, artist, mood, genre, or tags
3. **Adds** new songs through a normalized input form inside the app
4. **Recommends** songs with lightweight profile-aware scoring and random lucky-pick behavior
5. **Tracks** pick history and playlist statistics for visibility and reuse

This design follows a pragmatic playlist-first workflow: playlist classification happens first, then search, random selection, and recommendation logic use that organized library.

---

## How The System Works

### Data Model
Each song has metadata including:
- **Title, Artist, Genre, Mood** — categorical attributes
- **Energy, Danceability, Acousticness** — numeric 0-1 scales
- **Tempo, Valence, Popularity, Decade** — additional context
- **Mood Tags** (pipe-separated) — fine-grained emotional tags
- **Instrumentalness, Lyrical Density, Explicitness** — content features

### Playlist Flow

**1. Profile Setup**
- Set a profile name, favorite genre, Hype minimum energy, Chill maximum energy, and whether to show Mixed

**2. Library Expansion**
- Add new songs with title, artist, genre, mood, energy, and tags
- Normalize user input before storing it in session state

**3. Playlist Classification**
- Assign songs to Hype, Chill, or Mixed based on the current profile and metadata

**4. Playlist Browsing**
- Show playlist tabs with search filtering for quick lookup

**5. Lucky Picks and History**
- Pick random songs from any playlist and keep a local history of picks

**6. Statistics**
- Summarize total songs, playlist counts, hype ratio, average energy, and top artist

### Recommendation Flow

**1. Retrieval Stage**
- Parse user profile into structured hints (genre, mood, energy, tags)
- Filter song library by metadata matching (genre +2.0, mood +1.5, energy +1.0, tags +0.5 each)
- Return top-k candidates (default k=8)

**2. Ranking Stage**
- Score retrieved candidates using weighted attributes
- Apply diversity penalty to avoid repeating artists/genres
- Return top-k final recommendations (default k=5)

**3. Explanation Stage**
- Break down the score component-by-component
- Show retrieval evidence (which metadata drove the match)

**4. Logging Stage**
- Log every recommendation event to `recommendations.jsonl`

### Key Design Decisions

- **Session-state driven**: Playlist edits, history, and reset behavior live in the Streamlit session
- **User-controlled personalization**: Profile thresholds directly affect playlist grouping
- **Normalized input**: Added songs are cleaned before entering the library
- **Searchable playlists**: Users can filter by song metadata while browsing
- **Inspectable behavior**: Lucky picks, history, and stats make the app easy to explore

---

## Evaluation Results

### Retrieval Quality (5 benchmark queries)

| Metric | Score |
|--------|-------|
| **Genre Recall@5** | 100% |
| **Mood Recall@5** | 90% |
| **Groundedness** | 100% |

**Interpretation**: High recall means we find relevant songs. 100% groundedness means all explanations mention real metadata.

---

## Getting Started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate      # Mac/Linux
.venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

### Run

```bash
# Show RAG recommendations
python -m src.main

# Run evaluation suite
python src/evaluation.py
```

---

## Architecture

```
src/
├── main.py               # CLI runner
├── recommender.py        # Core logic + RAG functions
├── retrieval.py         # Metadata filtering & scoring
├── logger.py            # JSONL audit logging
└── evaluation.py        # Benchmarks & metrics
data/
└── songs.csv            # 10-song dataset
```

### Core Functions

**recommender.py:**
```python
def retrieve_and_rank(user_prefs, songs, k=5, mode=None, retrieve_k=15)
    # Retrieve → rank → return (candidates, final_recs)

def explain_retrieval_evidence(user_prefs, song)
    # Show which metadata drove retrieval
```

**retrieval.py:**
```python
def retrieve_candidates(user_prefs, songs, k=10)
    # Returns top-k songs with retrieval scores
```

**logger.py:**
```python
def log_recommendation(user_prefs, query, retrieved, final_recommendations, ...)
    # Log event to recommendations.jsonl
```

---

## Responsible AI Features

- **Transparency**: Users can see how songs are grouped, filtered, and picked
- **Guardrails**: Normalization reduces inconsistent user input
- **Logging**: Full audit trail with timestamps, preferences, retrieved songs, recommendations
- **Accountability**: JSONL format for easy parsing and analysis

---

## Testing

```bash
pytest tests/test_recommender.py -v
cd src && python evaluation.py
```

---

## Summary

Playlist Chaos upgrades the assignment recommender into a **hands-on playlist organizer** by:
- Adding playlist classification for Hype, Chill, and Mixed views
- Letting users add and normalize songs directly in the UI
- Providing searchable playlist tabs and random lucky-pick behavior
- Keeping local history and playlist statistics in session state

The system demonstrates practical playlist management behavior: user-controlled grouping, searchable browsing, stateful interaction, and lightweight recommendation support.
