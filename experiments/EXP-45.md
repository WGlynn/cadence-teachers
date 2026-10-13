# EXP-45: the Stone Age chain, grade vs brain (why grading worked for us and not in V5), and search inside an attempt

- Date: 2026-10-13 | Cadence version: 0.83.0 (`23dba71`), both brains on the 0.81 composition (working_memory_scale 12, decay 0.2) | Program iter: none (teaching track; spawned by Will forwarding Stone Age V5)
- Script: `exp/EXP-45_stone_age_2x2.py` | Evidence: `exp/EXP-45-pilot.json/.jsonl`, `exp/EXP-45-full.json/.jsonl/.out` (PENDING)

## Summary
- Question: EXP-39 (ours, 0.80) solved the 4-step Stone Age chain 12/12 by grading every move; Stone Age V5 (ali12mahmood12345-boop/cadence-stone-age, 0.81) reports grade_only at 0.2% and a corrective teacher at 18.8%. Is the difference the grade (V5's is a third as dense, half the size, added to a bigger end reward) or the brain (V5 uses Cadence defaults with arousal; ours is a tuned delayed-credit point)? And is V5's in-sequence success a learned chain, or search inside an attempt (a wrong action costs nothing but a decision, and a no-knowledge never-repeat searcher finishes 30.4%)?
- Setup: V5's COLD chamber re-implemented in our code (theirs read, not run; replica checked: uniform random through it .122 vs exact .121). 2 brains (ours = key-door protocol-3 point; v5 = compose defaults (48, 24) + arousal) x 4 signals (natural, grade-v5, grade-dense, corrective), one continuing life of 120 attempts (V5's budget), V5's event order. Readings on frozen copies: per-state greedy accuracy; greedy full-chain; sampled full-chain over 100 attempts (V5's headline); the same with the carried context erased before every decision (`working_memory.reset(1)`); and the success a memoryless policy with the measured per-state p(right) would have. Seeds 42-53 (V5 used 42-46).
- RUN GATE: (1) prediction below, written before the pilot. (2) Window: pilot of 3 seeds at the exact run conditions (120 attempts) before the full run; if a factor's effect is at floor or ceiling for a reason unrelated to the question, the budget changes before the full run and that change is written here first. (3) Variance: seeds vary; arms differ only in brain or signal. (4) Metric: per-state greedy accuracy is primary for "learned the chain" (search cannot pass it); sampled full-chain is V5's reading and is read against the never-repeat searcher (.304), not against uniform random (.121). (5) Chain per run: train success -> p(right) per state -> greedy accuracy -> sampled / erased / memoryless.
- Prediction (written before the pilot):
  - Check, not a prediction: v5/corrective lands in V5's band (sampled 10-30%, greedy accuracy below 1 in most seeds), so the replica reproduces their regime.
  - (P1) ours/grade-dense gets all 4 states right in >= 10 of 12 seeds (EXP-39 carries to V5's chamber: WAIT added, strict order, 10 decisions).
  - (P2) v5/grade-v5 stays at sampled <= .05 (V5's 0.2% reproduces).
  - (P3) The brain is the bigger factor: ours/grade-v5 mean greedy accuracy >= .75 while v5/grade-dense mean greedy accuracy < .5.
  - (P4) Search: in v5/corrective, sampled exceeds the memoryless prediction by >= .05, and erasing the carried context before each decision closes at least half of that gap.
  - (P5) No v5-brain arm beats the never-repeat searcher (.304) on sampled full-chain success.
- Decision rule (written before the pilot): P3 holds -> V5's grade_only failed on the operating point (actor step 1.0, critic .3, arousal), so the advice to V5 is "tune the brain, keep the grade"; the reverse (v5/grade-dense high, ours/grade-v5 low) -> the diluted grade is the cause; both low off-diagonal -> they interact and both changes are needed. P4 holds -> V5's full-chain number measures in-attempt search through the carried context, and per-state accuracy should be reported beside it.
- Result: PENDING. Verdict: PENDING.

## Reflection
- PENDING (after the run).
