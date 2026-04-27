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

from typing import List, Dict, Tuple, Optional, Set
import json
import os
import re


def _normalize(text: str) -> str:
    """Normalize text for comparison: lowercase, strip whitespace."""
    return str(text or "").strip().lower()


def _song_identity(song: Dict) -> str:
    """Build a stable identity key for deduping songs across sources."""
    song_id = song.get("id")
    if song_id is not None:
        return f"id:{song_id}"
    return f"title:{_normalize(song.get('title', ''))}|artist:{_normalize(song.get('artist', ''))}"


def merge_song_sources(base_songs: List[Dict], extra_song_sources: Optional[List[List[Dict]]] = None) -> List[Dict]:
    """Merge base songs with optional extra sources, deduping by id/title+artist."""
    merged: List[Dict] = []
    seen: Set[str] = set()

    for song in base_songs or []:
        key = _song_identity(song)
        if key not in seen:
            merged.append(song)
            seen.add(key)

    for source in extra_song_sources or []:
        for song in source or []:
            key = _song_identity(song)
            if key in seen:
                continue
            merged.append(song)
            seen.add(key)

    return merged


def load_song_source(path: str) -> List[Dict]:
    """Load a JSON song source file and ensure required fields are present."""
    normalized_path = str(path or "").strip()
    candidate_paths = [normalized_path]
    if not os.path.isabs(normalized_path):
        candidate_paths.append(os.path.normpath(os.path.join(os.path.dirname(__file__), normalized_path)))
        candidate_paths.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "..", normalized_path)))

    resolved_path = next((p for p in candidate_paths if os.path.exists(p)), None)
    if not resolved_path:
        raise FileNotFoundError(f"Song source not found: {path}")

    with open(resolved_path, "r", encoding="utf-8") as f:
        songs = json.load(f)

    for song in songs:
        song.setdefault("id", 1)
        song.setdefault("title", "Unknown")
        song.setdefault("artist", "Unknown")
        song.setdefault("genre", "Unknown")
        song.setdefault("mood", "neutral")
        song.setdefault("energy", 0.5)
        song.setdefault("tempo_bpm", 100)
        song.setdefault("valence", 0.5)
        song.setdefault("danceability", 0.5)
        song.setdefault("acousticness", 0.5)
        song.setdefault("popularity_0_100", 50)
        song.setdefault("release_decade", 2010)
        song.setdefault("mood_tags", "")
        song.setdefault("instrumentalness", 0.0)
        song.setdefault("lyrical_density", 0.5)
        song.setdefault("explicitness", 0.0)

    return songs


def load_custom_documents(path: str) -> List[Dict]:
    """Load external custom documents used to boost retrieval relevance."""
    normalized_path = str(path or "").strip()
    candidate_paths = [normalized_path]
    if not os.path.isabs(normalized_path):
        candidate_paths.append(os.path.normpath(os.path.join(os.path.dirname(__file__), normalized_path)))
        candidate_paths.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "..", normalized_path)))

    resolved_path = next((p for p in candidate_paths if os.path.exists(p)), None)
    if not resolved_path:
        raise FileNotFoundError(f"Custom document source not found: {path}")

    with open(resolved_path, "r", encoding="utf-8") as f:
        documents = json.load(f)

    return documents if isinstance(documents, list) else []


def _tokenize(text: str) -> Set[str]:
    return {token for token in re.split(r"[^a-z0-9]+", _normalize(text)) if token}


def _query_terms(user_prefs: Dict) -> Set[str]:
    terms: Set[str] = set()
    terms.update(_tokenize(user_prefs.get("genre", "")))
    terms.update(_tokenize(user_prefs.get("mood", "")))
    preferred_tags = user_prefs.get("preferred_mood_tags", [])
    if isinstance(preferred_tags, str):
        preferred_tags = preferred_tags.replace("|", ",").split(",")
    for tag in preferred_tags or []:
        terms.update(_tokenize(str(tag)))
    return terms


def _document_boost(song: Dict, user_prefs: Dict, custom_documents: Optional[List[Dict]]) -> float:
    """Return relevance boost from custom documents for this song."""
    if not custom_documents:
        return 0.0

    query_terms = _query_terms(user_prefs)
    if not query_terms:
        return 0.0

    song_id = song.get("id")
    song_title = _normalize(song.get("title", ""))
    song_genre = _normalize(song.get("genre", ""))
    song_mood = _normalize(song.get("mood", ""))
    song_tags = _parse_tags(song.get("mood_tags", ""))

    boost = 0.0
    for doc in custom_documents:
        keywords = set()
        for field in ("keywords", "aliases", "genre_aliases", "mood_aliases"):
            value = doc.get(field, [])
            if isinstance(value, str):
                value = value.replace("|", ",").split(",")
            for token in value or []:
                keywords.update(_tokenize(str(token)))

        keywords.update(_tokenize(doc.get("content", "")))
        overlap = len(query_terms & keywords)
        if overlap == 0:
            continue

        linked_ids = set(doc.get("linked_song_ids", []) or [])
        linked_titles = {_normalize(t) for t in (doc.get("linked_titles", []) or [])}
        linked_genres = {_normalize(g) for g in (doc.get("linked_genres", []) or [])}
        linked_moods = {_normalize(m) for m in (doc.get("linked_moods", []) or [])}
        linked_tags = {_normalize(t) for t in (doc.get("linked_tags", []) or [])}

        is_linked = False
        if song_id is not None and song_id in linked_ids:
            is_linked = True
        if song_title and song_title in linked_titles:
            is_linked = True
        if song_genre and song_genre in linked_genres:
            is_linked = True
        if song_mood and song_mood in linked_moods:
            is_linked = True
        if song_tags and (song_tags & linked_tags):
            is_linked = True

        if is_linked:
            boost += min(2.0, 0.5 + (0.45 * overlap))

    return boost


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
    extra_song_sources: Optional[List[List[Dict]]] = None,
    custom_documents: Optional[List[Dict]] = None,
    custom_document_weight: float = 1.0,
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
    merged_songs = merge_song_sources(songs, extra_song_sources)

    if use_metadata_only and not custom_documents:
        return _retrieve_metadata_only(user_prefs, merged_songs, k)

    metadata_ranked = _retrieve_metadata_only(user_prefs, merged_songs, len(merged_songs))
    rescored: List[Tuple[Dict, float]] = []
    for song, metadata_score in metadata_ranked:
        doc_score = _document_boost(song, user_prefs, custom_documents)
        combined_score = metadata_score + (custom_document_weight * doc_score)
        rescored.append((song, combined_score))

    return sorted(rescored, key=lambda item: item[1], reverse=True)[:k]


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
