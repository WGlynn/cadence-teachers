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
- PENDING.

## Reflection
- PENDING.
