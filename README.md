# 🎵 MoodMatch RAG: Explainable Music Recommendation System

## Project Summary

This project implements a **RAG-based (Retrieval-Augmented Generation) music recommender** that extends an earlier assignment-style recommender into a transparent, explainable recommendation system.

The system helps users discover songs that match their mood, genre preferences, and energy levels. Instead of treating recommendations as a black box, it:

1. **Retrieves** relevant songs from the library based on metadata filtering (genre, mood, energy, tags)
2. **Ranks** them using weighted scoring rules that reflect user preferences
3. **Explains** why each song was recommended, showing the evidence (matching genre, mood tags, energy closeness, etc.)
4. **Logs** all recommendation events for transparency and auditing

This design follows RAG principles: retrieval happens first to gather grounded context, then ranking and explanation use only that retrieved set, avoiding hallucinated recommendations.

---

## How The System Works

### Data Model
Each song has metadata including:
- **Title, Artist, Genre, Mood** — categorical attributes
- **Energy, Danceability, Acousticness** — numeric 0-1 scales
- **Tempo, Valence, Popularity, Decade** — additional context
- **Mood Tags** (pipe-separated) — fine-grained emotional tags
- **Instrumentalness, Lyrical Density, Explicitness** — content features

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

- **Non-breaking**: New RAG logic is additive; existing API unchanged
- **Hybrid retrieval**: Metadata filtering + numeric similarity, no embeddings required
- **Grounded explanations**: Only recommend songs in the indexed library
- **Transparent logging**: Full audit trail for accountability
- **Deterministic**: Same input always produces same output

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

### New RAG Functions

**recommender.py:**
```python
def retrieve_and_rank(user_prefs, songs, k=5, mode=None, retrieve_k=15)
    # RAG workflow: retrieve → rank → return (candidates, final_recs)

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

- **Transparency**: Retrieval shows candidate count, explanations break down scores
- **Guardrails**: Only recommend songs in the indexed library (no hallucinations)
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

MoodMatch RAG upgrades the assignment recommender into a **transparent, auditable RAG system** by:
- Adding a **retrieval stage** that filters candidates by metadata
- Keeping existing **scoring logic** as the reranker
- Providing **grounded explanations** tied to real song attributes
- Maintaining **full audit logs** for accountability

The system demonstrates core RAG principles: retrieval first, generation constrained to retrieved context, grounded explanations, and transparent evaluation.
