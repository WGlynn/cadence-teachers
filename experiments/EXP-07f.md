# EXP-07f: which of the 0.93 recipe's three settings lifts EXP-07d's limit?

- Date: 2026-11-04 | Cadence version: 0.93.1 (main `a4fcea0`) | Program iter: iter56 (generic queue; off the V(S) ladder, which waits on Will-gated CAL-1 / CAL-2 / the registered zero test)
- Script: `exp/EXP-07f_split.py` | Evidence: `exp/EXP-07f-a4fcea0.out`, `exp/EXP-07f-a4fcea0.json`, `exp/EXP-07f-a4fcea0.err`, `exp/EXP-07f-a4fcea0.time`

## Summary
- Question: EXP-07e found that the 0.93 recipe (`actor_eta=0.1, actor_eta_bias=0.01, memory_choice=True`) lets a
  composed brain learn, from reward, a rule whose answer needs a cue's feature and its context combined (10 of 10
  seeds above the 6 of 8 a sum of input weights allows), where the founder does not (0 of 10 above it, 9 of 10
  giving one answer to every cue). The recipe bundles three settings. Which of them, set alone on the founder, lifts the limit? Why it
  matters: it names the one setting (or shows that no single one is enough) a learned policy of ours must be
  composed with to hold situation-and-context rules from reward, instead of copying a three-setting bundle on faith.
