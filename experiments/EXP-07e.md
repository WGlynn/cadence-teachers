# EXP-07e: where is EXP-07d's limit, the inputs, the brain's size, learning only when aroused, or the actor's step?

- Date: 2026-11-03 | Cadence version: 0.93.0 (main `720c5a9`) | Program iter: none (generic queue; the program FRONTIER of 11-02 says V(S) waits on Will-gated CAL-1 / CAL-2 / the registered zero test)
- Script: `exp/EXP-07e_locate.py` | Evidence: `exp/EXP-07e-720c5a9.out`, `exp/EXP-07e-720c5a9.json`

## Summary
- Question: EXP-07d found that a default composed brain trained through `live` does not learn a rule that needs
  a cue's feature and its context combined (0 of 10 seeds above the 6 of 8 a sum of input weights allows, 7 of 10
  on one answer for every cue). Which single change, if any, lifts that on this task: handing the combination in
  as its own input, a larger brain, learning on every moment, or a slower actor? (More than one may; none may.) Why it matters: it tells us what a learned policy
  of ours must be given to hold a rule whose right answer depends on a situation and its context together. If one
  setting lifts it, such rules become learnable from reward at default sizes without hand-built inputs, on this
  8-cue, 2-action task in 1600 moments; the skeptic's fair objection is that our real policies are larger, so a
  pass here is necessary, not sufficient.
- Setup: EXP-07b's 8 cues (2-hot over 6 features; A cue i = {i, 4 if i < 2 else 5}, B cue i = {i, 5 if i < 2
  else 4}, B's answer the opposite of A's). Every seed gets a COMBINATION rule, EXP-07d's four in turn (s % 4),
  so no sum of the 6 inputs gets more than 6 of 8 (checked by brute force in the script). 10 fresh seeds
  (brain seed 7_075_000 + s, cue stream `default_rng(7_075_000 + s)`, the same stream in every arm), 1600
  moments, outcome +1 right / -1 wrong given with the next moment, Cadence 0.93.0. Five arms, each changing one
  thing against the control:
  - A0 control: `Brain.compose(inputs=6, actions=2, arousal=True)`, trained through `live` (EXP-07d's arm on
    fresh seeds and on 0.93.0).
  - A inputs: the 6 inputs plus a one-hot of the cue (14 inputs), so a sum of input weights can solve all 8
    (positive control for the inputs).
  - B size: `modules=(256,)`, four times the default association population of 64.
  - C step: trained through `step`, which learns on every moment, instead of `live`, which learns only when
    aroused.
  - D recipe: `actor_eta=0.1, actor_eta_bias=0.01, memory_choice=True`, through `live` (the 0.93.0 CHANGELOG,
    #208/#209: taught by terminal reward alone this learns a cue-dependent answer on 11 of 12 fresh founders,
    the composed founder on 2 of 12; the founder's reward update moves the preference 40 times more along the
    association activity both cues share than along the cue).
  Exam at 400, 800 and 1600 moments: per cue, a fresh deepcopy answers with `act(greedy=True)`; the exam does
  not touch the brain or the stream. This differs from EXP-07d, whose exam let an aroused copy sample, so A0
  re-measures the control under this exam. Greedy answers make the ceiling exact: 7 or 8 of 8 means the brain
  combined the inputs. Score = fraction of the 8 cues right.
- Prediction (written before any data): `docs/reward.md` says that with signed outcomes the composed actor rate of
  1.0 "walks the policy to one held action; a tenth of it ... lets the cue decide", and #208/#209 put the drag on
  the activity the cues share. So I expect the actor's step to be the limit, not the inputs or the size: A0 FAILS
  (at most 2 of 10 seeds above 6/8), A not LEARNS (the shared features still drag every cue's preference, so at
  most 6 of 10), B FAILS, C at most PARTIAL, D LEARNS (at least 7 of 10). Confidence moderate on D (upstream's
  chamber is a two-cue task, ours needs four combinations at once), low on A (one-hot units may give the cue
  enough of its own activity to escape the drag).
  Pre-registered rules, at 1600 moments, per arm: LEARNS if at least 7 of 10 seeds score above 6/8; PARTIAL if 3
  to 6; FAILS if at most 2. Reading:
  - If A0 LEARNS, EXP-07d does not replicate under this exam on 0.93.0; that is reported first and the other arms
    are read against it.
  - If D LEARNS and A0 FAILS, the limit EXP-07d found is located in the actor's step (the #208/#209 cause), not in
    the inputs, the size or the learning schedule, for this task.
  - Any other arm that LEARNS lifts the limit by itself; an arm that FAILS does not.
  - VOID if any arm errors or refuses to answer.
  Reported with them: each arm's mean score with its SEM, 8/8 counts, one-answer counts, and the curve at 400 and
  800 (registered secondary).
