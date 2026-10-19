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
- Question: with the zero pooled over the declared uninformative class and each fake required to sit below a margin of 1/32, does transfer price skill on the content-taking brain on fresh students?
- Setup: EXP-62's harness unchanged, lesson 80, 216 fresh students (seeds 6_800_000 + student), zero = per-student mean of {null, untaught, random, anti-echo}, decisive rule = non-superiority (every fake's worth + 1.645 SEM < .03125). Run 2026-10-19 on v0.84.3 (`8dc92d8`), 3,784 s at 4 workers (shared the CPU with EXP-66's check and pilot). The version had not moved since EXP-62d, so the identity gate was not needed.
- Prediction (written before the run): know-1..4 near +.065 / +.14 / +.26 / +.41, uninformative arms within +-.015, CONFIRM about 85% of the time; main risk an abstain-vs-random-labels gap near +.02.
- Result: zero = .451. know-1..4 +.069 / +.146 / +.254 / +.416 (SEMs .009-.012), ordered, Spearman .614 (n 864). Uninformative arms: null -.015 (SEM .007), untaught +.006 (.006), random -.013 (.007), **anti-echo +.023 (.006, 3.6 SEM)**. Misleading: wrong-chain -.093, echo -.134. Upper bounds vs the margin: null -.004, untaught +.016, random -.003, **anti-echo +.033 (margin .031)**, wrong-chain -.079, echo -.118. Separation (paired): know-1 beats null by 7.5 SEM, random 7.2, untaught 5.6, anti-echo 4.1. Fake pay share .024.
- Criteria: ordered + Spearman yes; know-4 >= .2 yes; non-superiority **NO (anti-echo, by .002)**; know-1 beats every uninformative arm by 2 SEM yes; fake pay <= .10 yes. No kill. EXP-62d's 2-SEM rule on the same data also fails (anti-echo).
- Exploratory (not pre-registered; mechanism read from logged fields): the share of labels that name the right action is .25 for anti-echo and .20 for the random null and the random teacher in every run (EXP-62 .253 / .198, 62c .252 / .200, 62d .251 / .197, 62e .249 / .201). That follows from the design: labels only follow mistakes, so "any action but the one just executed" picks the right one 1 time in 4, a random label 1 time in 5. Pooled over all four runs (432 students, lesson 80): anti-echo +.016 (3.4 SEM), random -.014 (-3.0 SEM), null -.009, untaught +.007, know-1 +.067 (10.5 SEM). Anti-echo carries about 38% of know-1's label-information edge over random (.05 of .13) and earns about 38% of its worth edge (.031 of .081).
- Verdict: BOUNDARY (4/5; the margin rule failed on anti-echo). As pre-registered, this was the last zero-point redesign; the program moves to EXP-62b.

## Reflection
- What it means: the skill price replicates a fourth time on a fourth disjoint student set, the tightest yet (know-1 at 7.5 SEM). The zero-point failures across EXP-62, 62c, 62d and 62e have one cause, and it is in the declared class, not the instrument: anti-echo is not uninformative. It names the right action a quarter of the time where random labels manage a fifth, and the instrument prices that difference in proportion. EXP-62's first reading ("worth tracks label information, r .99; the corrective schedule leaks an elimination bit") was right, and EXP-62c's withdrawal of it was wrong: at n 72 the effect sat inside the noise and the ordering of the uninformative arms looked random.
- Process: pre-registered before data and run as written; the verdict stands as BOUNDARY even though the mechanism now explains it, because the class was fixed before the data. Run outside the loop's one-experiment-per-24h cap (EXP-62d ran the same morning) on Will's live instruction to continue (2026-10-19). The mechanism check is post hoc but reads fields logged since EXP-62, not a new measurement.
- Lesson: declare "uninformative" by measured information, not by what an arm looks like. Every arm logs how often its labels name the right action; an arm belongs in the zero class only if that rate equals chance for the label channel (1 in 5 here). A fake built from the student's own mistake inherits information from the schedule that produced the mistake.
- Next: EXP-62b (instrument dependence: three brains, equal-size early-vs-late teachers), as committed. For any later zero test, use the random-label null alone (exactly chance information) or a class whose label accuracy is measured at chance. For Noesis: worth is continuous near zero and roughly linear in information carried, so a payout rule should price small honest contributions rather than treat them as fakes (Desktop noesis-design-brainstorm-2026-10-19.md, idea 4).
