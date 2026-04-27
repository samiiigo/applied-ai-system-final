# Reliability and Evaluation: How We Test and Improve the AI

This project uses multiple reliability checks so recommendations are measurable, auditable, and easier to improve.

## 1) Automated Tests

We use automated tests to verify core behavior in both recommendation logic and Streamlit helper functions.

- Test files:
	- `tests/test_recommender.py`
	- `tests/test_streamlit_app_helpers.py`
- Latest run result:
	- `15 out of 15 tests passed`
- What these tests cover:
	- Recommendation ranking behavior under different scoring modes
	- Diversity penalty behavior (to reduce repeated artists)
	- Explanation generation returns non-empty reasoning
	- Playlist classification and helper utility correctness
	- Input normalization for added songs and output row formatting

## 2) Confidence Scoring

The system records confidence with each recommendation event.

- Current implementation:
	- Recommendation logging includes a `confidence` field (`strong`, `medium`, `weak`), and the current app flow logs recommendations with `medium` confidence by default.
- Supporting quality signals:
	- Groundedness check: `100%` (3/3 grounded recommendations in evaluation run)
	- Retrieval recall is high (genre and mood recall each `100%` in the latest benchmark run)

This gives a baseline confidence signal, and it can be improved further by deriving confidence dynamically from score margins and retrieval evidence strength.

## 3) Logging and Error Handling

The project records recommendation events and supports fallback behavior when components fail.

- Structured logging:
	- Recommendations are written as JSONL events (event id, timestamp, user preferences, retrieved songs, final recommendations, confidence, optional error field).
	- Feedback events can also be logged and linked to prior recommendation event IDs.
- Error handling and resilience:
	- Retrieval import fallback: if retrieval helpers are unavailable, recommendation flow falls back to using full song list.
	- Evaluation execution is wrapped to avoid crashing the main app; errors are caught and reported.
	- Logger schema includes an `error` field to preserve failure context for audit/debugging.

## 4) Human Evaluation

Manual profile comparisons were used to verify recommendation quality and behavior shifts.

- Human review method:
	- Compared outputs across multiple user profiles (for example: Happy Pop, Chill Lofi, Deep Intense Rock, and an edge-case profile).
	- Checked whether ranking changes matched expected preference differences (genre, mood, and especially energy).
- Review finding:
	- Recommendations changed meaningfully when profile inputs changed, which supports that the model is responsive to user context instead of returning static lists.

## Quantitative Evaluation Snapshot

From the latest evaluation harness run (`src/evaluation.py`):

- Avg Genre Precision: `12.00%`
- Avg Genre Recall: `100.00%`
- Avg Mood Precision: `12.31%`
- Avg Mood Recall: `100.00%`
- Groundedness Score: `100.00%`

Interpretation: recall is very high (the system finds relevant categories), groundedness is strong (explanations stay tied to metadata), and precision is lower, indicating room to improve candidate filtering specificity.

## Short Testing Summary

`15 out of 15 tests passed; the system was reliable on core ranking and playlist helper functions. Confidence is currently logged at a medium level by default, while groundedness reached 100% and retrieval recall reached 100% in benchmarks. Precision was lower (~12%), so next improvements should focus on tighter filtering and dynamic confidence calibration.`

