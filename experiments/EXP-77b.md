# EXP-77b: M1b on Cadence 0.89.0, zero admitted by construction

- Date: 2026-10-27 (pre-registered before any EXP-77b data) | Cadence version: 0.89.0 (`81345d8`) | Program iter: iter49
- Script: `exp/EXP-77b_m1b_construction_zero.py` (EXP-77 exactly, one rule changed); admission: `exp/EXP-77b_construction_audit.py` | Evidence: `exp/EXP-77b-*`

## Pre-registration (written 2026-10-27, before any EXP-77b data)

**Question.** Does M1b, crossed by EXP-73 on Cadence v0.84.3, hold on the current release (0.89.0) under its own defaults, when the zero is admitted by construction instead of by a per-run sample test?

**Why this run exists, disclosed.** EXP-77 (0.88.1) passed all six CONFIRM criteria. It was VOID only because the null arm's label hit rate (.1958, interval [.1919, .1997]) excluded .20 by .0003. Those labels are drawn uniformly from five actions, so their true hit rate is exactly .20. A 95% check on each of two such arms therefore fails about 10% of runs by chance alone (EXP-77 Reflection). Changing a rule after a near-miss is exactly what pre-registration exists to police. So the safeguards are: EXP-77 stays VOID and is not re-scored. This run uses fresh seeds. The new rule is fixed here, before any of its data. The old check is still computed and reported. Will gave the go for this change on 2026-10-27.

**The one rule that changes (admission).** The zero is admitted iff `exp/EXP-77b_construction_audit.py` prints ADMITTED BY CONSTRUCTION, run once before the pilot. Its checks, all deterministic:
1. code: the labeller entry point both labelled zero-class arms use (null and random) routes `random` to EXP-52's branch `return lambda c, a: int(rng.integers(5))`;
2. blindness: 1,000 labels produced with a chamber whose `right()` raises and an action whose `int()` raises (a label that read either would crash);
3. a seeded draw of 10^6 labels (seeds 77_000_002 / 77_000_003): every action's share within .002 of .2 (5 SE), the hit rate against a seeded right-answer stream within .002 of .2, and the hit rate per right answer within .004 (5 SE at about 250k each).
If any check fails, EXP-77b is VOID before any run. The per-run binomial interval is reported next to the verdict, not decisive.

**Everything else is EXP-77.** Delayed-credit brain on the ported composition (`scales={'trace': 12.0}`), founder lateral (0.0), weather chamber, corrective schedule, 20 attempts through `step`, per-state greedy accuracy over 16 states on unseen weather, lesson 80, arms null, untaught, know-1..4, random, wrong-chain, echo, anti-echo. Zero Z = per-student mean of {null, untaught, random}; worth = arm minus Z on the same student; pay on batches of 6 students per arm, finalized iff batch mean > 0 and mean / SEM > 2.

**Version.** 0.89.0 adds a recall-memory position term on by default; this brain composes no recall memory, and the port gate (EXP-73's identity gate, lateral pinned to -0.5) on 0.89.0 reproduces every arm's actions and labels of EXP-62e student 0: IDENTICAL (`exp/EXP-77b-gate-81345d8.out`, 100 s).

**Students.** 216 fresh students, seeds 9_000_000 + student (disjoint from every earlier run). Pilot: 6 students, seeds 8_990_000 + student; pilot data never enters the verdict.

**Pilot rule.** If the pilot's know-4 worth is below .10, the full run does not start; record PILOT STOP.

**Prediction.** CONFIRM, with know-1..4 within about .05 of EXP-77's (+.060 / +.147 / +.250 / +.397). The old interval check passes with probability about .9; its outcome is not predicted and does not decide.

**Decision rules (EXP-73's six criteria and KILL, unchanged).**
- CONFIRM if all hold:
  1. know-1 < know-2 < know-3 < know-4 and Spearman(worth, k) >= .3 (n = 864);
  2. know-4 >= .2;
  3. non-superiority: for null, untaught, random, wrong-chain and echo, mean worth + 1.645 SEM < 1/32;
  4. know-1 beats each of null, untaught and random by at least 2 SEM, paired;
  5. know-1 beats anti-echo by at least 2 SEM, paired;
  6. all knowledge-free arms together (anti-echo included) take <= .10 of pay.
  Then M1b holds on Cadence 0.89.0 under its founder defaults, on instrument I (the delayed-credit brain). Limits as EXP-73: one brain, one chamber, one lesson length.
- KILL: any knowledge-free arm's mean worth >= know-2's.
- VOID: the construction audit fails.
- Anything else: BOUNDARY, failing criterion named.
- Reported, not decisive: the old interval check; per-arm worth next to EXP-73's and EXP-77's.

**Cost.** About 50 to 80 minutes at 4 workers (EXP-77: 3,080 s), run detached; audit and pilot a few minutes.

## Status (2026-10-27)
- Construction audit run before the pilot: ADMITTED BY CONSTRUCTION (all six checks pass; 10^6 labels, shares .1997-.2006, hit .1995; `exp/EXP-77b-audit.out`).
- Pilot (6 students, seeds 8_990_000+): stop check passed, know-4 worth +.431 (>= .10). Pilot data never enters the verdict (`exp/EXP-77b-pilot.log`).
- Full run (216 students, seeds 9_000_000+) NOT STARTED: held by Will on 2026-10-27 (token budget given to the ETM doc sweep). Start with `TAG=full WORKERS=4 python -u EXP-77b_m1b_construction_zero.py` from `exp/`; the rules above stand unchanged.

## Summary
- PENDING (to be written after the run)

## Reflection
- PENDING (to be written after the run)
