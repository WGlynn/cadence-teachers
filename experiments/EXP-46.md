# EXP-46: does 0.83's episodic memory make the default brain learn the Stone Age chain, read state by state?

- Date: 2026-10-13 | Cadence version: 0.83.0 (`23dba71`) | Program iter: none (teaching track; Will 13:46: "highest value target is to test it for Bernhard")
- Script: `exp/EXP-46_episodic_memory_stone_age.py` | Evidence: `exp/EXP-46-pilot.*`, `exp/EXP-46-full.json/.jsonl/.out` (PENDING)

## Summary
- Question: Cadence 0.83 adds an opt-in episodic memory (`Brain.compose(memory_choice=True)`). Upstream reports, on its own four-step crafting chain, frozen full-chain success 38.1% -> 98.7% with a caregiver, 9.0% -> 97.8% after 80 episodes alone through `live`, 9.1% -> 73.2% from reward alone. EXP-45 showed that on Stone Age V5's chamber full-chain success is mostly in-attempt search (a no-knowledge never-repeat searcher gets .304) and that the default brain learns the chain from no signal (per-state greedy accuracy .33-.42). Does the memory change that on this outside chamber, state by state?
- Setup: EXP-45's replica of V5's chamber (reproduces V5's published per-seed numbers). Brain = the current default composition, `Brain.compose(7, 5, modules=(48, 24), arousal=True)`, with and without `memory_choice=True` (its own defaults, nothing tuned). Signals: natural (world reward only), grade-v5 (V5's guided +-.5), corrective (V5's caregiver labels on executed mistakes). 120 teaching attempts, then 80 attempts alone through `live` with world reward only. Readings on frozen copies after teaching and after the 80 alone: per-state greedy accuracy (primary), greedy full-chain, sampled full-chain over 100 attempts. Seeds 42-53.
- RUN GATE: (1) prediction below, written before the pilot. (2) Window: a 3-seed pilot at the exact run conditions; a 1-seed 10-attempt smoke run was seen (code check only: memory/corrective all four states right, without memory .25). If the pilot puts every memory arm at the ceiling, the full run keeps the design (the claim under test is a ceiling claim) and the write-up says the budget cannot rank memory arms. (3) Variance: seeds vary; arms differ only in memory and signal. (4) Metric: per-state greedy accuracy is primary; full-chain is read against the never-repeat searcher (.304). (5) Chain: train success -> taught acc -> taught sampled -> alone train success -> after acc -> after sampled.
- Prediction (written before the pilot):
  - Check, not a prediction: without memory, corrective on V5's seeds 42-46 lands on upstream's published 0.82 figure for V5 (26.4% sampled), since 0.83 without memory builds the 0.82 composition and the replica reproduced V5 on 0.81.
  - (P1) corrective + memory: per-state greedy accuracy >= .9 (mean) and sampled full-chain >= .9 after teaching (upstream 98.7%).
  - (P2) natural + memory: per-state greedy accuracy >= .75 and sampled full-chain above the never-repeat searcher (.304) after teaching (upstream 73.2%).
  - (P3) after 80 alone through `live`, every memory arm keeps per-state accuracy within .1 of its taught value (upstream 97.8%).
  - (P4) grade-v5 + memory: per-state greedy accuracy >= .75 (the memory makes V5's diluted grade usable on the default brain).
  - (P5) without memory, every signal stays at per-state accuracy <= .5 after teaching (EXP-45's default-brain result carries to the 0.82 composition).
- Decision rule (written before the pilot): P1-P3 hold -> upstream's 0.83 claim replicates on an outside chamber with the per-state instrument, and memory turns search into a learned chain; sampled high but per-state accuracy low -> the memory helps search, not the mapping; P5 fails -> the 0.82 composition alone already fixed part of it, and the memory gain is read against that.
- Result: PENDING. Verdict: PENDING.

## Reflection
- PENDING (after the run).
