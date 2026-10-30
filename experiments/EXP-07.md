# EXP-07: does learning a second, unrelated skill erase the first?

- Date: 2026-10-30 | Cadence version: 0.91.2 (main `2062eda`) | Program iter: none (generic queue; per the program FRONTIER of 10-29, V(S) waits on Will-gated CAL-1 / CAL-2 / the registered zero test)
- Script: `exp/EXP-07_forgetting.py` | Evidence: `exp/EXP-07-2062eda.out`, `exp/EXP-07-2062eda.json`

## Summary
- Question: after a reward-learned skill A, does reward-learning an unrelated skill B on new cues wipe out A?
- Setup: `Brain.compose(inputs=8, actions=2, arousal=True)`, default sizes, 20 seeds (brain seed 7_070_000 + s,
  cue stream from `default_rng(7_070_000 + s)`). Skill A: cues 0 to 3, each with a right action (two cues per action,
  assignment permuted per seed). Skill B: cues 4 to 7, its own permuted assignment, independent of A. Outcome +1 right,
  -1 wrong, given on the next `live` call. Phase A: 200 moments on random A cues. Then fork with `copy.deepcopy`:
  arm LEARN-B gets 200 moments on random B cues (A's last outcome arrives with the first B cue); arm CONTROL gets
  nothing more. Exam: for each cue, a fresh deepcopy first receives the true outcome of the brain's pending action
  (as the next real moment would; no made-up 0 outcome), then answers once; the copy is thrown away.
  Known limit: one answer per cue, so each seed's score moves in steps of 0.25; the 20-seed mean carries the test.
  Measures per seed: A before (the fork, which equals CONTROL), A after B, B after B, B before B (chance check).
- Prediction (written before any data): inputs are one-hot, so A and B share no input weights, only the hidden and
  output layers. I expect little forgetting: mean A after B within 0.10 of A before.
  Pre-registered verdict rules, on the 20-seed means:
  - VOID if A before < 0.75 or B after < 0.75 (a skill was not acquired, so there was nothing to forget or no
    real second learning).
  - SUPPORTIVE (no catastrophic forgetting) if mean drop (A before minus A after) <= 0.10 and A after >= 0.75.
  - FORGETTING (prediction refuted) if mean drop >= 0.25 or A after <= 0.60.
  - INCONCLUSIVE otherwise.
  The paired drop is reported with its SEM over seeds.
- Result (40 s): A before 1.000, A after B 1.000, drop +0.000 (SEM 0.000), B after 1.000; 0 of 20 seeds lost any A
  answer. Every brain started B at chance (B at birth 0.25 to 0.75, mean 0.50) and learned all four B cues.
- Verdict: SUPPORTIVE by the pre-registered rule (drop <= 0.10, A after >= 0.75). It is a ceiling result: see Reflection.

## Reflection
- What it means: on this task, reward-learning a second skill on new cues left the first untouched in every seed.
  That rules out catastrophic forgetting in the easiest case only. The cues are one-hot, so A and B share no input
  weights, and every score sat at 1.00, so the test could see total forgetting but not partial interference. It says
  nothing yet about skills whose inputs overlap, which is where forgetting usually shows. It is about reward learning
  through `live`, not lessons, so it does not speak to upstream's open issue on taught types coexisting (#238).
- Process: pre-registered and committed (`7f362fb`) before any data; the exam gives each copy the true pending outcome
  instead of a made-up 0. Weakness: the effect window was at ceiling (both skills learned perfectly in 200 moments),
  so the prediction was never at risk; I should have picked a task where A sits below 1.00 or the inputs overlap.
- Lesson: a retention test needs room to fall. Pick a task where the first skill is learned well but not perfectly,
  or where the second skill reuses the first skill's inputs, otherwise a pass is guaranteed by the design.
- Next: queued EXP-07b, overlapping inputs: cues as 2-hot codes over 6 features where each B cue shares a feature
  with an A cue and wants the opposite action, with the same arms and rules.
