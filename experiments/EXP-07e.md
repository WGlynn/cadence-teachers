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
- Result: PENDING
- Verdict: PENDING

## Reflection
PENDING
