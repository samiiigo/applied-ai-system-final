# System Architecture

```mermaid
flowchart LR
  U[User: profile + preferences + optional new songs] --> UI[Streamlit UI / CLI]
  D[(songs.json library)] --> UI

  UI --> R[Retriever\nmetadata candidate search]
  R --> A[Recommendation Agent\nranker + diversity penalty + explanations]
  A --> O[Outputs\nTop-K recommendations + explanations]
  O --> L[(recommendations.jsonl logs)]

  O --> H[Human-in-the-loop\nLike / Skip feedback in UI]
  H --> L

  T[Pytest test suite\nunit/helper tests] --> C[Quality gate]
  E[Evaluator\nretrieval metrics + groundedness checks] --> C
  C --> A
```

## Flow Summary

1. Input: user preferences and song library enter via UI or CLI.
2. Process: retriever narrows candidates, then recommendation logic ranks and explains results.
3. Output: recommendations are shown and logged.
4. Human check: users rate recommendations (like/skip), and feedback is logged.
5. Automated checks: evaluator and tests verify retrieval quality, groundedness, and helper logic.
