from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import json
import os

DEFAULT_SCORING_MODE = "balanced"
SCORING_WEIGHTS_BY_MODE: Dict[str, Dict[str, float]] = {
    "balanced": {
        "genre": 1.0,
        "mood": 1.0,
        "energy": 4.0,
        "danceability": 1.0,
        "acoustic": 0.5,
        "popularity": 1.5,
        "decade": 1.25,
        "mood_tag": 0.8,
        "instrumental": 1.0,
        "lyrical": 1.0,
        "explicitness": 0.9,
    },
    "genre-first": {
        "genre": 3.0,
        "mood": 0.8,
        "energy": 2.5,
        "danceability": 0.8,
        "acoustic": 0.4,
        "popularity": 1.0,
        "decade": 1.0,
        "mood_tag": 0.6,
        "instrumental": 0.6,
        "lyrical": 0.6,
        "explicitness": 0.6,
    },
    "mood-first": {
        "genre": 0.8,
        "mood": 3.0,
        "energy": 2.5,
        "danceability": 1.0,
        "acoustic": 0.6,
        "popularity": 1.0,
        "decade": 1.0,
        "mood_tag": 1.6,
        "instrumental": 0.8,
        "lyrical": 0.8,
        "explicitness": 0.7,
    },
    "energy-focused": {
        "genre": 0.7,
        "mood": 0.7,
        "energy": 6.0,
        "danceability": 1.5,
        "acoustic": 0.3,
        "popularity": 0.8,
        "decade": 0.7,
        "mood_tag": 0.5,
        "instrumental": 0.7,
        "lyrical": 0.7,
        "explicitness": 0.5,
    },
}


def get_scoring_weights(mode: str) -> Dict[str, float]:
    """Return scoring weights for a named strategy mode, falling back to balanced."""
    normalized_mode = str(mode or DEFAULT_SCORING_MODE).strip().lower()
    return SCORING_WEIGHTS_BY_MODE.get(normalized_mode, SCORING_WEIGHTS_BY_MODE[DEFAULT_SCORING_MODE])


def _normalize_key(value: object) -> str:
    return str(value or "").strip().lower()


def _build_song_payload(song) -> Dict:
    return {
        "id": song.id,
        "title": song.title,
        "artist": song.artist,
        "genre": song.genre,
        "mood": song.mood,
        "energy": song.energy,
        "tempo_bpm": song.tempo_bpm,
        "valence": song.valence,
        "danceability": song.danceability,
        "acousticness": song.acousticness,
        "popularity_0_100": song.popularity_0_100,
        "release_decade": song.release_decade,
        "mood_tags": song.mood_tags,
        "instrumentalness": song.instrumentalness,
        "lyrical_density": song.lyrical_density,
        "explicitness": song.explicitness,
    }


def _apply_diversity_penalty(song: Dict, artist_counts: Dict[str, int], genre_counts: Dict[str, int]) -> Tuple[float, List[str]]:
    song_payload = song.get("song_data", song.get("song", song))
    artist_key = _normalize_key(song_payload.get("artist"))
    genre_key = _normalize_key(song_payload.get("genre"))
    penalty = 0.0
    reasons: List[str] = []

    artist_hits = artist_counts.get(artist_key, 0)
    if artist_key and artist_hits > 0:
        artist_penalty = 2.5 * artist_hits
        penalty += artist_penalty
        reasons.append(f"diversity penalty: repeated artist (-{artist_penalty:.2f})")

    genre_hits = genre_counts.get(genre_key, 0)
    if genre_key and genre_hits > 0:
        genre_penalty = 0.85 * genre_hits
        penalty += genre_penalty
        reasons.append(f"diversity penalty: repeated genre (-{genre_penalty:.2f})")

    return penalty, reasons