- Result (452 s, stderr empty): the brute-force ceiling was 6 of 8 on the 6 inputs and 8 of 8 with arm A's 14,
  as designed. At 1600 moments, seeds above 6 of 8 out of 10, mean score (SEM), and seeds giving one answer to
  every cue:
  - A0 control: 0/10, 0.500 (0.000), 9/10 on one answer. Curve 0.525, 0.500, 0.500 at 400, 800, 1600.
  - A the cue as its own input: 9/10, 0.925 (0.028), 0/10; 5 of 10 at 8 of 8. Curve 0.825, 0.850, 0.925.
  - B four times the association: 0/10, 0.537 (0.027), 7/10. Curve 0.562, 0.537, 0.537.
  - C trained through `step`: 0/10, 0.512 (0.012), 9/10. Curve 0.475, 0.512, 0.512.
  - D the 0.93.0 recipe: 10/10, 0.975 (0.017), 0/10; 8 of 10 at 8 of 8. Curve 0.925, 0.925, 0.975.
- Verdict: by the pre-registered rules, A0 FAILS, A LEARNS, B FAILS, C FAILS, D LEARNS. With A0 failing and D
  learning, the limit EXP-07d found sits in the actor's step on this task, not in the brain's size or in learning
  only when aroused. Arm A shows the inputs are a second, independent way out. The prediction held on four of
  five arms; it was wrong on A, which I expected not to learn. Atlas category: SUPPORTIVE.

## Reflection
- What it means: the composed founder's actor (rate 1.0) does not just fail to find the combination; it drives
  the policy to one answer for every cue (9 of 10 control seeds). A four-times-larger brain and learning on every
  moment leave that unchanged here, so on this task neither capacity (up to 256 association neurons) nor the
  learning schedule is the cause. Two single changes
  each lift it. A slower actor with the episodic memory (D) learns the combined rule on 10 of 10 seeds. Giving each
  cue its own input unit (A) learns it on 9 of 10, even at the founder's actor rate. Both fit the #208/#209 account:
  the reward update moves the preference mostly along activity all cues share, and either a smaller step or
  activity of the cue's own gives the cue's preference room to separate. For our own use, the guidance changes
  from yesterday's "hand the brain the combination as an input" to: hand it the combination, or compose it with
  `actor_eta=0.1, actor_eta_bias=0.01, memory_choice=True`. Of the two, only the recipe needs no hand-built input.
- Process: pre-registered and pushed (`b15cfc8`) before any data; an API-only smoke run (30 moments, no scores
  printed) checked that every arm composes and answers. Outputs were written to `.partial` files and renamed when
  the run finished, so the timed checkpoint could not commit a half-written run (the fix for this morning's slip).
  Weaknesses: arm D bundles three settings (a tenth of the actor rate, a fifth of its bias rate, the episodic
  memory), so this does not say which one does the work; and arm A's one-hot units grow with the number of
  situations, so A is a positive control here, not a recipe that scales.
- Lesson: when a reward-trained learner collapses to one answer for every input, test a slower actor step
  before a larger brain. On this task the size arm changed nothing and the slower-actor recipe nearly
  everything; one task is a reason to try it first, not proof that it always works.
- Next: queued EXP-07f, which splits arm D into its three settings (the actor rate alone, the bias rate alone, the
  episodic memory alone), so the guidance names the one setting that matters. For the Telegram creature (Will-gated,
  pinned at 0.91.1): if any of its rules depends on an encounter and its context together, it runs at the founder
  actor rate and so cannot learn that rule by this result. Nothing changes there without Will.
- Correction 2026-11-04 (EXP-07f, Cadence 0.93.1): splitting arm D on the same seeds, `memory_choice=True` alone learns
  on 10 of 10 (mean .975) and `actor_eta=0.1` alone and `actor_eta_bias=0.01` alone on 0 of 10 each. The memory alone
  gives D's whole lift on this task, so the verdict's reading that the limit "sits in the actor's step", and the lesson to
  try a slower actor step first, do not hold here. The arm verdicts above stand.
