from src.streamlit_app import (
    _build_playlists,
    _choose_lucky_pool,
    _classify_playlist,
    _compute_stats,
    _normalize_new_song,
    _normalize_text,
    _playlist_rows,
    _song_matches_query,
    _to_rows,
)


def _song(**overrides):
    base = {
        "id": 1,
        "title": "Midnight Drive",
        "artist": "Nova",
        "genre": "pop",
        "mood": "euphoric",
        "energy": 0.72,
        "tempo_bpm": 120,
        "valence": 0.6,
        "danceability": 0.8,
        "acousticness": 0.2,
        "popularity_0_100": 80,
        "release_decade": 2020,
        "mood_tags": "party|night-drive",
        "instrumentalness": 0.1,
        "lyrical_density": 0.5,
        "explicitness": 0.1,
    }
    base.update(overrides)
    return base


def _profile(**overrides):
    base = {
        "name": "Tester",
        "favorite_genre": "pop",
        "hype_min_energy": 0.7,
        "chill_max_energy": 0.45,
        "include_mixed": True,
    }
    base.update(overrides)
    return base


def test_normalize_text_trims_and_handles_none():
    assert _normalize_text("  hello  ") == "hello"
    assert _normalize_text(None) == ""


def test_classify_playlist_hype_for_high_energy():
    song = _song(energy=0.85)
    playlist = _classify_playlist(song, _profile())
    assert playlist == "Hype"


def test_classify_playlist_chill_for_low_energy():
    song = _song(energy=0.35, genre="jazz", mood_tags="serene|acoustic")
    playlist = _classify_playlist(song, _profile())
    assert playlist == "Chill"


def test_classify_playlist_mixed_when_between_thresholds_and_no_keywords():
    song = _song(
        title="City Walk",
        genre="jazz",
        mood_tags="warm|late-night",
        energy=0.55,
    )
    playlist = _classify_playlist(song, _profile(favorite_genre="rock"))
    assert playlist == "Mixed"


def test_build_playlists_moves_mixed_when_include_mixed_false():
    songs = [
        _song(id=1, title="Above Mid", energy=0.58, genre="jazz", mood_tags="soft"),
        _song(id=2, title="Below Mid", energy=0.52, genre="jazz", mood_tags="soft"),
    ]
    playlists = _build_playlists(
        songs,
        _profile(favorite_genre="rock", include_mixed=False, hype_min_energy=0.7, chill_max_energy=0.45),
    )

    assert len(playlists["Mixed"]) == 0
    assert [s["title"] for s in playlists["Hype"]] == ["Above Mid"]
    assert [s["title"] for s in playlists["Chill"]] == ["Below Mid"]


def test_song_matches_query_checks_tags_title_and_artist():
    song = _song(title="Sunrise", artist="Aurora", mood_tags="dreamy|soft")

    assert _song_matches_query(song, "sun") is True
    assert _song_matches_query(song, "aur") is True
    assert _song_matches_query(song, "dreamy") is True
    assert _song_matches_query(song, "missing") is False


def test_playlist_rows_formats_tags_and_energy():
    rows = _playlist_rows([_song(mood_tags="a|b", energy=0.734)], "Hype")

    assert rows[0]["Playlist"] == "Hype"
    assert rows[0]["Tags"] == "a, b"
    assert rows[0]["Energy"] == 0.73


def test_compute_stats_returns_expected_counts_and_top_artist():
    songs = [
        _song(id=1, artist="Nova", energy=0.8),
        _song(id=2, artist="Nova", energy=0.4),
        _song(id=3, artist="Rhea", energy=0.6),
    ]
    playlists = {
        "Hype": [songs[0]],
        "Chill": [songs[1]],
        "Mixed": [songs[2]],
    }

    stats = _compute_stats(playlists, songs)

    assert stats["total"] == 3
    assert stats["hype_count"] == 1
    assert stats["chill_count"] == 1
    assert stats["mixed_count"] == 1
    assert stats["hype_ratio"] == 1 / 3
    assert stats["top_artist"] == "Nova"


def test_normalize_new_song_coerces_defaults_and_tags():
    raw = {
        "title": "  Test Song  ",
        "artist": "",
        "genre": "",
        "mood": "",
        "mood_tags": "  Chill, Focus | STUDY  ",
        "energy": "0.9",
    }

    normalized = _normalize_new_song(raw, next_id=42)

    assert normalized["id"] == 42
    assert normalized["title"] == "Test Song"
    assert normalized["artist"] == "Unknown Artist"
    assert normalized["genre"] == "Unknown"
    assert normalized["mood"] == "custom"
    assert normalized["mood_tags"] == "chill|focus|study"
    assert normalized["energy"] == 0.9


def test_choose_lucky_pool_returns_playlist_or_all_songs():
    songs = [_song(id=1), _song(id=2)]
    playlists = {"Hype": [songs[0]], "Chill": [], "Mixed": [songs[1]]}

    assert _choose_lucky_pool(playlists, songs, "Hype") == [songs[0]]
    assert _choose_lucky_pool(playlists, songs, "Chill") == []
    assert _choose_lucky_pool(playlists, songs, "Mixed") == [songs[1]]
    assert _choose_lucky_pool(playlists, songs, "Any") == songs


def test_to_rows_builds_ranked_table_rows():
    recs = [
        (_song(title="A", artist="Artist A", genre="pop", mood="happy"), 4.567, "genre match"),
        (_song(title="B", artist="Artist B", genre="rock", mood="moody"), 3.111, "mood match"),
    ]

    rows = _to_rows(recs)

    assert rows[0]["Rank"] == 1
    assert rows[0]["Title"] == "A"
    assert rows[0]["Score"] == 4.57
    assert rows[1]["Rank"] == 2
    assert rows[1]["Why"] == "mood match"
