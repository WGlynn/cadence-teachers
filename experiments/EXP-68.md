# EXP-68: is the failure cost's harm a switch in the memory, and which part of the memory?

- Date: pre-registered 2026-10-20 (Will's go 2026-10-20 06:57; off-program, memory track, upstream #202 / #210), before any EXP-68 data | Cadence version: 0.84.3 (`8dc92d8`), record at run time | Program iter: none
- Script: `exp/EXP-68_memory_switch.py` (imports EXP-67, so chambers, brain, cost and readings are EXP-66/67's code) | Evidence: `exp/EXP-68-check.out`, `exp/EXP-68-full.*`

## Pre-registration (written 2026-10-20, before any EXP-68 data)

**In one line: is the cost an on/off switch inside the memory?** The library treats any nonzero reward, however small, as a known outcome. So a cost of any size may flip how the memory behaves. This test checks for the switch, then finds which part of the memory carries it.

**Why.** EXP-67 found that under reward alone a per-miss cost cut hidden-chain sampled success from .349 to about .04 to .10, almost flat from a cost of .005 to .05. A harm that does not shrink over a tenfold range looks like a switch. Reading the library at 0.84.3 (`_cadence_study/src/cadence/generic.py`) shows two places where any nonzero reward acts as a switch, whatever its size:
- **Writes** (`_record_outcome`, line 3154): `known = learned & ((reward != 0) | done | woken | marked)`. A charged miss becomes an outcome the episodic memory writes.
- **Replay** (`_replay`, lines 3221-3222): the success reward is credited backwards along the path only while each earlier step's reward is exactly `0.0`. A charged miss stops the replay there, so the final +2 is credited only to the decisions after the last miss. Without the cost it can reach back along the whole attempt (up to `memory_replay` steps).

**Setup.** EXP-67's brain, chambers, 120 attempts and readings, unchanged (chambers allow 10 decisions per attempt and pay +2 / -1 at the end). Four changes. The hidden chain only. The natural signal only. Fresh seeds 68_000 + i; no script in `exp/` uses 68_000-68_999 (checked by grep). 48 lives per arm, paired by seed. Arms (7):
- `ctx5`: no cost.
- `pen@1e-6`, `pen@1e-4`, `pen@.005`: every non-terminal miss pays -p (EXP-66/67's cost).
- `penm@.005`: the cost reaches the brain's learner (the basal-ganglia actor-critic gets the true reward), but the episodic memory sees zero. Rewards with |r| < .5 are replaced by 0 in both `_received` (what the path stores) and `_record_outcome` (what the memory writes and replays from). Terminal rewards (+2 / -1) are untouched.
- `penmR@.005`: replay restored only. The path stores 0 for the cost (so replay flows through), but `_record_outcome` still sees the cost (the miss is still written).
- `penmW@.005`: writes removed only. `_record_outcome` sees 0 for the cost (no write), but the path keeps the cost (replay still stops at it).
The masks patch two private `Brain` methods at the class level in this process only. They are a probe, not a proposed change to the library.

**Primary reading.** Sampled success, Delta = arm minus ctx5, paired by seed, with the paired SEM. Contrasts against pen@.005 the same way. Also reported: clean greedy passes, first-try accuracy by stage, and per-life counts of the non-terminal nonzero rewards the memory saw, in `_received` and in `_record_outcome`.

**Check (`MODE=check`, before the full run; a failure stops it).** (a) penm, penmR and penmW at p = 0 are identical to ctx5 (hidden chain, natural, seed 68_990). (b) The masks do what they say, at p = .005 on that seed. In pen the memory sees the cost in both methods. In penm it sees it in neither. In penmR the path holds no cost. In penmW `_record_outcome` sees no cost. And pen@1e-6 charges every non-terminal miss. (c) pen@.005 through this script equals EXP-67's `life()` on the same seed.

**Predictions (written before any data).**
- pen@1e-6 harms at 2 SEM (the switch): about 75%, because both code paths test for exactly zero.
- penm@.005 recovers (above pen@.005 by 2 SEM and not below ctx5 by 2 SEM): about 65%.
- Of the two parts, restoring replay (penmR) recovers more than removing writes (penmW): about 60%, because the hidden chain needs credit to reach back along the chain.

**Decision rules (written before any data).**
- MEMORY SWITCH (SUPPORTIVE): pen@1e-6 has Delta at or below -2 SEM, and penm@.005 is at least +2 SEM above pen@.005 and not below ctx5 by 2 SEM.
- SWITCH OUTSIDE THE MEMORY (BOUNDARY): pen@1e-6 has Delta at or below -2 SEM, and penm@.005 does not meet that bar.
- DOSE (NULL): pen@1e-6 is within 2 SEM of ctx5. pen@1e-4 shows where the harm turns on.
- Reported with every verdict: penmR - pen@.005 and penmW - pen@.005 (which part carries it), and penmR + penmW against penm (whether the parts add).
Loop verdict: SUPPORTIVE -> CONFIRMED; BOUNDARY -> INCONCLUSIVE; NULL -> REFUTED.

**Cost.** 7 arms x 48 lives = 336 lives, about 15 s each, about 20-25 min at 4 workers.

## Check
- 2026-10-20 07:10, `exp/EXP-68-check.out`, Cadence 0.84.3, seed 68_990, hidden chain, natural: **PASS.** (a) penm, penmR and penmW at p = 0 are identical to ctx5. (b) At .005 the memory saw the cost 809 / 809 times in pen (path / outcome), 0 / 0 in penm, 0 / 552 in penmR, 906 / 0 in penmW. pen@1e-6 charged all 915 non-terminal misses, and the memory saw them. (c) pen at .005 equals EXP-67's `life()`. Nothing in the design changed.

## Summary
- Question: is the per-miss cost's harm to a teacherless learner a switch in the episodic memory, and which part of the memory carries it?
- Setup: as registered. Cadence 0.84.3 (`8dc92d8`), check PASS (90da30b), hidden chain, natural signal, 7 arms x 48 lives = 336, seeds 68_000+, 1,358 s at 4 workers.
- Prediction: see the pre-registration (switch about 75%; penm recovers about 65%; replay part recovers more than the writes part about 60%).
- Result, sampled success (delta vs ctx5, paired SEM):
  - ctx5 .413. pen@1e-6 .068 (-.344, .051). pen@1e-4 .071 (-.341, .052). pen@.005 .127 (-.285, .059). A cost of one millionth harms as much as one of .005.
  - penm@.005 (the learner gets the cost, the memory sees none) .417 (+.004, .083): no harm detected (the interval still allows a loss of up to about .16). penm minus pen@.005 +.290 (.060).
  - penmR@.005 (replay restored, writes kept) .294; penmR minus pen +.167 (.055). penmW@.005 (writes removed, replay still stopped) .142; penmW minus pen +.015 (.044).
  - Additivity, (R + W) minus both: -.107 (.082). The two parts recover less apart than together. Removing the writes matters only once replay is restored.
  - Clean greedy passes stay near zero under reward alone (0 to 5 of 48).
- Criteria: pen@1e-6 at -6.7 SEM (switch). penm recovers (+4.8 SEM over pen, +.004 vs ctx5).
- Verdict: **MEMORY SWITCH** (SUPPORTIVE; loop: CONFIRMED).

## Reflection
- What it means: the timidity in EXP-66 and EXP-67 is not the learner reacting to a cost. It is the episodic memory flipping a switch. Hide the cost from the memory alone and no harm is detected (.417 vs .413; the SEM of .083 still allows a loss of up to about .16), even though the actor-critic still gets every charge. Show the memory a cost of 1e-6 and the harm is full size. The switch is mostly the replay rule. `_replay` credits the final reward backwards only through steps whose own reward is exactly 0.0 (`generic.py` 3221-3222, Cadence 0.84.3). So any charged miss stops the replayed success credit at that miss, and the decisions before it never get that credit (they can still learn through the actor-critic). Restoring replay recovers about 58% of the harm. Removing the writes recovers nothing alone, and the rest together with replay.
- For upstream (#202, #210): for this brain (memory choice with replay on), in a world that charges anything for a miss, the memory's replay stops at every miss. A shaping cost then works against a reward-only learner at any size, and that is a property of the exact-zero tests (`reward != 0` for writes, `== 0.0` for replay), not of the cost. Whether to change them is the library's design call. A tolerance, or treating sub-salient rewards as nothing on the replay path, would be the obvious candidates, and this harness can test either.
- Prediction check: all three held (switch, penm recovers, replay part larger than the writes part). I did not predict the interaction: removing writes helps only together with restored replay.
- Process: reading the library before designing the test turned a vague "eligibility switch" into two exact code sites. That let one run split the mechanism instead of just confirming it. The check confirmed each mask hid exactly what it said (path 0 / outcome 552 for penmR, path 906 / outcome 0 for penmW) before any data.
- Lesson: when a harm is flat across sizes, find the exact-zero test in the code. Then build one arm per test site that hides the signal from that site only.
- Next: offer the finding on #202 (Will's call), with the two code sites and this harness. A natural follow-up is the replay rule with a tolerance, under reward alone and with the corrective teacher, to check that it does not cost EXP-66's teacher gains.
