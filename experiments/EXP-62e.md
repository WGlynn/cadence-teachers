# EXP-62e: a non-superiority margin for the fakes, powered for the class

- Date: pre-registered 2026-10-19 (not run) | Cadence version: record at run time (identity-gate one EXP-62d student first) | Program iter: iter39
- Script: `exp/EXP-62e_margin_zero.py` (EXP-62's harness unchanged; analysis = EXP-62d's plus the margin rule) | Evidence: `exp/EXP-62e-full.*`

## Pre-registration (written 2026-10-19, before any EXP-62e data)

**Question.** With the zero pooled over the declared uninformative class, and each fake required to sit below a margin set by the instrument's own resolution, does transfer price skill on the content-taking brain on fresh students?

**Why, and why this is the last redesign of the zero test.** EXP-62, 62c and 62d each failed only the zero-point criterion, by a different arm each time. EXP-62d's rule (no fake above zero by more than 2 SEM) is a significance test that a fake is positive. Under exact equality of the four uninformative arms it fails about 9% of the time at n 72 and at n 216 alike (within-student permutation of the real EXP-62/62c/62d data, 4,000 resamples). With any small real gap (pooled, abstain minus the random-label arms is about +.02), more students make it fail more often, not less. So the 62d rule cannot be fixed by adding students. The question we care about is whether a fake is worth anything that matters, which is a non-superiority test against a margin. This is the fourth decision rule in four runs. Whatever EXP-62e returns stands: no further zero-point redesign in this program; the next rung is EXP-62b either way.

**Disclosure.** This rule was written after seeing EXP-62, 62c and 62d. The margin comes from the instrument's grid, not from those results (see below), but the choice to use a margin was prompted by them.

**Setup.** EXP-62's harness exactly (delayed-credit brain, weather chamber, corrective schedule, 20 attempts alone through `step`, per-state greedy accuracy over 16 states on unseen weather), lesson 80, **216 fresh students**, seeds 6_800_000 + student (disjoint from 6_200_000+, 6_400_000+, 6_600_000+ and every pilot). Arms: null, untaught, know-1..4, random, wrong-chain, echo, anti-echo.
- Zero Z = per-student mean accuracy of {null, untaught, random, anti-echo}. Worth = arm minus Z on the same student.
- Margin delta = 1/32 = .03125: half of one state of the 16 on which accuracy is read, the smallest worth that is not a fraction of a single answer.
- Pay: worth vs Z, batches of 6 students per arm, finalized iff batch mean > 0 and mean / SEM > 2.

**Prediction.** Planning numbers from resampling the 216 seen students at n 216 (not a result): the margin criterion passes in about 85% of resamples and all criteria together in about 85%; under exact equality the margin criterion false-fails about 1%. Expected: know-1..4 near +.065 / +.14 / +.26 / +.41, uninformative arms within +-.015, CONFIRM. Main risk: a real abstain-vs-random-labels gap near +.02 pushing untaught's upper bound toward the margin.

**Decision rules.**
- CONFIRM if all hold:
  1. know-1 < know-2 < know-3 < know-4 and Spearman(worth, k) >= .3 (n = 864);
  2. know-4 >= .2;
  3. **non-superiority:** for every fake (null, untaught, random, anti-echo, wrong-chain, echo), mean worth + 1.645 SEM < 1/32;
  4. know-1 beats every uninformative arm by at least 2 SEM, paired;
  5. fakes take <= .10 of pay.
  Then M1b is crossed: transfer prices skill on instrument I (delayed-credit brain) against zero N (the pooled uninformative class), with no fake worth half an answer.
- KILL: any fake's mean worth >= know-2's.
- Anything else: BOUNDARY, failing criterion named. Also reported, not decisive: EXP-62d's 2-SEM criterion on the same data.

**Cost.** About 56 min at 4 workers (216 students x 10 twins, about 62 s per student per worker on 0.84.3).

## Summary
PENDING (after the run)

## Reflection
PENDING (after the run)
