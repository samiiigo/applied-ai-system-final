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

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

