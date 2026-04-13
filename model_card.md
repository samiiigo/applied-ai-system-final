# Model Card: Music Recommender Simulation

## Model Name

VibeFinder Lite 1.0

## Goal / Task

This model suggests songs for a user based on their taste profile.
It tries to rank songs that best match preferred genre, mood, and energy.

## Data Used

The dataset has 10 songs in `data/songs.csv`.
Each song includes genre, mood, energy, tempo, valence, danceability, and acousticness.
The catalog is small and not balanced across all genres.
Pop-style songs appear more often than niche styles.

## Algorithm Summary

The model gives each song a compatibility score.
It adds points for exact genre and mood matches.
It adds the most points when song energy is close to the user's target energy.
It can also add points for danceability closeness (if provided) and for acoustic vs non-acoustic preference.
Songs are sorted by total score, and the top results are returned.

## Observed Behavior / Biases

The recommender is very sensitive to energy because energy has the largest weight.
This can push high-energy songs up, even if genre is only a partial fit.
The small dataset also creates catalog bias.
Since pop songs are overrepresented, pop listeners often get stronger matches.
Exact mood matching is rigid and may miss "in-between" moods.

## Evaluation Process

I tested four profiles: Happy Pop, Chill Lofi, Deep Intense Rock, and Conflicted Edge Case.
For each profile, I reviewed the top 5 songs and explanation strings.
I compared whether top songs matched the profile's genre, mood, and energy goals.
I also compared rankings before and after weight tuning to see how behavior changed.

## Intended Use and Non-Intended Use

Intended use: classroom learning, demos, and basic recommender experiments.
It is useful for showing how simple scoring rules produce recommendations.

Non-intended use: real music product decisions, personalized mental health support, or high-stakes profiling.
It should not be used as a production recommender because the dataset is tiny and biased.

## Ideas for Improvement

1. Expand the song catalog to improve coverage and fairness.
2. Replace exact mood matches with soft similarity across related moods.
3. Add a diversity rule so the top results are less repetitive.

## Personal Reflection

My biggest learning moment was seeing how one weight change can reshape the whole ranking.
A small scoring rule can create large behavior shifts.

AI tools helped me move faster when drafting tests, explanations, and documentation.
I still had to double-check outputs against the actual code and run behavior.

I was surprised that a simple weighted formula can still feel like a "real" recommender.
Even basic feature matching can produce believable top picks.

If I extend this project, I want to add more data, test for fairness across profiles, and try hybrid scoring (rules + similarity learning).
