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
- Result (85 s): SEQ reproduced EXP-07b exactly (0 of 20 seeds differ). 15 of 20 seeds passed the filter (2 never
  learned A, 3 failed REF). On those 15: A after SEQ .533, A after INTER .683, difference +.150 (SEM .064); B after
  SEQ .900, B after INTER .767. On all 20 seeds, per arm: SEQ kept both 6, overwrote 5, one answer for all 6,
  partial 3; INTER kept both 6, overwrote 0, one answer for all 8, partial 5, and 1 seed with the same answer on all
  pairs but B not fully right.
- Verdict: INCONCLUSIVE by the pre-registered rule (+.15 is above the .10 NULL line and below the .25 SUPPORTIVE
  line). The prediction failed: A after INTER is .68, not the .85 predicted, and the one-answer collapse grew (6 to 8
  seeds) instead of shrinking. Atlas category: BOUNDARY (see the exploratory finding below).
- Exploratory, not pre-registered (computed after the run from each seed's rule, which the seed fixes before any
  data): whether a brain can hold both skills depends on which cues skill A pairs together. If A cues 0 and 1 want
  the same action, a plain sum of input weights (feature weight plus context weight) can answer all 8 cues
  correctly. That holds for 1 in 3 assignments, and 6 of the 20 seeds drew one. For the other assignments, the right
  answer flips with the context, so the brain has to combine the feature and the context (an XOR-shaped mapping).
  The split is complete in both arms: the 6 seeds with a sum-solvable rule kept both skills, with or without
  rehearsal, and none of the other 14 kept both in either arm.

## Reflection
- What it means: EXP-07b's forgetting was not the ordinary kind that rehearsal fixes. In the 6 seeds where a sum of
  input weights could hold both skills, A survived 200 moments of B with no rehearsal at all. In the other 14, the brain never held both,
  so learning B had to cost A, and rehearsal only changed how it failed: overwrites became partial answers or one
  answer for everything. Rehearsal can only protect a skill the brain is able to hold alongside the new one. At these
  default sizes and 400 reward moments, none of these brains learned the full mapping that needs the feature and the
  context combined (some got part of it). That points to a representation or learning limit, not an ordering problem. It is shown for one task shape and
  one budget, and the split is post hoc, so it needs its own registered test.
- Process: pre-registered and committed (`8ba827c`) before any data, with the per-seed filter EXP-07b's reflection
  asked for, and a built-in reproduction check (SEQ matched EXP-07b on every seed). Weakness: the primary averaged
  two kinds of rule that the seed fixes in advance, one the brain can solve with sums and one it cannot. That factor
  was knowable before data and should have been a registered split, not something found afterwards. The filter
  could not catch it, because B alone is always sum-solvable.
- Lesson: when a random assignment decides whether a task is solvable by the simplest mechanism (here, a sum of input
  weights), classify the assignments before running and report each class separately. A mean over both classes can
  look like a dose effect when it is two populations.
- Next: queued EXP-07d, registered on fresh seeds with the rule type balanced (10 sum-solvable, 10 that need the
  combination): train all 8 cues interleaved from birth for 800 moments, and ask whether the brain learns the
  combination at all. If it cannot even from birth, the limit is representational and has nothing to do with order.
