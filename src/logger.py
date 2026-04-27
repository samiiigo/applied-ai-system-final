"""
Structured logging for RAG-based music recommendation.

This module logs:
- User queries and preferences
- Retrieved candidates and their scores
- Final recommendations and confidence
- Explanations and evidence tags
- Errors and fallback cases

Logs are written to a JSONL file for auditing and analysis.
"""

import json
import os
from datetime import datetime, timezone
import uuid
from typing import Dict, List, Optional, Any


DEFAULT_LOG_FILE = "recommendations.jsonl"


class RecommendationLogger:
    """Logs recommendation events to a JSONL file."""
    
    def __init__(self, log_file: str = DEFAULT_LOG_FILE):
        self.log_file = log_file
        # Ensure directory exists
        os.makedirs(os.path.dirname(log_file) if os.path.dirname(log_file) else ".", exist_ok=True)
    
    def log_recommendation(
        self,
        user_prefs: Dict,
        query: Optional[str],
        retrieved: List[Dict],
        final_recommendations: List[Dict],
        mode: str = "balanced",
        confidence: str = "medium",
        error: Optional[str] = None,
        decision_trace: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Log a complete recommendation event.
        
        Args:
            user_prefs: User profile dictionary.
            query: Optional natural-language query string.
            retrieved: List of retrieved song candidates.
            final_recommendations: List of final recommended songs.
            mode: Scoring mode used (balanced, genre-first, etc.).
            confidence: Confidence level (strong, medium, weak).
            error: Optional error message if recommendation failed.
        """
        event_id = str(uuid.uuid4())
        normalized_final_recommendations = []
        for rank, rec in enumerate(final_recommendations, start=1):
            song = rec if isinstance(rec, dict) else rec[0] if rec else {}
            score = rec.get("score") if isinstance(rec, dict) else (rec[1] if len(rec) > 1 else None)
            normalized_final_recommendations.append(
                {
                    "rank": rank,
                    "id": song.get("id"),
                    "title": song.get("title"),
                    "artist": song.get("artist"),
                    "genre": song.get("genre"),
                    "mood": song.get("mood"),
                    "score": score,
                    "song_features": {
                        "energy": song.get("energy"),
                        "danceability": song.get("danceability"),
                        "acousticness": song.get("acousticness"),
                        "popularity_0_100": song.get("popularity_0_100"),
                        "release_decade": song.get("release_decade"),
                        "mood_tags": song.get("mood_tags", ""),
                        "instrumentalness": song.get("instrumentalness"),
                        "lyrical_density": song.get("lyrical_density"),
                        "explicitness": song.get("explicitness"),
                    },
                }
            )

        event = {
            "event_type": "recommendation",
            "event_id": event_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_preferences": user_prefs,
            "query": query,
            "mode": mode,
            "retrieved_count": len(retrieved),
            "retrieved_songs": [
                {
                    "id": r.get("id"),
                    "title": r.get("title"),
                    "artist": r.get("artist"),
                    "genre": r.get("genre"),
                    "mood": r.get("mood"),
                }
                for r in retrieved
            ],
            "final_recommendations_count": len(normalized_final_recommendations),
            "final_recommendations": normalized_final_recommendations,
            "confidence": confidence,
            "error": error,
            "decision_trace": decision_trace or [],
        }
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
        return event_id

    def log_feedback(
        self,
        recommendation_event_id: str,
        song_id: Optional[int],
        feedback: str,
        rank: Optional[int] = None,
        score: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log explicit user feedback linked to a prior recommendation event."""
        event = {
            "event_type": "feedback",
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "recommendation_event_id": recommendation_event_id,
            "song_id": song_id,
            "feedback": str(feedback or "").strip().lower(),
            "rank": rank,
            "score": score,
            "metadata": metadata or {},
        }
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    
    def read_logs(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Read logged events from the JSONL file."""
        events = []
        if not os.path.exists(self.log_file):
            return events
        
        with open(self.log_file, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if limit and i >= limit:
                    break
                try:
                    event = json.loads(line.strip())
                    events.append(event)
                except json.JSONDecodeError:
                    continue
        
        return events
    
    def clear_logs(self) -> None:
        """Clear the log file."""
        if os.path.exists(self.log_file):
            os.remove(self.log_file)


# Global logger instance
_logger: Optional[RecommendationLogger] = None


def get_logger(log_file: str = DEFAULT_LOG_FILE) -> RecommendationLogger:
    """Get or create the global logger instance."""
    global _logger
    if _logger is None:
        _logger = RecommendationLogger(log_file)
    return _logger


def log_recommendation(
    user_prefs: Dict,
    query: Optional[str],
    retrieved: List[Dict],
    final_recommendations: List[Dict],
    mode: str = "balanced",
    confidence: str = "medium",
    error: Optional[str] = None,
    decision_trace: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """Convenience function to log via the global logger."""
    return get_logger().log_recommendation(
        user_prefs,
        query,
        retrieved,
        final_recommendations,
        mode,
        confidence,
        error,
        decision_trace,
    )


def log_feedback(
    recommendation_event_id: str,
    song_id: Optional[int],
    feedback: str,
    rank: Optional[int] = None,
    score: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Convenience function to log explicit feedback via the global logger."""
    get_logger().log_feedback(recommendation_event_id, song_id, feedback, rank, score, metadata)
