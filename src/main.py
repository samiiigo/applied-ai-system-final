"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import textwrap

try:
    from .recommender import load_songs, recommend_songs
except ImportError:
    from recommender import load_songs, recommend_songs

try:
    from .retrieval import retrieve_candidates
    from .logger import log_recommendation
    from .recommender import retrieve_and_rank, explain_retrieval_evidence
    RETRIEVAL_AVAILABLE = True
except ImportError:
    RETRIEVAL_AVAILABLE = False


def _wrap_cell(value: str, width: int) -> list:
    lines = textwrap.wrap(str(value), width=width) or [""]
    return lines


def _print_recommendation_table(recommendations: list) -> None:
    headers = ["#", "Title", "Artist", "Score", "Reasons"]
    rows = []

    for idx, rec in enumerate(recommendations, start=1):
        song, score, explanation = rec
        reasons = " | ".join(
            reason.strip()
            for reason in explanation.split(";")
            if reason.strip()
        )
        rows.append([str(idx), song["title"], song["artist"], f"{score:.2f}", reasons])

    widths = [
        max(len(headers[col]), *(len(row[col]) for row in rows))
        for col in range(len(headers))
    ]
    widths[0] = max(widths[0], 1)
    widths[1] = min(max(widths[1], 8), 28)
    widths[2] = min(max(widths[2], 8), 20)
    widths[3] = max(widths[3], 5)
    widths[4] = min(max(widths[4], 18), 70)

    def border(char: str = "-") -> str:
        return "+" + "+".join(char * (width + 2) for width in widths) + "+"

    def format_row(cells: list) -> str:
        return "|" + "|".join(f" {cells[i]:<{widths[i]}} " for i in range(len(widths))) + "|"

    print(border("-"))
    print(format_row(headers))
    print(border("="))

    for row in rows:
        wrapped_cells = [_wrap_cell(row[col], widths[col]) for col in range(len(row))]
        max_lines = max(len(cell_lines) for cell_lines in wrapped_cells)
        for line_index in range(max_lines):
            line_cells = [
                wrapped_cells[col][line_index] if line_index < len(wrapped_cells[col]) else ""
                for col in range(len(row))
            ]
            print(format_row(line_cells))
        print(border("-"))


def print_recommendations(profile_name: str, user_prefs: dict, songs: list) -> None:
    mode = user_prefs.get("scoring_mode", "balanced")
    recommendations = recommend_songs(user_prefs, songs, k=5, mode=mode)

    print(f"\n=== {profile_name} ===")
    print(f"Scoring Mode: {mode}")
    print(f"Preferences: {user_prefs}")
    print("Top 5 recommendations:")
    _print_recommendation_table(recommendations)


def print_rag_recommendations(profile_name: str, user_prefs: dict, songs: list) -> None:
    """RAG-aware recommendation with retrieval transparency."""
    if not RETRIEVAL_AVAILABLE:
        print_recommendations(profile_name, user_prefs, songs)
        return
    
    mode = user_prefs.get("scoring_mode", "balanced")
    retrieved, recommendations = retrieve_and_rank(user_prefs, songs, k=5, retrieve_k=8, mode=mode)
    
    print(f"\n=== {profile_name} (RAG) ===")
    print(f"Scoring Mode: {mode}")
    print(f"Preferences: {user_prefs}")
    print(f"\nRetrieval: {len(retrieved)} candidates retrieved from {len(songs)} songs")
    print("-" * 70)
    print("Top 5 recommendations with retrieval evidence:")
    _print_recommendation_table(recommendations)
    
    # Log the recommendation event
    log_recommendation(user_prefs, profile_name, retrieved, recommendations, mode=mode, confidence="medium")

def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    profiles = [
        (
            "Genre-First Pop Explorer",
            {
                "genre": "pop",
                "mood": "euphoric",
                "energy": 0.78,
                "preferred_mood_tags": ["party", "bold"],
                "preferred_decade": 2010,
                "scoring_mode": "genre-first",
            },
        ),
        (
            "Mood-First Dream Listener",
            {
                "genre": "indie",
                "mood": "dreamy",
                "energy": 0.55,
                "likes_acoustic": True,
                "preferred_mood_tags": ["nostalgic", "introspective", "dreamy"],
                "scoring_mode": "mood-first",
            },
        ),
        (
            "Energy-Focused Gym Session",
            {
                "genre": "rap",
                "mood": "intense",
                "energy": 0.92,
                "min_popularity": 75,
                "target_lyrical_density": 0.55,
                "scoring_mode": "energy-focused",
            },
        ),
        (
            "Balanced All-Rounder",
            {
                "genre": "pop",
                "mood": "sad",
                "energy": 0.9,
                "likes_acoustic": True,
                "max_explicitness": 0.3,
                "scoring_mode": "balanced",
            },
        ),
    ]

    for profile_name, user_prefs in profiles:
        print_rag_recommendations(profile_name, user_prefs, songs)
    
    # Run evaluation if available
    if RETRIEVAL_AVAILABLE:
        try:
            try:
                from .evaluation import run_full_evaluation
            except ImportError:
                from evaluation import run_full_evaluation
            print(f"\n{'='*70}")
            print("RUNNING RAG EVALUATION SUITE")
            print(f"{'='*70}")
            eval_results = run_full_evaluation(csv_path="data/songs.csv", verbose=False)
            print(f"\nEvaluation Summary:")
            print(f"  Genre Recall: {eval_results['retrieval']['aggregate_metrics']['avg_genre_recall']:.1%}")
            print(f"  Mood Recall:  {eval_results['retrieval']['aggregate_metrics']['avg_mood_recall']:.1%}")
            print(f"  Groundedness: {eval_results['groundedness']['groundedness_score']:.1%}")
        except Exception as e:
            print(f"[Evaluation skipped: {e}]")


if __name__ == "__main__":
    main()