- Setup: EXP-07e's harness unchanged. EXP-07b's 8 cues (2-hot over 6 features); every seed a COMBINATION rule
  (EXP-07d's four in turn, s % 4), so no sum of the 6 inputs gets more than 6 of 8 (brute-forced in the script);
  the same 10 seeds (brain seed 7_075_000 + s, cue stream `default_rng(7_075_000 + s)`, the same stream in every
  arm); 1600 moments through `live`; outcome +1 right / -1 wrong given with the next moment; greedy exam at 400,
  800 and 1600 (per cue, a fresh deepcopy answers with `act(greedy=True)`; the exam does not touch the brain or
  the stream). Score = fraction of the 8 cues right; 7 or 8 of 8 means the brain combined the inputs. Cadence
  0.93.1, whose CHANGELOG reports every answer as on 0.93.0. Five arms, each
  `Brain.compose(inputs=6, actions=2, arousal=True, seed=...)` plus:
  - A0 control: nothing added (the founder: actor rate 1.0, bias rate 0.05, no episodic memory). EXP-07e's A0.
  - ETA: `actor_eta=0.1` alone. A named `actor_eta` keeps the current bias rate (docs/reward.md), so this arm
    runs at bias 0.05, half its actor rate.
  - BIAS: `actor_eta_bias=0.01` alone (actor rate stays 1.0, no episodic memory).
  - MEM: `memory_choice=True` alone (the episodic memory; actor rate 1.0, bias 0.05).
  - D recipe: all three together, EXP-07e's arm D.
  An API check before any data read the settings back from `basal_ganglia.config` and `memory_choice`: A0 1.0 /
  0.05 / off, ETA 0.1 / 0.05 / off, BIAS 1.0 / 0.01 / off, MEM 1.0 / 0.05 / on, D 0.1 / 0.01 / on, with no
  warnings. None of the three names was removed or renamed in 0.93.1.
- Prediction (written before any data): docs/reward.md says the composed actor rate "walks the policy to one held
  action; a tenth of it ... lets the cue decide", and EXP-07e's arm A showed the founder rate is not fatal once
  each cue has activity of its own, which points at the size of the step on activity the cues share. So I expect
  the actor rate to carry the lift: ETA LEARNS (at least 7 of 10 seeds above 6/8), BIAS FAILS (the step on shared
  activity stays at 1.0), MEM at most PARTIAL (its records key on the stream's temporal context, which on this
  task mixes in random earlier cues). A0 FAILS and D LEARNS as in EXP-07e, with per-seed answers identical to
  EXP-07e's, since 0.93.1 is reported bit-identical to 0.93.0. Confidence moderate on ETA and low on MEM:
  upstream's account credits the slower step and the episodic records together, in a two-cue chamber where the
  cue is gone by the answer, unlike here.
  Pre-registered rules, at 1600 moments, per arm: LEARNS (the registered test passes) if at least 7 of 10 seeds
  score above 6/8; PARTIAL if 3 to 6; FAILS if at most 2. Reading, in order:
  - Reproduction first: if D does not LEARN or A0 LEARNS, the split is not read; the verdict is INCONCLUSIVE and
    the run is reported as a failure to reproduce EXP-07e on 0.93.1. The per-seed answers of A0 and D at every
    exam are compared with `exp/EXP-07e-720c5a9.json` and reported as identical or not (identity is expected; a
    difference with the same verdicts is reported, not fatal).
  - One setting suffices: exactly one of ETA, BIAS, MEM LEARNS. That setting names the lift on this task.
  - Several suffice: two or three of them LEARN; each lifts it alone.
  - No single setting suffices: D LEARNS and none of ETA, BIAS, MEM LEARNS. Then at least two of the three are
    needed together on this task.
  - Two settings needed: this design has no pair arms, so it cannot show that exactly two are needed or name the
    pair. Under "no single setting suffices", the single arms that are PARTIAL are the candidate pair, and the
    follow-up runs the three pairs (ETA+BIAS, ETA+MEM, BIAS+MEM) on the same seeds. "Two settings needed" is
    claimed only when a pair arm passes the registered test there.
  - Loop verdict on the prediction: CONFIRMED if the reproduction holds and ETA LEARNS; REFUTED if the
    reproduction holds and ETA does not LEARN; INCONCLUSIVE if the reproduction fails. The BIAS and MEM
    predictions are reported as secondary.
  - VOID if any arm errors or refuses to answer.
  Reported with them: each arm's mean score with its SEM, 8/8 counts, one-answer counts, and the curve at 400 and
  800 (registered secondary).
- Result (444 s wall, exit 0, stderr empty): the brute-force ceiling was 6 of 8 on every rule, as designed, and the
  settings read back after the runs were the ones listed above. At 1600 moments, seeds above 6 of 8 out of 10, mean
  score (SEM), seeds at 8 of 8, and seeds giving one answer to every cue:
  - A0 control: 0/10, 0.500 (0.000), 0, 9/10. Curve 0.525, 0.500, 0.500 at 400, 800, 1600.
  - ETA `actor_eta=0.1` alone: 0/10, 0.588 (0.033), 0, 2/10. Curve 0.575, 0.537, 0.588. Its best seeds (2) sit at 6
    of 8, the ceiling, none above it.
  - BIAS `actor_eta_bias=0.01` alone: 0/10, 0.500 (0.019), 0, 8/10. Curve 0.537, 0.500, 0.500.
  - MEM `memory_choice=True` alone: 10/10, 0.975 (0.017), 8, 0/10. Curve 0.963, 0.963, 0.975 (9 of 10 seeds above
    the ceiling already at 400).
  - D the full recipe: 10/10, 0.975 (0.017), 8, 0/10. Curve 0.925, 0.925, 0.975.
  - Reproduction: A0's and D's answers are identical to EXP-07e's (0.93.0) at all three exams on 10 of 10 seeds.
- Verdict: the reproduction holds. By the pre-registered rules A0 FAILS, ETA FAILS, BIAS FAILS, MEM LEARNS, D
  LEARNS: one setting suffices, and it is the episodic memory, `memory_choice=True`. Loop verdict on the
  prediction: REFUTED, because I predicted the actor rate would carry the lift and ETA scored 0 of 10. Of the
  secondary predictions, BIAS FAILS held and MEM at most PARTIAL was wrong (10 of 10). Atlas category: SUPPORTIVE.

## Reflection
- What it means: on this task the setting that lets a composed brain learn a situation-and-context rule from
  reward is the episodic memory. The actor settings are not needed for it (MEM learns at the founder's actor rate
  1.0 and bias 0.05, as well as the full recipe at 1600), and neither one alone is enough (0 of 10 each). The
  slower actor alone changes how the failure looks, not whether it fails: 2 of 10 seeds give one answer to every
  cue against 9 of 10 for the founder, but no seed beats the 6 of 8 a sum of input weights can reach. This
  corrects EXP-07e's reading, which placed the limit "in the actor's step": here the memory alone gives the
  bundle's whole lift, and the actor settings are not needed for it. A reading I did not test: the memory's place records are keyed through a fixed random separation
  (1,024 cells, 24 active per key, per the 0.93.1 docstring), so each of the 8 cues can hold a record of its own,
  which is what EXP-07e's arm A gave with one-hot units; the lift would then be a per-situation lookup. For our
  learned policies the guidance becomes: compose with `memory_choice=True`; on this task the slower actor is not
  needed. Whether that holds as the number of situations grows, or for a situation never seen, is open.
- Process: pre-registered and pushed with the script (`292cd34`) before any data; an API-only smoke run (30
  moments, no scores) and a read-back of each arm's settings. Outputs were written as `.partial` and renamed on
  finish, with python's exit code kept in the `.time` file. The reproduction check against EXP-07e's JSON was
  exact. Weaknesses: one task, one budget (1600 moments), 10 seeds; the ETA arm kept the founder's bias 0.05,
  because a named `actor_eta` keeps the current bias rate, so the slower actor pair (0.1 with bias 0.01) without
  the memory was not run; and MEM and D tie at 1600, so this does not show whether the slower actor helps or
  hurts beside the memory (their 400 means, 0.963 and 0.925, are within their SEMs of 0.027 and 0.033).
- Lesson: split a bundle of settings before writing guidance from it, and word a pre-registered reading about a
  bundle as "in the bundle" until it is split. The recipe's documentation leads with the slower actor; on our
  task the slower actor alone passed on no seed and the memory alone on every seed.
- Next: queued EXP-07g on the same seeds: the place records alone (`memory_choice=True, memory_context=0.0`) to
  test the lookup reading, and the slower actor pair without the memory to close the one combination this run
  left out. EXP-07e's write-up gets a dated note pointing here.
