# EXP-07d: can the brain learn the overlapping 8-cue task at all when the rule needs feature and context combined?

- Date: 2026-11-02 | Cadence version: 0.92.1 (main `a37d150`) | Program iter: none (generic queue; per the program FRONTIER of 11-01, V(S) waits on Will-gated CAL-1 / CAL-2 / the registered zero test)
- Script: `exp/EXP-07d_joint.py` | Evidence: `exp/EXP-07d-a37d150.out`, `exp/EXP-07d-a37d150.json`

## Summary
- Question: in EXP-07b and EXP-07c no brain held both skills when the rule needed a cue's feature and its context
  combined (0 of 14 seeds), while every seed whose rule a sum of input weights can solve did (6 of 6, in both arms of
  EXP-07c). That split was found after the fact, and those brains learned the skills one after the other. If all 8
  cues are trained mixed together from birth, with the rule type fixed in advance, does the brain learn the combined
  rule? If it cannot even then, the limit is in what the brain can learn here, not in the order of training.
  Why it matters: any learned policy of ours whose right answer depends on a situation and its context together
  (an encounter whose right answer changes with the context, a hook deciding from two facts) needs this kind of
  rule. A clean answer tells us whether to expect it at these sizes, or to build the combination into the inputs
  ourselves. The skeptic's way out is the budget: 1600 moments may simply be too few. The 1600-moment secondary
  answers that in part; a LIMIT at 1600 still holds only for this budget and these default sizes.
- Setup: EXP-07b's 8 cues exactly (2-hot over 6 features; A cue i = {i, 4 if i < 2 else 5}, B cue i = {i, 5 if i < 2
  else 4}, B's answer the opposite of A's). `Brain.compose(inputs=6, actions=2, arousal=True)`, default sizes, on
  Cadence 0.92.1, which the monitor found byte-identical to 0.91.3 on our probes today. 20 fresh seeds: brain seed
  7_074_000 + s, cue stream `default_rng(7_074_000 + s)`. The rule is fixed by construction, not drawn:
  - seeds 0 to 9, SUM rules (A cues 0 and 1 share an action): (0,0,1,1) for even s, (1,1,0,0) for odd s. Here the
    right answer follows the context feature alone, so a sum of input weights solves all 8 cues.
  - seeds 10 to 19, COMBINATION rules (A cues 0 and 1 differ): the four assignments (0,1,0,1), (0,1,1,0), (1,0,0,1),
    (1,0,1,0) in turn, s % 4. Each feature appears once in each context with opposite answers, two features one way
    and two the other, so no sum of input weights gets more than 6 of 8 right. The script checks this ceiling by brute
    force over integer weights before any brain runs.
  One arm: every moment draws one of the 8 cues uniformly from the stream; outcome +1 right, -1 wrong, given on the
  next `live` call; 1600 moments. Exams at 200, 400, 800 and 1600 moments, as in EXP-07: per cue, a fresh deepcopy
  first receives the true outcome of the pending action, answers once, and is thrown away (the exam does not touch the
  brain or the stream). A copy the outcome arouses answers by sampling, a calm one greedily, as in all EXP-07 runs.
  Score = fraction of the 8 cues right, in steps of 1/8.
- Prediction (written before any data): EXP-07b and EXP-07c showed 0 of 14 combination brains holding both skills
  after 400 moments, and a calm `live` moment does not learn, so I expect the combined rule mostly not to be learned:
  at 800 moments, combination mean at most 0.80 and at most 2 of 10 combination seeds at 8 of 8, with the sum seeds
  at 0.90 or more. At 1600 moments I expect at most 3 of 10 combination seeds at 8 of 8. Confidence is moderate: the
  composed brain has hidden neurons, so it could represent the mapping; the question is whether it finds it.
  Pre-registered verdict rules, at 800 moments:
  - VOID if the sum seeds' mean score is below 0.85 (the easy control did not learn, so the budget or setup is wrong).
  - LIMIT (prediction confirmed: at this budget the brain does not learn the combined rule) if the combination mean
    is at most 0.80 and at most 2 of 10 combination seeds score 8 of 8.
  - LEARNABLE (prediction refuted: the order of training was the problem) if the combination mean is at least 0.90
    or at least 7 of 10 combination seeds score 8 of 8.
  - INCONCLUSIVE otherwise.
  Reported with them: the difference sum mean minus combination mean with its SEM, and how many combination seeds
  beat the 6-of-8 ceiling of a sum of input weights (7 or 8 of 8). Registered secondary: the same rules applied at
  1600 moments (does twice the budget change the answer), and the learning curve per rule type at 200, 400, 800, 1600.
- Result: PENDING
- Verdict: PENDING

## Reflection
- PENDING
