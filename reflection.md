# Reflection Notes

I tested four profiles: Happy Pop, Chill Lofi, Deep Intense Rock, and a Conflicted Edge Case.

- Happy Pop vs Chill Lofi: Happy Pop ranked Greedy, Talk, and Yukon near the top, while Chill Lofi shifted to Sincerity first and included more mellow songs. The output changed from upbeat pop to softer tracks because the second profile asked for peaceful mood, lower energy, and acoustic preference.

- Happy Pop vs Deep Intense Rock: Happy Pop favored pop songs, but Deep Intense Rock moved Evil Jordan to rank 1 and pulled in other high-energy songs. This makes sense because the intense profile targets very high energy and an intense mood, so energetic rap-style songs gain points quickly.

- Happy Pop vs Conflicted Edge Case: Happy Pop starts with confident, high-energy pop, while Conflicted Edge Case puts Passionfruit at the top and keeps pop songs behind it. That change is reasonable because the conflicted profile adds sad mood and acoustic preference, so the model rewards emotional match even when the user still likes pop.

- Chill Lofi vs Deep Intense Rock: Chill Lofi promotes calm songs like Sincerity and other lower-energy options, while Deep Intense Rock promotes Evil Jordan, Greedy, and other higher-energy songs. The large shift makes sense because these profiles ask for opposite energy ranges and different mood labels.

- Chill Lofi vs Conflicted Edge Case: Both profiles can include songs with some acoustic value, but Chill Lofi keeps peaceful low-energy songs higher and Conflicted Edge Case keeps more pop songs in the list. This is expected because one profile is calm and acoustic-first, while the other mixes sadness with high energy and pop.

- Deep Intense Rock vs Conflicted Edge Case: Deep Intense Rock strongly prioritizes Evil Jordan and similar high-intensity tracks, while Conflicted Edge Case allows Passionfruit to beat pure intensity matches. That result makes sense because the conflicted profile blends pop and sad mood with high energy, so songs that balance mood and genre can outrank the hardest tracks.

The main thing I learned is that the same scoring rules can give very different lists when I change just one preference, especially when energy has a bigger weight. This tells me my system really reacts to small changes in the user profile.