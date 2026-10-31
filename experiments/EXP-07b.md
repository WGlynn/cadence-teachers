# EXP-07b: does a second skill erase the first when their inputs overlap?

- Date: 2026-10-31 | Cadence version: 0.91.3 (main `f84125e`) | Program iter: none (generic queue; per the program FRONTIER of 10-30, V(S) waits on Will-gated CAL-1 / CAL-2 / the registered zero test)
- Script: `exp/EXP-07b_overlap_forgetting.py` | Evidence: `exp/EXP-07b-f84125e.out`, `exp/EXP-07b-f84125e.json`

## Summary
- Question: EXP-07 showed no forgetting when the two skills shared no inputs. Does reward-learning skill B erase skill A
  when each B cue shares one input feature with one A cue and its right action is the opposite of that A cue's?
- Setup: `Brain.compose(inputs=6, actions=2, arousal=True)`, default sizes, 20 seeds (brain seed 7_071_000 + s, cue stream
  from `default_rng(7_071_000 + s)`). Cues are 2-hot over 6 features. Skill A: cue i = {i, 4 if i < 2 else 5} for
  i = 0..3, two cues per action, assignment permuted per seed. Skill B: cue i = {i, 5 if i < 2 else 4}, so B cue i
  shares feature i with A cue i and carries the other context feature, and its right action is the opposite of A cue i's.
  B alone is solvable from features 0 to 3; holding A and B together needs the context feature. Outcome +1 right,
  -1 wrong, given on the next `live` call. Phase A: 200 moments on random A cues. Fork with `copy.deepcopy`: LEARN-B
  gets 200 moments on random B cues (A's last outcome arrives with the first B cue); CONTROL gets nothing more. Exam
  as in EXP-07: per cue, a fresh deepcopy first receives the true outcome of the pending action, answers once, and is
  thrown away. One answer per cue, so per-seed scores move in steps of 0.25; the 20-seed means carry the test.
  Measures per seed: A before (the fork), A after B, B after B, B before B (chance check).
- Prediction (written before any data): B's lessons push the shared feature weights the opposite way, with no A
  rehearsal, so I expect clear forgetting: mean drop (A before minus A after) of at least 0.25.
  Pre-registered verdict rules, on the 20-seed means (same rules as EXP-07):
  - VOID if A before < 0.75 or B after < 0.75.
  - SUPPORTIVE (no catastrophic forgetting) if mean drop <= 0.10 and A after >= 0.75.
  - FORGETTING (prediction confirmed) if mean drop >= 0.25 or A after <= 0.60.
  - INCONCLUSIVE otherwise.
  The paired drop is reported with its SEM over seeds.
- Result: (pending)
- Verdict: (pending)

## Reflection
- (pending)
