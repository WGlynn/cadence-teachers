# EXP-07c: does rehearsal keep both skills when their inputs overlap?

- Date: 2026-11-01 | Cadence version: 0.91.3 (main `f84125e`) | Program iter: none (generic queue; per the program FRONTIER of 10-31, V(S) waits on Will-gated CAL-1 / CAL-2 / the registered zero test)
- Script: `exp/EXP-07c_rehearsal.py` | Evidence: `exp/EXP-07c-f84125e.out`, `exp/EXP-07c-f84125e.json`

## Summary
- Question: in EXP-07b, 200 moments of skill B with no A practice took A from .94 to .50. If one moment in four
  during B training is an A moment instead, does the brain keep both skills? The answer says whether a brain that
  must hold two overlapping skills (the creature's season changes, any multi-skill policy) needs old practice
  replayed, and whether the one-answer collapse seen in EXP-07b is a separate problem.
- Setup: EXP-07b's task and seeds exactly: `Brain.compose(inputs=6, actions=2, arousal=True)`, default sizes, 20 seeds
  (brain seed 7_071_000 + s, cue stream from `default_rng(7_071_000 + s)`), 2-hot cues over 6 features, B cue i shares
  feature i with A cue i, carries the other context feature, and wants the opposite action. Phase A is 200 moments
  on random A cues, the same calls as EXP-07b. Then three arms:
  - SEQ: fork with `copy.deepcopy`, 200 moments on B cues, continuing the cue stream. This repeats EXP-07b's LEARN-B
    call for call, so its scores must match EXP-07b's per seed.
  - INTER: fork from the same point with a copy of the cue stream's state, 200 moments drawing the same cue index
    sequence as SEQ, but moment k is A cue i when k % 4 == 3 and B cue i otherwise (150 B moments, 50 A moments).
  - REF: a fresh brain with the same seed, 200 moments on B cues only, using a copy of the stream state at the fork.
    It is used only to ask whether B is learnable for that seed.
  Exam as in EXP-07 and EXP-07b: per cue, a fresh deepcopy first receives the true outcome of the pending action,
  answers once, and is thrown away. Measures per seed and arm: A score, B score, and the 8 answers.
- Learnability filter (declared before data, the fix the EXP-07b reflection asked for): a seed counts toward the
  primary comparison only if A before >= 0.75 and REF's B score >= 0.75. Both inputs are fixed before the arms
  diverge (A before) or come from a separate brain (REF), so the filter cannot favour either arm.
- Prediction (written before any data): rehearsal (mixing old-task practice into new-task training) prevents most
  of this kind of overwrite in neural nets, and interleaved replay is also the standard account of how brains avoid
  it (McClelland, McNaughton and O'Reilly 1995), so I expect A after INTER to be at least 0.85 on filtered seeds, at least 0.30 above SEQ, with B after
  INTER still at least 0.75 despite 50 fewer B moments. The one-answer-for-all-cues collapse has an unknown cause, so
  I expect it to shrink but not vanish (at least 1 seed in INTER).
  Pre-registered verdict rules, on the means over filtered seeds:
  - VOID if fewer than 8 seeds pass the filter, or if SEQ does not reproduce EXP-07b's per-seed A after and B after.
  - SUPPORTIVE (rehearsal keeps both) if A after INTER minus A after SEQ >= 0.25, A after INTER >= 0.75 and
    B after INTER >= 0.75.
  - NULL (rehearsal does not rescue A) if A after INTER minus A after SEQ <= 0.10.
  - INCONCLUSIVE otherwise.
  The paired difference is reported with its SEM over filtered seeds. Registered secondary, on all 20 seeds, per arm:
  how many seeds keep both (different answers on all 4 pairs), overwrite (same answer on all 4 pairs, B correct),
  collapse (one action for all 8 cues), or are partial, counted the same way as EXP-07b's exploratory split.
- Result: (pending)
- Verdict: (pending)

## Reflection
- (pending)
