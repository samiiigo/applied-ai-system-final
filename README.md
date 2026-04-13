# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

In my system, each song has several features that describe its vibe and style. I use things like genre, mood, energy, tempo, valence, danceability, and acousticness. These help define what kind of song it is.

My UserProfile stores the listener’s main preferences — favorite genre, favorite mood, target energy level, and whether they like acoustic music or not.

The recommender gives every song a score by checking how well it matches the user profile.

It adds points for matching genre and mood.

For numeric traits like energy or tempo, it adds more points when the song’s values are close to the user’s target so similar songs score higher.

Genre match matters the most, then mood, and the rest help fine-tune the result.

After that, all songs get ranked by their total score, and the system recommends the top few. That way, you can always see exactly why each song was suggested.

I have added 10 songs in data/songs.csv. Each song has a genre, mood, energy, tempo_bpm, valence, danceability, and acousticness.

My user profile is a small dictionary with these fields:
- favorite_genre
- favorite_mood
- target_energy
- likes_acoustic

The scoring is simple:

- +2.0 for a genre match
- +1.0 for a mood match
- up to +2.0 for energy closeness
- up to +1.0 for danceability closeness
- +0.5 if the acousticness fits what the user likes

I then rank every song by total score and return the top results.

One bias I expect is that genre can still overpower everything else if I weight it too much. That might make the system ignore songs that match the mood and energy really well.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Phase 3 CLI Verification

Latest terminal run using default profile (`genre=pop`, `mood=happy`, `energy=0.8`):

```text
Loaded songs: 10

Top recommendations:

1. Greedy by Ariana Grande
   Score   : 4.48
   Reasons :
   - genre match (+2.0)
   - energy closeness (+1.98)
   - non-acoustic preference match (+0.5)

2. Talk by DJ Khalid
   Score   : 4.16
   Reasons :
   - genre match (+2.0)
   - energy closeness (+1.66)
   - non-acoustic preference match (+0.5)

3. Yukon by Justin Bieber
   Score   : 4.06
   Reasons :
   - genre match (+2.0)
   - energy closeness (+1.56)
   - non-acoustic preference match (+0.5)
```

Screenshot placeholder (add your terminal screenshot file here):

`![Phase 3 CLI output](docs/phase3-cli-output.png)`

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

I changed the scoring so energy mattered more and genre mattered less. That made the rankings move toward songs with the right intensity, even when the genre was only a partial match. For example, the Conflicted Edge Case profile still put Passionfruit at the top because the sad mood and target energy lined up well enough to beat a pure genre match.

---

## Limitations and Risks

The biggest limitation is that the catalog is tiny, so the system can only recommend from 10 songs. Pop is also overrepresented, which gives pop listeners more chances to get a strong match than listeners who want niche styles. The system relies on exact mood labels, so it is not good at handling mixed or in-between tastes. It also leans toward high-energy tracks after the experiment, which can make the same songs show up for very different users.

---

## Phase 4 Evaluation

I tested four profiles: Happy Pop, Chill Lofi, Deep Intense Rock, and Conflicted Edge Case.

| Profile | Top Result | Quick Take |
| --- | --- | --- |
| Happy Pop | Greedy | High-energy pop songs rose to the top as expected. |
| Chill Lofi | Sincerity | Lower-energy, acoustic-friendly songs moved up. |
| Deep Intense Rock | Evil Jordan | Intense and high-energy tracks were prioritized. |
| Conflicted Edge Case | Passionfruit | Mixed preferences (pop + sad + high energy) still produced a believable top match. |

Biggest surprise: the conflicted profile still gave a sensible top song, which shows the scorer can combine competing signals instead of following just one preference.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this

---

## 7. `model_card_template.md`

The model card template is no longer needed now that the evaluation and reflection sections are filled in.

