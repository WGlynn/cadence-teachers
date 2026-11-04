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
- Result: PENDING
- Verdict: PENDING

## Reflection
PENDING
