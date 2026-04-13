from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

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

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return top-k songs ranked by compatibility with the user profile."""
        scored: List[Tuple[Song, float]] = []
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
        }

        for song in self.songs:
            song_dict = {
                "genre": song.genre,
                "mood": song.mood,
                "energy": song.energy,
                "danceability": song.danceability,
                "acousticness": song.acousticness,
                "popularity_0_100": song.popularity_0_100,
                "release_decade": song.release_decade,
                "mood_tags": song.mood_tags,
                "instrumentalness": song.instrumentalness,
                "lyrical_density": song.lyrical_density,
                "explicitness": song.explicitness,
            }
            score, _ = score_song(user_prefs, song_dict)
            scored.append((song, score))

        scored.sort(key=lambda item: item[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
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
        }
        song_dict = {
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "danceability": song.danceability,
            "acousticness": song.acousticness,
            "popularity_0_100": song.popularity_0_100,
            "release_decade": song.release_decade,
            "mood_tags": song.mood_tags,
            "instrumentalness": song.instrumentalness,
            "lyrical_density": song.lyrical_density,
            "explicitness": song.explicitness,
        }
        _, reasons = score_song(user_prefs, song_dict)
        return "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    """Load songs from CSV into dictionaries with numeric fields parsed."""
    songs: List[Dict] = []
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append(
                {
                    "id": int(row["id"]),
                    "title": row["title"],
                    "artist": row["artist"],
                    "genre": row["genre"],
                    "mood": row["mood"],
                    "energy": float(row["energy"]),
                    "tempo_bpm": float(row["tempo_bpm"]),
                    "valence": float(row["valence"]),
                    "danceability": float(row["danceability"]),
                    "acousticness": float(row["acousticness"]),
                    "popularity_0_100": int(row.get("popularity_0_100", 50)),
                    "release_decade": int(row.get("release_decade", 2010)),
                    "mood_tags": row.get("mood_tags", ""),
                    "instrumentalness": float(row.get("instrumentalness", 0.0)),
                    "lyrical_density": float(row.get("lyrical_density", 0.5)),
                    "explicitness": float(row.get("explicitness", 0.0)),
                }
            )
    return songs

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

    genre_weight = 1.0
    mood_weight = 1.0
    energy_weight = 4.0
    danceability_weight = 1.0
    acoustic_weight = 0.5
    popularity_weight = 1.5
    decade_weight = 1.25
    mood_tag_weight = 0.8
    instrumental_weight = 1.0
    lyrical_weight = 1.0
    explicitness_weight = 0.9

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

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    """Score all songs and return the top-k with score and explanation."""
    scored: List[Tuple[Dict, float, str]] = []

    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons)
        scored.append((song, score, explanation))

    # Use sorted() to keep the original list unchanged and return a new ranked list.
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)
    return ranked[:k]
