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
from datetime import datetime
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
    ) -> None:
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
        event = {
            "timestamp": datetime.utcnow().isoformat(),
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
            "final_recommendations_count": len(final_recommendations),
            "final_recommendations": [
                {
                    "id": r.get("id") if isinstance(r, dict) else r[0].get("id") if isinstance(r[0], dict) else None,
                    "title": r.get("title") if isinstance(r, dict) else r[0].get("title") if isinstance(r[0], dict) else None,
                    "artist": r.get("artist") if isinstance(r, dict) else r[0].get("artist") if isinstance(r[0], dict) else None,
                    "score": r.get("score") if isinstance(r, dict) else (r[1] if len(r) > 1 else None),
                }
                for r in final_recommendations
            ],
            "confidence": confidence,
            "error": error,
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
) -> None:
    """Convenience function to log via the global logger."""
    get_logger().log_recommendation(user_prefs, query, retrieved, final_recommendations, mode, confidence, error)
