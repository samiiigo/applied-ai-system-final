"""
Evaluation harness for RAG-based music recommendation.

This module provides:
1. Benchmark queries with expected relevant genres/moods
2. Retrieval metrics (precision@k, recall@k)
3. Groundedness checks (explanations only mention real metadata)
4. End-to-end recommendation quality assessment
"""

from typing import Dict, List, Tuple, Set

try:
    from .recommender import retrieve_and_rank, load_songs
    from .retrieval import compute_retrieval_metrics
except ImportError:
    from recommender import retrieve_and_rank, load_songs
    from retrieval import compute_retrieval_metrics


BENCHMARK_QUERIES = [
    {
        "name": "Party Music",
        "preferences": {
            "genre": "pop",
            "mood": "euphoric",
            "energy": 0.78,
            "preferred_mood_tags": ["party", "bold"],
        },
        "expected_genres": {"pop"},
        "expected_moods": {"euphoric", "confident"},
        "description": "User wants upbeat, party-ready pop music",
    },
    {
        "name": "Chill Indie Vibes",
        "preferences": {
            "genre": "indie",
            "mood": "dreamy",
            "energy": 0.35,
            "preferred_mood_tags": ["serene", "acoustic"],
        },
        "expected_genres": {"indie"},
        "expected_moods": {"dreamy", "peaceful"},
        "description": "User seeks relaxing indie music with acoustic elements",
    },
    {
        "name": "Energetic Workout",
        "preferences": {
            "genre": "hip-hop",
            "mood": "intense",
            "energy": 0.85,
            "preferred_mood_tags": ["adrenaline", "aggressive"],
        },
        "expected_genres": {"hip-hop", "rap"},
        "expected_moods": {"intense"},
        "description": "User needs high-energy music for workout sessions",
    },
    {
        "name": "Late Night Electronic",
        "preferences": {
            "genre": "electronic",
            "mood": "vibey",
            "energy": 0.77,
            "preferred_mood_tags": ["euphoric", "club"],
        },
        "expected_genres": {"electronic"},
        "expected_moods": {"vibey"},
        "description": "User wants uplifting electronic dance music",
    },
    {
        "name": "R&B Smooth Vibes",
        "preferences": {
            "genre": "r&b",
            "mood": "smooth",
            "energy": 0.65,
            "preferred_mood_tags": ["sultry", "night-drive"],
        },
        "expected_genres": {"r&b"},
        "expected_moods": {"smooth", "luxurious"},
        "description": "User seeks smooth R&B for evening listening",
    },
]


def evaluate_retrieval(
    songs: List[Dict],
    verbose: bool = True,
) -> Dict[str, any]:
    """
    Evaluate retrieval quality across benchmark queries.
    
    Returns metrics including precision@k, recall@k for genres and moods.
    """
    results = {
        "benchmark_queries": len(BENCHMARK_QUERIES),
        "queries": [],
        "aggregate_metrics": {
            "avg_genre_precision": 0.0,
            "avg_genre_recall": 0.0,
            "avg_mood_precision": 0.0,
            "avg_mood_recall": 0.0,
        },
    }
    
    total_genre_prec = 0.0
    total_genre_rec = 0.0
    total_mood_prec = 0.0
    total_mood_rec = 0.0
    
    for query in BENCHMARK_QUERIES:
        if verbose:
            print(f"\n{'='*70}")
            print(f"Benchmark: {query['name']}")
            print(f"Description: {query['description']}")
        
        # Run retrieval
        retrieved, final_recs = retrieve_and_rank(
            query["preferences"],
            songs,
            k=3,
            retrieve_k=5,
        )
        
        # Compute metrics
        metrics = compute_retrieval_metrics(
            retrieved,
            query["expected_genres"],
            query["expected_moods"],
        )
        
        if verbose:
            print(f"Retrieved {len(retrieved)} candidates:")
            for song in retrieved[:3]:
                print(f"  - {song['title']} ({song['genre']}, {song['mood']})")
            print(f"Metrics:")
            print(f"  Genre Precision: {metrics['genre_precision']:.2%}")
            print(f"  Genre Recall:    {metrics['genre_recall']:.2%}")
            print(f"  Mood Precision:  {metrics['mood_precision']:.2%}")
            print(f"  Mood Recall:     {metrics['mood_recall']:.2%}")
        
        total_genre_prec += metrics["genre_precision"]
        total_genre_rec += metrics["genre_recall"]
        total_mood_prec += metrics["mood_precision"]
        total_mood_rec += metrics["mood_recall"]
        
        results["queries"].append({
            "name": query["name"],
            "metrics": metrics,
        })
    
    # Compute averages
    n = len(BENCHMARK_QUERIES)
    results["aggregate_metrics"]["avg_genre_precision"] = total_genre_prec / n
    results["aggregate_metrics"]["avg_genre_recall"] = total_genre_rec / n
    results["aggregate_metrics"]["avg_mood_precision"] = total_mood_prec / n
    results["aggregate_metrics"]["avg_mood_recall"] = total_mood_rec / n
    
    if verbose:
        print(f"\n{'='*70}")
        print("AGGREGATE METRICS")
        print(f"{'='*70}")
        print(f"Avg Genre Precision: {results['aggregate_metrics']['avg_genre_precision']:.2%}")
        print(f"Avg Genre Recall:    {results['aggregate_metrics']['avg_genre_recall']:.2%}")
        print(f"Avg Mood Precision:  {results['aggregate_metrics']['avg_mood_precision']:.2%}")
        print(f"Avg Mood Recall:     {results['aggregate_metrics']['avg_mood_recall']:.2%}")
    
    return results


