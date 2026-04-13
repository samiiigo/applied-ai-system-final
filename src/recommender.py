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
        }

        for song in self.songs:
            song_dict = {
                "genre": song.genre,
                "mood": song.mood,
                "energy": song.energy,
                "danceability": song.danceability,
                "acousticness": song.acousticness,
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
        }
        song_dict = {
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "danceability": song.danceability,
            "acousticness": song.acousticness,
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

    genre_weight = 1.0
    mood_weight = 1.0
    energy_weight = 4.0
    danceability_weight = 1.0
    acoustic_weight = 0.5

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
