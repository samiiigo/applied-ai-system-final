"""
Retrieval layer for RAG-based music recommendation.

This module implements candidate filtering and scoring before the final ranking.
It extracts search hints from user preferences (genre, mood, energy, tags) and filters
the song library to retrieve top-k candidates that match those criteria.

The retrieval layer is separate from the final scoring, allowing us to:
1. Show which songs were retrieved (transparency)
2. Measure retrieval quality independently (recall@k, precision@k)
3. Keep the final ranking logic unchanged
"""

from typing import List, Dict, Tuple, Optional


def _normalize(text: str) -> str:
    """Normalize text for comparison: lowercase, strip whitespace."""
    return str(text or "").strip().lower()


def _parse_tags(tags_str: str) -> set:
    """Parse pipe or comma-separated mood tags into a set."""
    if not tags_str:
        return set()
    raw = str(tags_str).replace("|", ",").split(",")
    return {_normalize(t) for t in raw if t.strip()}


def _energy_in_range(song_energy: float, target_energy: float, tolerance: float = 0.3) -> bool:
    """Check if song energy is within tolerance of target energy."""
    return abs(song_energy - target_energy) <= tolerance


def retrieve_candidates(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 10,
    use_metadata_only: bool = True,
) -> List[Tuple[Dict, float]]:
    """
    Retrieve top-k songs from the library based on user preferences.
    
    Args:
        user_prefs: User profile with genre, mood, energy, mood_tags, etc.
        songs: Full song library.
        k: Number of candidates to return.
        use_metadata_only: If True, use only categorical/numeric filtering.
                          If False (future), use embeddings.
    
    Returns:
        List of (song_dict, retrieval_score) tuples, sorted by score descending.
    """
    if use_metadata_only:
        return _retrieve_metadata_only(user_prefs, songs, k)
    else:
        # Future: embedding-based retrieval
        return _retrieve_metadata_only(user_prefs, songs, k)


def _retrieve_metadata_only(
    user_prefs: Dict,
    songs: List[Dict],
    k: int,
) -> List[Tuple[Dict, float]]:
    """
    Filter and score songs using metadata matching: genre, mood, energy, tags.
    
    Scoring logic:
    - Genre exact match: +2.0
    - Mood exact match: +1.5
    - Energy closeness (within tolerance): +1.0
    - Mood tag overlap: +0.5 per matching tag
    - Decade proximity: +0.5 if within 20 years
    
    Returns top-k candidates sorted by retrieval score descending.
    """
    scored_candidates = []
    
    pref_genre = _normalize(user_prefs.get("genre", ""))
    pref_mood = _normalize(user_prefs.get("mood", ""))
    target_energy = float(user_prefs.get("energy", 0.5))
    pref_mood_tags = user_prefs.get("preferred_mood_tags", [])
    pref_decade = user_prefs.get("preferred_decade")
    
    # Normalize mood tags into a set
    if isinstance(pref_mood_tags, str):
        pref_mood_tags_set = _parse_tags(pref_mood_tags)
    elif isinstance(pref_mood_tags, (list, tuple)):
        pref_mood_tags_set = {_normalize(tag) for tag in pref_mood_tags if tag}
    else:
        pref_mood_tags_set = set()
    
    for song in songs:
        score = 0.0
        evidence = []
        
        song_genre = _normalize(song.get("genre", ""))
        song_mood = _normalize(song.get("mood", ""))
        song_energy = float(song.get("energy", 0.5))
        song_decade = int(song.get("release_decade", 2010))
        song_tags = _parse_tags(song.get("mood_tags", ""))
        
        # Genre match: +2.0
        if pref_genre and song_genre == pref_genre:
            score += 2.0
            evidence.append(f"genre:{pref_genre}")
        
        # Mood match: +1.5
        if pref_mood and song_mood == pref_mood:
            score += 1.5
            evidence.append(f"mood:{pref_mood}")
        
        # Energy closeness: +1.0 if within tolerance
        if _energy_in_range(song_energy, target_energy, tolerance=0.3):
            score += 1.0
            evidence.append(f"energy:{song_energy:.2f}")
        
        # Mood tag overlap: +0.5 per matching tag (up to 2.0 max)
        if pref_mood_tags_set and song_tags:
            tag_overlap = len(song_tags & pref_mood_tags_set)
            tag_score = min(0.5 * tag_overlap, 2.0)
            if tag_score > 0:
                score += tag_score
                matching_tags = list(song_tags & pref_mood_tags_set)
                evidence.append(f"tags:{','.join(matching_tags)}")
        
        # Decade proximity: +0.5 if within 20 years
        if pref_decade is not None:
            pref_decade = int(pref_decade)
            if abs(song_decade - pref_decade) <= 20:
                score += 0.5
                evidence.append(f"decade:{song_decade}")
        
        scored_candidates.append((song, score, evidence))
    
    # Sort by score descending, return top-k
    ranked = sorted(scored_candidates, key=lambda x: x[1], reverse=True)
    return [(song, score) for song, score, _ in ranked[:k]]


def compute_retrieval_metrics(
    retrieved: List[Dict],
    expected_genres: set,
    expected_moods: set,
) -> Dict[str, float]:
    """
    Compute basic retrieval metrics.
    
    Args:
        retrieved: List of retrieved song dictionaries.
        expected_genres: Set of genre strings expected in results.
        expected_moods: Set of mood strings expected in results.
    
    Returns:
        Dictionary with precision@k, recall@k metrics.
    """
    retrieved_genres = {_normalize(s.get("genre", "")) for s in retrieved}
    retrieved_moods = {_normalize(s.get("mood", "")) for s in retrieved}
    
    genre_precision = len(retrieved_genres & expected_genres) / len(retrieved_genres) if retrieved_genres else 0.0
    genre_recall = len(retrieved_genres & expected_genres) / len(expected_genres) if expected_genres else 0.0
    
    mood_precision = len(retrieved_moods & expected_moods) / len(retrieved_moods) if retrieved_moods else 0.0
    mood_recall = len(retrieved_moods & expected_moods) / len(expected_moods) if expected_moods else 0.0
    
    return {
        "genre_precision": genre_precision,
        "genre_recall": genre_recall,
        "mood_precision": mood_precision,
        "mood_recall": mood_recall,
    }