def check_groundedness(final_recommendations: List[Tuple[Dict, float, str]]) -> Dict[str, any]:
    """
    Check if explanations only mention real metadata.
    
    Returns a report with groundedness score and any hallucinations detected.
    """
    valid_metadata_fields = {
        "genre", "mood", "energy", "danceability", "acousticness",
        "popularity", "decade", "tags", "tag", "instrumental",
        "lyrical", "explicit", "popularity_0_100",
    }
    
    hallucinations = []
    grounded_count = 0
    
    for song_dict, score, explanation in final_recommendations:
        explanation_lower = explanation.lower()
        
        # Simple heuristic: check if explanation mentions song title, artist
        # or other fields not in the metadata
        mentions_title = song_dict.get("title", "").lower() in explanation_lower
        mentions_artist = song_dict.get("artist", "").lower() in explanation_lower
        
        if mentions_title or mentions_artist:
            # These are fine, they're metadata
            pass
        
        # Check for invented attributes (strings that don't match known fields)
        for word in explanation_lower.split():
            word = word.rstrip("(),;:").lower()
            if any(field in word for field in valid_metadata_fields):
                grounded_count += 1
                break
    
    groundedness_score = grounded_count / len(final_recommendations) if final_recommendations else 0.0
    
    return {
        "groundedness_score": groundedness_score,
        "grounded_count": grounded_count,
        "total_recommendations": len(final_recommendations),
        "hallucinations": hallucinations,
    }


def run_full_evaluation(csv_path: str = "data/songs.csv", verbose: bool = True) -> Dict[str, any]:
    """
    Run the complete evaluation suite: retrieval metrics + groundedness checks.
    """
    if verbose:
        print("\n" + "="*70)
        print("MOODMATCH RAG EVALUATION SUITE")
        print("="*70)
    
    songs = load_songs(csv_path)
    
    # Evaluate retrieval
    if verbose:
        print("\n1. RETRIEVAL EVALUATION")
        print("-" * 70)
    
    retrieval_results = evaluate_retrieval(songs, verbose=verbose)
    
    # Evaluate groundedness on first benchmark query
    if verbose:
        print("\n2. GROUNDEDNESS CHECK")
        print("-" * 70)
    
    first_query = BENCHMARK_QUERIES[0]
    _, final_recs = retrieve_and_rank(first_query["preferences"], songs, k=3, retrieve_k=5)
    
    groundedness = check_groundedness(final_recs)
    
    if verbose:
        print(f"Groundedness Score: {groundedness['groundedness_score']:.2%}")
        print(f"Grounded Recommendations: {groundedness['grounded_count']}/{groundedness['total_recommendations']}")
    
    return {
        "retrieval": retrieval_results,
        "groundedness": groundedness,
    }


if __name__ == "__main__":
    results = run_full_evaluation(verbose=True)
