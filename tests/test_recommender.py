from src.recommender import Song, UserProfile, Recommender, recommend_songs, retrieve_rank_with_trace

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_scoring_modes_change_ranking_order():
    songs = [
        {
            "id": 1,
            "title": "Genre Match Song",
            "artist": "A",
            "genre": "pop",
            "mood": "sad",
            "energy": 0.8,
            "tempo_bpm": 120,
            "valence": 0.6,
            "danceability": 0.7,
            "acousticness": 0.3,
            "popularity_0_100": 80,
            "release_decade": 2010,
            "mood_tags": "nostalgic|moody",
            "instrumentalness": 0.1,
            "lyrical_density": 0.6,
            "explicitness": 0.2,
        },
        {
            "id": 2,
            "title": "Mood Match Song",
            "artist": "B",
            "genre": "rock",
            "mood": "happy",
            "energy": 0.8,
            "tempo_bpm": 120,
            "valence": 0.7,
            "danceability": 0.7,
            "acousticness": 0.3,
            "popularity_0_100": 80,
            "release_decade": 2010,
            "mood_tags": "euphoric|uplifting",
            "instrumentalness": 0.1,
            "lyrical_density": 0.6,
            "explicitness": 0.2,
        },
    ]
    prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
    }

    genre_first = recommend_songs(prefs, songs, k=2, mode="genre-first")
    mood_first = recommend_songs(prefs, songs, k=2, mode="mood-first")

    assert genre_first[0][0]["title"] == "Genre Match Song"
    assert mood_first[0][0]["title"] == "Mood Match Song"


def test_diversity_penalty_limits_repeated_artists():
    songs = [
        {
            "id": 1,
            "title": "Artist A Strong 1",
            "artist": "Artist A",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.9,
            "tempo_bpm": 124,
            "valence": 0.9,
            "danceability": 0.9,
            "acousticness": 0.2,
            "popularity_0_100": 92,
            "release_decade": 2020,
            "mood_tags": "euphoric|party",
            "instrumentalness": 0.05,
            "lyrical_density": 0.6,
            "explicitness": 0.1,
        },
        {
            "id": 2,
            "title": "Artist A Strong 2",
            "artist": "Artist A",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.88,
            "tempo_bpm": 122,
            "valence": 0.88,
            "danceability": 0.88,
            "acousticness": 0.2,
            "popularity_0_100": 90,
            "release_decade": 2020,
            "mood_tags": "euphoric|party",
            "instrumentalness": 0.05,
            "lyrical_density": 0.6,
            "explicitness": 0.1,
        },
        {
            "id": 3,
            "title": "Different Artist",
            "artist": "Artist B",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.87,
            "tempo_bpm": 121,
            "valence": 0.87,
            "danceability": 0.87,
            "acousticness": 0.2,
            "popularity_0_100": 89,
            "release_decade": 2020,
            "mood_tags": "euphoric|party",
            "instrumentalness": 0.05,
            "lyrical_density": 0.6,
            "explicitness": 0.1,
        },
    ]
    prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.9,
        "scoring_mode": "genre-first",
    }

    ranked = recommend_songs(prefs, songs, k=3)

    assert ranked[0][0]["artist"] == "Artist A"
    assert ranked[1][0]["artist"] == "Artist B"
    assert len({ranked[0][0]["artist"], ranked[1][0]["artist"]}) == 2


def test_agentic_workflow_returns_trace_steps():
    songs = [
        {
            "id": 1,
            "title": "Trace Song A",
            "artist": "Artist A",
            "genre": "pop",
            "mood": "euphoric",
            "energy": 0.8,
            "tempo_bpm": 120,
            "valence": 0.8,
            "danceability": 0.8,
            "acousticness": 0.2,
            "popularity_0_100": 90,
            "release_decade": 2020,
            "mood_tags": "party|bold",
            "instrumentalness": 0.1,
            "lyrical_density": 0.6,
            "explicitness": 0.1,
        },
        {
            "id": 2,
            "title": "Trace Song B",
            "artist": "Artist B",
            "genre": "rock",
            "mood": "intense",
            "energy": 0.9,
            "tempo_bpm": 130,
            "valence": 0.4,
            "danceability": 0.6,
            "acousticness": 0.2,
            "popularity_0_100": 86,
            "release_decade": 2010,
            "mood_tags": "adrenaline|bold",
            "instrumentalness": 0.1,
            "lyrical_density": 0.6,
            "explicitness": 0.2,
        },
    ]
    prefs = {
        "genre": "pop",
        "mood": "euphoric",
        "energy": 0.8,
        "preferred_mood_tags": ["party", "bold"],
        "scoring_mode": "balanced",
    }

    result = retrieve_rank_with_trace(prefs, songs, k=1, retrieve_k=2)

    assert "retrieved" in result
    assert "final_recommendations" in result
    assert "decision_trace" in result
    assert len(result["decision_trace"]) >= 4
    assert [step["stage"] for step in result["decision_trace"][:4]] == ["plan", "retrieve", "rank", "decide"]
