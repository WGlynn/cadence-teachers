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
  (an encounter whose right answer changes with the context, a hook deciding from two facts) is a rule of this kind. A clean answer tells us whether to expect it at these sizes, or to build the combination into the inputs
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
- Result (151 s): the brute-force check gave the ceilings expected, 8 of 8 for the sum rules and 6 of 8 for the
  combination rules. At 800 moments the sum seeds scored 1.000 (all 10 at 8 of 8, already at 200 moments) and the
  combination seeds 0.525: 0 of these 10 seeds at 8 of 8 or above the 6-of-8 ceiling, difference +0.475 (SEM
  0.031). 7 of the 10 combination brains gave one action to every cue on that exam. At 1600 moments: combination
  0.537, again 0 of 10 above 6 of 8, 6 of 10 on one answer. Over the whole curve (200, 400, 800, 1600) the combination mean stayed between 0.52 and 0.57, and
  the best single combination score at any exam was 6 of 8 (5 of the 40 combination exams, by 3 seeds: 7074012 at 800
  and 1600, 7074017 at 1600, 7074018 at 200 and 400).
- Verdict: LIMIT by the pre-registered rule at 800 moments, and LIMIT again at 1600 (registered secondary). The
  prediction holds, more strongly than written: I predicted a mean of at most 0.80, and the brains did not even reach
  the 0.75 that a sum of input weights allows. Atlas category: BOUNDARY.

## Reflection
- What it means: the split EXP-07c found after the fact replicates on fresh seeds with the rule type fixed in
  advance. Trained on all 8 cues mixed from birth, the default composed brain learns the rule that follows the context
  alone at once, and does not learn the rule that needs a feature and its context together, in 1600 reward moments.
  It does not even find the best partial answer (6 of 8, which a sum of input weights gets): most combination brains
  end on one action for everything, which is right half the time. So the forgetting seen in EXP-07b was mostly this
  limit, not an effect of training order. What it does not show: whether a larger brain, another budget beyond 1600,
  or a different learning path would learn it. The composed brain has hidden neurons, so the mapping is not ruled
  out by its shape; this is what these defaults find through `live`, not what the network could hold.
- Process: pre-registered and pushed (`3d47707`) before any data, with the rule type fixed by construction (the fix
  EXP-07c's reflection asked for) and the linear ceiling computed before the run, which turned a vague "learned it or
  not" into a hard line: a score above 6 of 8 means the brain combined the inputs. (The line is exact for greedy
  answers; an exam copy the outcome arouses samples, so one lucky draw could add a cue. No exam crossed it.) Weakness: the sum rules in this
  task follow the context feature alone, so the control is easier than "solvable by a sum" in general; a control rule
  needing several weights summed would separate "needs a combination" from "needs more than one input". The collapse to
  one answer has no tested cause here.
- Lesson: when a task has a simple-mechanism ceiling (here, the best a sum of input weights can do), compute it by
  brute force before the run and register "beats the ceiling" as the test. A null then says the brain stayed inside
  the simple mechanism, and a pass says it went beyond it, instead of a score with no reference point.
- Next: queued EXP-07e, to locate the limit: the same 10 combination rules with arms that change one thing each (the
  conjunction given as its own input, so a sum can solve it; a larger brain; training that learns on every moment
  instead of only when aroused). For our own use: a learned policy at these defaults should be handed the
  situation-and-context combination as an input, not expected to find it.
