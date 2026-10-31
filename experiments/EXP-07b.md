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
- Result (41 s): A before 0.938, A after B 0.500, drop +0.438 (SEM 0.094), B after 0.825; 12 of 20 seeds lost at least
  one A answer. B at birth was 0.50 in every seed, which fits a newborn giving one action to all B cues (not checked directly).
- Verdict: FORGETTING by the pre-registered rule (drop >= 0.25 and A after <= 0.60). The prediction holds. Atlas
  category: BOUNDARY (a limit, stated with a number).
- Exploratory, not pre-registered (`exp/EXP-07b_pairs_explore.py`, same seeds and calls, it reproduces every scored
  result): after B, how often did the brain give A cue i and B cue i the same answer? The 20 seeds fall in four groups.
  - Kept both, 6 seeds: different answers on all 4 pairs, A 1.00 and B 1.00. These brains used the context feature.
  - Overwrote A with B, 5 seeds: same answer on all 4 pairs, A 0.00 and B 1.00.
  - One action for all 8 cues, 6 seeds: A 0.50 and B 0.50. Three of these (7071008, 7071013, 7071019) had A at 1.00
    before B, so B training turned a working skill into a single answer. The other three never learned A well (0.50,
    0.50, 0.75 before B), so they say nothing about forgetting.
  - Partial, 3 seeds: the same answer on 2 or 3 of the 4 pairs.

## Reflection
- What it means: when the second skill reuses the first skill's inputs and wants the opposite answer on them, 200
  moments of B with no A rehearsal cost A heavily on average. The mean hides two different failures. In 5 seeds B
  simply took over the shared features. In 3 more, a brain that had learned A ended up giving one action to every
  cue. That is a different failure, not a worse score: it gets 4 of 8 cues right, the same as an overwrite, but it
  keeps neither skill, while an overwrite at least holds B. 6 of 20 brains did keep both,
  so the network can hold the pair; it just does not reliably find that solution from sequential training.
- Process: pre-registered and committed (`1766330`) before any data; same arms, exam and rules as EXP-07, so the two
  results compare directly. Weakness: the VOID rule was set on the means, and it passed (A before .938, B after
  .825), yet 3 seeds never learned A and 6 never learned B. A per-seed learnability filter, declared in advance,
  would have kept the drop clean of seeds that had nothing to lose.
- Lesson: split a forgetting score by how the brain fails. Overwriting and collapsing to one answer both lower the
  score, but they may need different fixes (rehearsal is the usual one for overwriting; what causes the single-answer collapse is not known yet).
- Next: queued EXP-07c, the same setup with an interleaved arm (B training with A moments mixed in at a fixed ratio)
  and a per-seed learnability filter declared before data, to see whether rehearsal keeps both skills.
