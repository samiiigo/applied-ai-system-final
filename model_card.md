# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

VibeFinder Lite

---

## 2. Intended Use

This recommender suggests songs from a small classroom catalog based on a listener’s genre, mood, and energy preferences. It is designed for learning and evaluation, not for real users. The system assumes a user can describe their taste in a few simple labels and a target energy level.

---

## 3. How the Model Works

Each song is described by genre, mood, energy, danceability, and acousticness. The recommender compares those features to the user’s preferences and gives points for matches. Genre and mood get exact-match credit, energy gets the largest numeric score because close energy usually matters most, danceability can help if the user provides a target, and acousticness adds a small bonus when it matches the user’s style. I shifted the experiment to make energy matter more and genre matter less so I could see how sensitive the ranking was.

---

## 4. Data

The catalog contains 10 songs in `data/songs.csv`. It includes pop, R&B, hip-hop, rap, electronic, and indie songs, with moods such as happy, chill, sad, intense, and peaceful. I did not add or remove songs. The dataset is small and uneven, so it does not cover every taste equally and it does not represent many subgenres.

---

## 5. Strengths

The system works well for users whose preferences are clear and direct. Happy pop users get obvious pop matches near the top, and acoustic-friendly chill users tend to get softer songs with similar energy. The explanations also make sense to a non-programmer because each score can be traced back to a few simple reasons.

---

## 6. Limitations and Bias

The biggest weakness is the tiny catalog, which limits variety no matter what the user wants. Pop is overrepresented, so pop listeners have more chances to get a strong match than users with niche tastes. The recommender also depends on exact mood labels, which makes it rigid for users whose taste is more mixed or emotional than a single word. After the weight shift, energy became even more dominant, so songs with the right intensity can stay high even when genre is only a partial fit. That creates a bias toward high-energy songs and can make the same tracks appear for very different users.

---

## 7. Evaluation

I tested four profiles: Happy Pop, Chill Lofi, Deep Intense Rock, and Conflicted Edge Case. I reviewed the top 5 songs for each profile and checked whether the explanation lines matched the preferences I gave. Happy Pop mostly returned pop songs with high energy, while Chill Lofi moved to softer tracks led by Sincerity, which matched my intuition. Deep Intense Rock promoted Evil Jordan to the top because it matched both intense mood and high energy. The most surprising result was Conflicted Edge Case: even with mixed signals (pop, sad, high energy), Passionfruit ranked first because it satisfied mood and genre together and still stayed close enough on energy. This showed that the model can combine conflicting preferences, but it also confirmed that changing one weight can quickly shift which songs dominate.

---

## 8. Future Work

I would add more songs so the recommender has a better chance of making diverse choices. I would also consider soft ranges for mood instead of exact label matches, because real listeners often want something between two vibes. A better diversity rule could keep the top five from all being near-duplicates in energy or genre. I would also improve the explanations so they mention tradeoffs instead of only listing the matched features.

---

## 9. Personal Reflection

This project made recommender systems feel more transparent to me because the ranking comes from a small set of rules that I can inspect directly. I also noticed how easy it is for a simple weight change to reshape the whole list. That made it clear why real recommendation systems need careful testing for bias, not just good-looking top results.
