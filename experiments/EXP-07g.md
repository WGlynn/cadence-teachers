# EXP-07g: is the episodic memory's lift a per-situation lookup, and does the slower actor pair lift EXP-07d's limit without the memory?

- Date: 2026-11-05 | Cadence version: 0.94.0 (main `2a32a98`) | Program iter: iter57 (generic queue; off the V(S) ladder, which waits on Will-gated CAL-1 / CAL-2 / the registered zero test)
- Version note: 0.94.0 adds maturity as an opt-in. It is off here, the default. Upstream reports that a brain with it off is 0.93.1 to the bit; the MEM control tests that claim on this task.
- Script: `exp/EXP-07g_split2.py` | Evidence: `exp/EXP-07g-2a32a98.out`, `exp/EXP-07g-2a32a98.json`, `exp/EXP-07g-2a32a98.err`, `exp/EXP-07g-2a32a98.time`

## Summary
- Question: EXP-07f found that `memory_choice=True` alone lifts EXP-07d's limit (10 of 10 seeds above the 6 of 8 a
  sum of input weights allows) while `actor_eta=0.1` alone and `actor_eta_bias=0.01` alone do not (0 of 10 each).
  Two things were left open. First, the reading of the lift: the memory's place records are keyed through a fixed
  random separation of the observation together with the stream's temporal context, so the lift could be a
  per-situation lookup (each of the 8 cues holds a record of its own, as EXP-07e's arm A gave with one-hot units)
  or something that needs the context in the key. Second, the one combination EXP-07f did not run: the slower
  actor pair (0.1 with bias 0.01) without the memory, since a named `actor_eta` keeps the current bias rate. Why it
  matters: the first decides whether "compose with `memory_choice=True`" is a lookup that grows with the number of
  situations or something that carries over; the second closes the gap in EXP-07f's guidance and bears on #169's
  actor-step table, which moves step and bias together and leaves the memory out.
- Setup: EXP-07f's harness unchanged (EXP-07e's). EXP-07b's 8 cues (2-hot over 6 features); every seed a
  COMBINATION rule (EXP-07d's four in turn, s % 4), so no sum of the 6 inputs gets more than 6 of 8 (brute-forced
  in the script); the same 10 seeds (brain seed 7_075_000 + s, cue stream `default_rng(7_075_000 + s)`, the same
  stream in every arm); 1600 moments through `live`; outcome +1 right / -1 wrong given with the next moment; greedy
  exam at 400, 800 and 1600 (per cue, a fresh deepcopy answers with `act(greedy=True)`; the exam does not touch the
  brain or the stream). Score = fraction of the 8 cues right; 7 or 8 of 8 means the brain combined the inputs.
  Cadence 0.94.0 with maturity off (the default), which upstream reports as 0.93.1 to the bit. Three arms, each
  `Brain.compose(inputs=6, actions=2, arousal=True, seed=...)` plus:
  - MEM control: `memory_choice=True` alone. EXP-07f's MEM arm, expected to repeat its answers exactly.
  - MEMCTX0: `memory_choice=True, memory_context=0.0`, the place records alone, keyed by the observation through
    the memory's fixed random separation, with no context in the key (`memory_context` composes on 0.93.1 and
    0.94.0; the setting is read back after the runs).
  - PAIR: `actor_eta=0.1, actor_eta_bias=0.01` without the memory, the combination EXP-07f left out.
  An API-only smoke run (30 moments of one seed per arm, no scores) checks that each arm composes, trains and
  answers on 0.94.0 before any data, and the settings are read back from `basal_ganglia.config`, `memory_choice`
  and the memory's context attribute after the runs.
- Prediction (written before any data): EXP-07f's reflection leaned toward the lookup reading, because the
  separation already gives each distinct observation its own key and the 8 cues are distinct 2-hot vectors, so the
  temporal context should not be needed to keep their records apart. So I expect MEMCTX0 LEARNS (at least 7 of 10
  seeds above 6 of 8), moderate confidence: the risk is that `memory_context=0.0` changes the key in a way the
  docstring does not describe, or that the records then collide. For PAIR I expect FAILS (at most 2 of 10):
  neither setting alone moved any seed above the ceiling, the ceiling is representational (a sum of input weights
  caps at 6 of 8 whatever the step), and the lift needs either a per-situation record or a per-cue input; the
  slower pair should change how the failure looks (fewer one-answer seeds, as ETA did) but not whether it fails.
  Moderate confidence; upstream's #169 table credits the slower pair in reward chambers where the cue is gone by
  the answer, which is not this task. MEM LEARNS with answers identical to EXP-07f's on 10 of 10 seeds, since
  0.94.0 is reported bit-identical to 0.93.1 with maturity off.
  Pre-registered rules, at 1600 moments, per arm: LEARNS (the registered test passes) if at least 7 of 10 seeds
  score above 6/8; PARTIAL if 3 to 6; FAILS if at most 2. Reading, in order:
  - Reproduction first: if MEM does not LEARN, the other arms are not read; the verdict is INCONCLUSIVE and the
    run is reported as a failure to reproduce EXP-07f on 0.94.0. MEM's per-seed answers at every exam are compared
    with `exp/EXP-07f-a4fcea0.json` and reported as identical or not (identity is expected; a difference with the
    same verdict is reported, not fatal, and is itself a finding about 0.94.0).
  - Lookup reading: MEMCTX0 LEARNS means the lift does not need the temporal context in the key, which is what a
    per-observation record predicts (it does not prove the lookup reading; a record keyed on the observation alone
    is consistent with it). MEMCTX0 PARTIAL or FAILS means the context in the key is part of the lift on this task.
  - Actor pair: PAIR LEARNS means the slower pair is a second way out without the memory, and EXP-07f's guidance
    gains an alternative; PAIR FAILS means the actor settings are not sufficient without the memory on this task,
    which closes EXP-07f's gap. PARTIAL is reported as such and named a weak second way.
  - Loop verdict on the prediction: CONFIRMED if the reproduction holds, MEMCTX0 LEARNS and PAIR FAILS; REFUTED if
    the reproduction holds and either arm reads otherwise; INCONCLUSIVE if the reproduction fails.
  - VOID if any arm errors or refuses to answer.
  Reported with them: each arm's mean score with its SEM, 8/8 counts, one-answer counts, and the curve at 400 and
  800 (registered secondary).
- Result: PENDING (pre-registered before any data; the run follows the 0.94.0 monitor probes).
- Verdict: PENDING.

## Reflection
- PENDING.