def _rank_with_diversity(scored_songs: List[Dict], k: int) -> List[Tuple[Dict, float, str]]:
    remaining = list(scored_songs)
    ranked: List[Tuple[Dict, float, str]] = []
    selected_artist_counts: Dict[str, int] = {}
    selected_genre_counts: Dict[str, int] = {}

    while remaining and len(ranked) < k:
        best_index = 0
        best_adjusted_score = float("-inf")
        best_base_score = float("-inf")
        best_penalty_reasons: List[str] = []

        for index, candidate in enumerate(remaining):
            penalty, penalty_reasons = _apply_diversity_penalty(candidate, selected_artist_counts, selected_genre_counts)
            adjusted_score = candidate["score"] - penalty

            if (
                adjusted_score > best_adjusted_score
                or (adjusted_score == best_adjusted_score and candidate["score"] > best_base_score)
            ):
                best_index = index
                best_adjusted_score = adjusted_score
                best_base_score = candidate["score"]
                best_penalty_reasons = penalty_reasons

        chosen = remaining.pop(best_index)
        chosen_payload = chosen.get("song_data", chosen.get("song", chosen))
        artist_key = _normalize_key(chosen_payload.get("artist"))
        genre_key = _normalize_key(chosen_payload.get("genre"))

        if artist_key:
            selected_artist_counts[artist_key] = selected_artist_counts.get(artist_key, 0) + 1
        if genre_key:
            selected_genre_counts[genre_key] = selected_genre_counts.get(genre_key, 0) + 1

        explanation = chosen["explanation"]
        if best_penalty_reasons:
            explanation = f"{explanation}; {'; '.join(best_penalty_reasons)}"
        ranked.append((chosen["song"], best_adjusted_score, explanation))

    return ranked

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity_0_100: int = 50
    release_decade: int = 2010
    mood_tags: str = ""
    instrumentalness: float = 0.0
    lyrical_density: float = 0.5
    explicitness: float = 0.0

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    preferred_decade: Optional[int] = None
    preferred_mood_tags: Optional[List[str]] = None
    min_popularity: Optional[int] = None
    target_instrumentalness: Optional[float] = None
    target_lyrical_density: Optional[float] = None
    max_explicitness: Optional[float] = None

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5, mode: str = DEFAULT_SCORING_MODE) -> List[Song]:
        """Return top-k songs ranked by compatibility with the user profile."""
        scored: List[Dict] = []
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
            "preferred_decade": user.preferred_decade,
            "preferred_mood_tags": user.preferred_mood_tags,
            "min_popularity": user.min_popularity,
            "target_instrumentalness": user.target_instrumentalness,
            "target_lyrical_density": user.target_lyrical_density,
            "max_explicitness": user.max_explicitness,
            "scoring_mode": mode,
        }

        for song in self.songs:
            song_dict = _build_song_payload(song)
            score, _ = score_song(user_prefs, song_dict)
            scored.append({"song": song, "song_data": song_dict, "score": score, "explanation": ""})

        ranked = _rank_with_diversity(scored, k)
        return [item[0] for item in ranked]

    def explain_recommendation(self, user: UserProfile, song: Song, mode: str = DEFAULT_SCORING_MODE) -> str:
        """Explain why a specific song was recommended for this user."""
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
            "preferred_decade": user.preferred_decade,
            "preferred_mood_tags": user.preferred_mood_tags,
            "min_popularity": user.min_popularity,
            "target_instrumentalness": user.target_instrumentalness,
            "target_lyrical_density": user.target_lyrical_density,
            "max_explicitness": user.max_explicitness,
            "scoring_mode": mode,
        }
        song_dict = _build_song_payload(song)
        _, reasons = score_song(user_prefs, song_dict)
        return "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from JSON file.
    Required by src/main.py
    """
    # Load from JSON format
    json_path = csv_path.replace(".csv", ".json") if csv_path.endswith(".csv") else csv_path + ".json"
    
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            songs = json.load(f)
            # Ensure all songs have the expected fields
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
    
    raise FileNotFoundError(f"JSON file not found at {json_path}")

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    """Return a weighted score and plain-language reasons for a single song."""
    score = 0.0
    reasons: List[str] = []

    pref_genre = str(user_prefs.get("genre", "")).strip().lower()
    pref_mood = str(user_prefs.get("mood", "")).strip().lower()
    target_energy = float(user_prefs.get("energy", 0.5))
    likes_acoustic = bool(user_prefs.get("likes_acoustic", False))

    song_genre = str(song.get("genre", "")).strip().lower()
    song_mood = str(song.get("mood", "")).strip().lower()
    song_energy = float(song.get("energy", 0.0))
    song_danceability = float(song.get("danceability", 0.5))
    song_acousticness = float(song.get("acousticness", 0.0))
    song_popularity = float(song.get("popularity_0_100", 50.0))
    song_decade = int(song.get("release_decade", 2010))
    song_mood_tags_raw = str(song.get("mood_tags", ""))
    song_instrumentalness = float(song.get("instrumentalness", 0.0))
    song_lyrical_density = float(song.get("lyrical_density", 0.5))
    song_explicitness = float(song.get("explicitness", 0.0))

    preferred_decade = user_prefs.get("preferred_decade")
    preferred_mood_tags = user_prefs.get("preferred_mood_tags")
    min_popularity = user_prefs.get("min_popularity")
    target_instrumentalness = user_prefs.get("target_instrumentalness")
    target_lyrical_density = user_prefs.get("target_lyrical_density")
    max_explicitness = user_prefs.get("max_explicitness")

    weights = get_scoring_weights(str(user_prefs.get("scoring_mode", DEFAULT_SCORING_MODE)))

    genre_weight = weights["genre"]
    mood_weight = weights["mood"]
    energy_weight = weights["energy"]
    danceability_weight = weights["danceability"]
    acoustic_weight = weights["acoustic"]
    popularity_weight = weights["popularity"]
    decade_weight = weights["decade"]
    mood_tag_weight = weights["mood_tag"]
    instrumental_weight = weights["instrumental"]
    lyrical_weight = weights["lyrical"]
    explicitness_weight = weights["explicitness"]

    if pref_genre and song_genre == pref_genre:
        score += genre_weight
        reasons.append(f"genre match (+{genre_weight:.1f})")

    if pref_mood and song_mood == pref_mood:
        score += mood_weight
        reasons.append(f"mood match (+{mood_weight:.1f})")

    # Energy closeness: max +4.0 when identical, tapering to 0 as distance grows.
    energy_points = max(0.0, energy_weight * (1.0 - abs(song_energy - target_energy)))
    score += energy_points
    reasons.append(f"energy closeness (+{energy_points:.2f})")

    target_danceability = user_prefs.get("danceability")
    if target_danceability is None:
        target_danceability = user_prefs.get("target_danceability")
    if target_danceability is not None:
        target_danceability = float(target_danceability)
        dance_points = max(0.0, danceability_weight * (1.0 - abs(song_danceability - target_danceability)))
        score += dance_points
        reasons.append(f"danceability closeness (+{dance_points:.2f})")

    if likes_acoustic and song_acousticness >= 0.5:
        score += acoustic_weight
        reasons.append(f"acoustic preference match (+{acoustic_weight:.1f})")
    elif not likes_acoustic and song_acousticness < 0.5:
        score += acoustic_weight
        reasons.append(f"non-acoustic preference match (+{acoustic_weight:.1f})")

    # Popularity is normalized from 0-100 into a 0.0-1.0 multiplier.
    popularity_points = popularity_weight * max(0.0, min(song_popularity, 100.0)) / 100.0
    score += popularity_points
    reasons.append(f"popularity boost (+{popularity_points:.2f})")

    if min_popularity is not None:
        min_popularity = float(min_popularity)
        if song_popularity >= min_popularity:
            score += 0.7
            reasons.append("meets minimum popularity (+0.70)")
        else:
            score -= 0.7
            reasons.append("below minimum popularity (-0.70)")

    if preferred_decade is not None:
        preferred_decade = int(preferred_decade)
        # Up to +1.25 for exact decade match, tapering to 0 by a 40-year gap.
        decade_points = max(0.0, decade_weight * (1.0 - abs(song_decade - preferred_decade) / 40.0))
        score += decade_points
        reasons.append(f"decade proximity (+{decade_points:.2f})")

    song_mood_tags = {
        tag.strip().lower()
        for tag in song_mood_tags_raw.replace("|", ",").split(",")
        if tag.strip()
    }
    if preferred_mood_tags:
        if isinstance(preferred_mood_tags, str):
            preferred_mood_tags = [preferred_mood_tags]
        preferred_tag_set = {tag.strip().lower() for tag in preferred_mood_tags if str(tag).strip()}
        overlap = len(song_mood_tags.intersection(preferred_tag_set))
        tag_points = mood_tag_weight * overlap
        score += tag_points
        if overlap > 0:
            reasons.append(f"mood-tag overlap x{overlap} (+{tag_points:.2f})")

    if target_instrumentalness is not None:
        target_instrumentalness = float(target_instrumentalness)
        instrumental_points = max(
            0.0,
            instrumental_weight * (1.0 - abs(song_instrumentalness - target_instrumentalness)),
        )
        score += instrumental_points
        reasons.append(f"instrumentalness closeness (+{instrumental_points:.2f})")

    if target_lyrical_density is not None:
        target_lyrical_density = float(target_lyrical_density)
        lyrical_points = max(
            0.0,
            lyrical_weight * (1.0 - abs(song_lyrical_density - target_lyrical_density)),
        )
        score += lyrical_points
        reasons.append(f"lyrical-density closeness (+{lyrical_points:.2f})")

    if max_explicitness is not None:
        max_explicitness = float(max_explicitness)
        if song_explicitness <= max_explicitness:
            explicit_points = explicitness_weight * (1.0 - (song_explicitness / max(max_explicitness, 0.01)))
            explicit_points = max(0.0, explicit_points)
            score += explicit_points
            reasons.append(f"explicitness below max (+{explicit_points:.2f})")
        else:
            penalty = explicitness_weight * (song_explicitness - max_explicitness)
            score -= penalty
            reasons.append(f"explicitness penalty (-{penalty:.2f})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5, mode: Optional[str] = None) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    """Score all songs and return the top-k with score and explanation."""
    scored: List[Tuple[Dict, float, str]] = []
    active_mode = mode or user_prefs.get("scoring_mode", DEFAULT_SCORING_MODE)
    prefs_with_mode = dict(user_prefs)
    prefs_with_mode["scoring_mode"] = active_mode

    for song in songs:
        score, reasons = score_song(prefs_with_mode, song)
        reasons.insert(0, f"scoring mode: {str(active_mode).strip().lower()}")
        explanation = "; ".join(reasons)
        scored.append({"song": song, "score": score, "explanation": explanation})

    return _rank_with_diversity(scored, k)


# ============================================================================
# RAG-based recommendation functions (additive, non-breaking)
# ============================================================================

def retrieve_and_rank(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: Optional[str] = None,
    retrieve_k: int = 15,
) -> Tuple[List[Dict], List[Tuple[Dict, float, str]]]:
    """
    RAG-style recommendation: retrieve candidates, then rank.
    
    This is a non-breaking addition that layers retrieval before the existing
    ranking logic. The retrieval stage filters songs based on metadata matching,
    and the ranking stage uses the existing score_song logic for final scoring.
    
    Args:
        user_prefs: User profile dictionary.
        songs: Full song library.
        k: Number of final recommendations to return.
        mode: Scoring mode (balanced, genre-first, mood-first, energy-focused).
        retrieve_k: Number of candidates to retrieve before final ranking.
    
    Returns:
        Tuple of (retrieved_candidates, final_recommendations)
        - retrieved_candidates: List of retrieved song dicts
        - final_recommendations: List of (song_dict, score, explanation) tuples
    """
    try:
        from retrieval import retrieve_candidates
    except ImportError:
        # Fallback if retrieval module not available: use all songs
        retrieved = songs
    else:
        # Call retrieval layer to get top-k candidates
        retrieved_with_scores = retrieve_candidates(user_prefs, songs, k=retrieve_k)
        retrieved = [song for song, score in retrieved_with_scores]
    
    # Score and rank retrieved candidates using existing logic
    final_recs = recommend_songs(user_prefs, retrieved, k=k, mode=mode)
    
    return retrieved, final_recs


def explain_retrieval_evidence(
    user_prefs: Dict,
    song: Dict,
) -> Dict[str, any]:
    """
    Explain what metadata drove retrieval of a song.
    
    Returns a dictionary with:
    - matched_genre: bool
    - matched_mood: bool
    - energy_closeness: float
    - tag_matches: list of matching mood tags
    - explanation: human-readable string
    """
    def _normalize(text: str) -> str:
        return str(text or "").strip().lower()
    
    pref_genre = _normalize(user_prefs.get("genre", ""))
    pref_mood = _normalize(user_prefs.get("mood", ""))
    target_energy = float(user_prefs.get("energy", 0.5))
    pref_mood_tags = user_prefs.get("preferred_mood_tags", [])
    
    song_genre = _normalize(song.get("genre", ""))
    song_mood = _normalize(song.get("mood", ""))
    song_energy = float(song.get("energy", 0.5))
    song_mood_tags_raw = str(song.get("mood_tags", ""))
    
    # Parse mood tags
    if isinstance(pref_mood_tags, str):
        pref_tags_set = {_normalize(t) for t in pref_mood_tags.replace("|", ",").split(",") if t.strip()}
    else:
        pref_tags_set = {_normalize(t) for t in pref_mood_tags if t}
    
    song_tags = {
        _normalize(t)
        for t in song_mood_tags_raw.replace("|", ",").split(",")
        if t.strip()
    }
    
    matched_genre = bool(pref_genre and song_genre == pref_genre)
    matched_mood = bool(pref_mood and song_mood == pref_mood)
    energy_closeness = 1.0 - abs(song_energy - target_energy)
    tag_matches = list(song_tags & pref_tags_set)
    
    evidence_parts = []
    if matched_genre:
        evidence_parts.append(f"genre {pref_genre}")
    if matched_mood:
        evidence_parts.append(f"mood {pref_mood}")
    if tag_matches:
        evidence_parts.append(f"tags {', '.join(tag_matches)}")
    if energy_closeness > 0.7:
        evidence_parts.append(f"energy {song_energy:.2f}")
    
    explanation = f"Retrieved because: {'; '.join(evidence_parts) if evidence_parts else 'profile similarity'}"
    
    return {
        "matched_genre": matched_genre,
        "matched_mood": matched_mood,
        "energy_closeness": energy_closeness,
        "tag_matches": tag_matches,
        "explanation": explanation,
    }
