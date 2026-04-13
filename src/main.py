"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

try:
    from .recommender import load_songs, recommend_songs
except ImportError:
    from recommender import load_songs, recommend_songs


def print_recommendations(profile_name: str, user_prefs: dict, songs: list) -> None:
    recommendations = recommend_songs(user_prefs, songs, k=5)

    print(f"\n=== {profile_name} ===")
    print(f"Preferences: {user_prefs}")
    print("Top 5 recommendations:\n")

    for idx, rec in enumerate(recommendations, start=1):
        song, score, explanation = rec
        reasons = [reason.strip() for reason in explanation.split(";") if reason.strip()]

        print(f"{idx}. {song['title']} by {song['artist']}")
        print(f"   Score   : {score:.2f}")
        print("   Reasons :")
        for reason in reasons:
            print(f"   - {reason}")
        print()

def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    profiles = [
        ("Happy Pop", {"genre": "pop", "mood": "happy", "energy": 0.8}),
        ("Chill Lofi", {"genre": "indie", "mood": "peaceful", "energy": 0.45, "likes_acoustic": True}),
        ("Deep Intense Rock", {"genre": "rap", "mood": "intense", "energy": 0.95}),
        ("Conflicted Edge Case", {"genre": "pop", "mood": "sad", "energy": 0.9, "likes_acoustic": True}),
    ]

    for profile_name, user_prefs in profiles:
        print_recommendations(profile_name, user_prefs, songs)


if __name__ == "__main__":
    main()
