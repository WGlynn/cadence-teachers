# EXP-07g: is the episodic memory's lift a per-situation lookup, and does the slower actor pair lift EXP-07d's limit without the memory?

- Date: pre-registered 2026-11-05 (`7a27f4e`, 09:57); first run 2026-11-05 10:00; recorded 2026-11-13 from a rerun | Cadence version: 0.94.0 (main `2a32a98`; the 2026-11-13 rerun used the clone at `4cb9c29`, which is `2a32a98` plus one local commit that touches only tests/test_maturity.py, so `src/` is identical) | Program iter: iter57 (generic queue; off the V(S) ladder, which waits on Will-gated CAL-1 / CAL-2 / the registered zero test)
- Version note: 0.94.0 adds maturity as an opt-in. It is off here, the default. Upstream reports that a brain with it off is 0.93.1 to the bit; the MEM control tests that claim on this task. Upstream has since released up to 0.99.0 (2026-11-12); this result is not checked there.
- Script: `exp/EXP-07g_split2.py` | Evidence: `exp/EXP-07g-2a32a98.out`, `exp/EXP-07g-2a32a98.json`, `exp/EXP-07g-2a32a98.err`, `exp/EXP-07g-2a32a98.time` (2026-11-05 run); `exp/EXP-07g-4cb9c29-rerun.out`, `.json`, `.err`, `.time` (2026-11-13 rerun)

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
- Result (2026-11-13 rerun: 205 s wall, exit 0, stderr empty; the 2026-11-05 run: 273 s, exit 0, stderr empty): the
  rerun's rows, summary checks and settings read-back are equal to the 2026-11-05 run's JSON in full, so the two
  runs are one result. The API smoke run passed on 0.94.0. The brute-force ceiling was 6 of 8 on every rule, and the
  settings read back were MEM eta 1.0, bias 0.05, memory on, context 0.5; MEMCTX0 the same with context 0.0; PAIR eta
  0.1, bias 0.01, memory off. At 1600 moments, seeds above 6 of 8 out of 10, mean score (SEM), seeds at 8 of 8, seeds
  giving one answer to every cue:
  - MEM control `memory_choice=True`: 10/10, 0.975 (0.017), 8, 0/10. Curve 0.963, 0.963, 0.975 at 400, 800, 1600.
    Reproduction: answers identical to EXP-07f's MEM arm (0.93.1) at all three exams on 10 of 10 seeds.
  - MEMCTX0 `memory_choice=True, memory_context=0.0`: 10/10, 1.000 (0.000), 10, 0/10. Curve 0.975, 0.988, 1.000;
    9 of 10 seeds already above the ceiling at 400.
  - PAIR `actor_eta=0.1, actor_eta_bias=0.01`, no memory: 0/10, 0.588 (0.033), 0, 2/10. Curve 0.525, 0.512, 0.588.
    Best seeds (2) at 6 of 8, the ceiling, none above it. Its scores at 1600 have the same spread as EXP-07f's
    `actor_eta=0.1` alone arm (five at 4/8, three at 5/8, two at 6/8) but differ seed by seed (equal on 1 of 10).
- Verdict: the reproduction holds (0.94.0 with maturity off answers as 0.93.1 on this task). By the pre-registered
  rules MEM LEARNS, MEMCTX0 LEARNS, PAIR FAILS. Loop verdict on the prediction: CONFIRMED (MEMCTX0 LEARNS and PAIR
  FAILS, both as predicted, and the reproduction is exact). Atlas category: SUPPORTIVE.

## Reflection
- What it means: on this task the memory's lift does not need the temporal context in the key. With the context
  weight at 0.0 the place records, keyed by the observation alone through the memory's fixed random separation,
  learned the feature-and-context rule on every seed, at 8 of 8 on all 10 (the default context weight 0.5 left 2
  seeds at 7 of 8). That is what a per-observation record predicts, the same thing EXP-07e's arm A got from one-hot
  units, but it does not prove it; a record keyed on the observation alone is consistent with the lookup reading
  and so is anything else that separates the 8 distinct 2-hot inputs. The slower actor pair without the memory
  fails like each of its halves did alone in EXP-07f: no seed beats what a sum of input weights allows, so the
  actor settings are not a second way out on this task. EXP-07f's guidance stands and gets narrower: compose with
  `memory_choice=True`; the context in the key and the slower actor are not needed here. If the lift is a lookup,
  it grows with the number of distinct situations and should give nothing for a situation never seen; that is the
  open question, and it decides whether this is a recipe for our learned policies or only for small, closed sets
  of situations.
- Process: pre-registered and committed (`7a27f4e`, 09:57) before any data. The fire that pre-registered it ran
  it at 10:00 on 2026-11-05 (exit 0, outputs on disk) and then stopped before writing it up, so the result sat
  unrecorded for eight days with the queue item still `ready`. This fire found the orphaned outputs, reran the
  script under the same pre-registration on the installed clone, and recorded the run only after the rerun matched
  it in full. The interpreter of this fire saw the 2026-11-05 numbers before the rerun; the verdict comes from the
  pre-registered rules, so that did not change it. MONITOR-STATE's baseline still says 0.93.1 (the monitor has not
  run since 2026-11-08 because of a cron fault); the clone's installed version was read directly. Weaknesses: one
  task, 8 situations, one budget (1600 moments), 10 seeds; no unseen situation was tested; the setting read-back
  shows the context weight the brain reports, not how the key is built inside the memory.
- Lesson: an orphaned run (outputs on disk, write-up never filled) is not a result until a deterministic rerun
  under the same pre-registration matches it; then record both, and say who saw what when.
- Next: queued EXP-07h (does the memory's lift hold as the number of situations grows, and does it give anything
  on a situation it never saw?). The queue item is marked done; it should be re-read on the version the monitor
  installs next (upstream is at 0.99.0).
