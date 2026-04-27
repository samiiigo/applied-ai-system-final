# Model Card: Playlist Chaos Recommender

## Base Project and Version
- Base project from Modules 1-3: Music Recommender Simulation
- Current project name: Playlist Chaos
- Version: 1.0 (rule-based recommender with retrieval, ranking, and explanation)

## Model Goal and Scope
This system recommends songs from a local catalog using user preferences such as genre, mood, and target energy.
It is designed for learning and demonstration of applied AI systems, not for commercial-scale personalization.

## Data and Features
- Primary catalog file: src/data/songs.json
- Core fields used in scoring: genre, mood, energy, danceability, acousticness, popularity, and mood tags
- Additional metadata used for transparency and filtering: artist, tempo, valence, release decade, explicitness

Data limitations:
- The catalog is still relatively small compared to real-world music services.
- Genre and mood coverage are uneven, which can bias outcomes toward better-represented categories.
- Metadata quality depends on manual curation assumptions in the dataset.

## Algorithm Summary
The recommender uses a transparent multi-step process:
1. Retrieve: select candidate songs from metadata relevance.
2. Rank: compute weighted compatibility scores using preference alignment.
3. Diversify: apply penalties to reduce repetitive outputs.
4. Explain: generate grounded reason strings from known metadata fields.

This is intentionally rule-based so behavior can be inspected, tuned, and tested.

## AI Collaboration Reflection
AI tools were used as a development assistant for drafting documentation structure, suggesting edge-case tests, and refining explanation text.

How I used AI responsibly:
1. I treated AI output as a draft, not final truth.
2. I validated suggestions by running tests and checking actual runtime behavior.
3. I kept scoring logic decisions human-controlled and traceable.

What AI did not replace:
1. Final design choices for scoring trade-offs.
2. Manual review of failure cases and bias risks.
3. Interpretation of evaluation results.

## Biases, Risks, and Ethical Considerations
Observed biases and risks:
1. Catalog bias: overrepresented styles can dominate recommendations.
2. Feature-weight bias: high energy alignment can overpower other preference signals.
3. Mood rigidity: categorical mood matching can miss nuanced emotional intent.

Potential impact:
1. Users with niche tastes may receive weaker matches.
2. Recommendations can look confident despite limited data breadth.

Mitigations currently implemented:
1. Diversity-aware ranking to reduce repetitive recommendations.
2. Explanation strings so users can inspect why songs were selected.
3. Evaluation checks for groundedness to reduce unsupported explanation claims.

## Testing and Evaluation Results
Testing approach:
1. Automated unit tests for scoring behavior, ranking modes, and helper utilities.
2. Streamlit helper tests for playlist/search/stat formatting logic.
3. Evaluation harness for retrieval quality and explanation groundedness.

Reported results:
- 15/15 automated tests passed.
- Benchmark recall reached 100% across selected queries.
- Groundedness checks reported 100% on sampled outputs.
- Precision remained lower than recall on mixed queries, indicating room to tighten ranking specificity.

## Intended and Non-Intended Use
Intended use:
1. Applied AI coursework demonstrations.
2. Explainable recommender prototyping.
3. Small-scale experimentation with human feedback logging.

Non-intended use:
1. Production music recommendation systems.
2. High-stakes personalization decisions.
3. Any setting that requires fairness guarantees across broad populations.

## Known Limitations
1. Limited catalog size and representational imbalance.
2. No learned personalization from long-term user history.
3. Evaluation set is small and may not cover all profile types.

## Improvement Roadmap
1. Expand and rebalance the catalog across genres, moods, and eras.
2. Add softer similarity metrics for mood and context.
3. Introduce feedback-informed weight adaptation.
4. Add fairness-oriented slice evaluations by profile type.

## Final Reflection
The most important takeaway is that trustworthy AI behavior came from the whole system loop, not one scoring formula. Combining transparent rules, explicit explanations, feedback logging, and testing made it easier to detect weak spots and iterate responsibly.
