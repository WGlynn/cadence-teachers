# EXP-73: M1b with the zero declared by measured information

- Date: pre-registered 2026-10-25 (not run) | Cadence version: record at run time (identity gate first, see Setup) | Program iter: iter47
- Script: `exp/EXP-73_m1b_measured_zero.py` (EXP-62's harness unchanged, through EXP-62d's as in EXP-62e; new zero class and analysis) | Evidence: `exp/EXP-73-full.*`

## Pre-registration (written 2026-10-25, before any EXP-73 data; Will's go 2026-10-25 21:43)

**Question.** Does transfer price skill on the delayed-credit brain when the zero is built only from arms whose labels are right at chance? And does the weakest real teacher still out-earn anti-echo, the one knowledge-free arm whose labels beat chance?

**Disclosure, read first.** This is the fifth zero-point attempt on this instrument (EXP-62, 62c, 62d, 62e), and EXP-62e's pre-registration said: "Whatever EXP-62e returns stands: no further zero-point redesign in this program." This run breaks that commitment, on Will's go. Why: EXP-62e's failure was traced, after the fact, to its declared class rather than its rule. anti-echo's labels name the right action .25 of the time against .20 for random labels, in all four runs. That is because labels only follow mistakes, so "any action but yours" removes one wrong option. EXP-62e's reflection already wrote the replacement rule (2026-10-19): "use the random-label null alone or a class whose label accuracy is measured at chance." Five things keep this from being "try until it passes". EXP-62e's BOUNDARY verdict stands as written. The 216 students are fresh. Every numeric threshold is kept from EXP-62e: margin 1/32, 2 SEM, pay share .10, know-4 .2, Spearman .3. The zero class is fixed by a measured property, and its check is fixed here. And anti-echo is not excused: it stays a knowledge-free arm, counts as a fake for pay, and must lose to know-1 by 2 SEM. Any crossing is reported with this history attached.

The strongest objection, answered here: anti-echo is the arm that failed EXP-62e's margin test, and this run takes it out of that test. Its replacement (know-1 beats anti-echo by 2 SEM) already passed at 4.1 SEM in EXP-62e. So this swaps a test anti-echo fails for one it is expected to pass. That swap is the redesign, and it is why the disclosure exists. The margin test asks whether a fake is worth less than half an answer. anti-echo is not, because it carries about a third of know-1's information edge. The replacement asks the market's question instead: does any knowledge-free arm out-earn the weakest real teacher? The pay cap still counts anti-echo. A reader who holds that any knowledge-free earning fails M1b should read a CONFIRM here as "crossed on the market question, not on the zero-worth question".

**Setup.** EXP-62's harness exactly (delayed-credit brain, weather chamber, corrective schedule, 20 attempts alone through `step`, per-state greedy accuracy over 16 states on unseen weather), lesson 80, **216 fresh students**, seeds 8_200_000 + student (disjoint from every earlier EXP-62 series run). Arms as EXP-62e: null, untaught, know-1..4, random, wrong-chain, echo, anti-echo.
- Identity gate before any data: EXP-62e's student 0 (seed 6_800_000) on the current version must reproduce its logged actions and labels in every arm. If it does, the run uses the current version. If not, the run uses tag v0.84.3 (`8dc92d8`), the version all four earlier runs used, and the difference is recorded.
- Zero Z = per-student mean of {null, untaught, random}. null and random are random-label teachers (labels right 1 time in 5 by construction); untaught gets no labels. Worth = arm minus Z on the same student.
- Zero admission check (on this run's logged labels): for null and random, the pooled share of labels naming the right action has a 95% binomial interval containing .20. If either fails, the verdict is VOID.
- Knowledge-free arms: null, untaught, random, anti-echo, wrong-chain, echo.
- Pay as EXP-62e: worth vs Z, batches of 6 students per arm, finalized iff batch mean > 0 and mean / SEM > 2.

**Prediction.** From EXP-62e's numbers re-expressed against this zero (not a result): know-1..4 near +.075 / +.15 / +.26 / +.42; untaught about +.013 (upper bound about +.023, the tightest margin); anti-echo about +.03; know-1 beats anti-echo by about 4 SEM. Expected: CONFIRM. Main risk: untaught's upper bound, from the abstain-vs-random-labels gap, reaching the 1/32 margin.

**Decision rules.**
- CONFIRM if all hold:
  1. know-1 < know-2 < know-3 < know-4 and Spearman(worth, k) >= .3 (n = 864);
  2. know-4 >= .2;
  3. non-superiority: for null, untaught, random, wrong-chain and echo, mean worth + 1.645 SEM < 1/32;
  4. know-1 beats each of null, untaught and random by at least 2 SEM, paired;
  5. know-1 beats anti-echo by at least 2 SEM, paired;
  6. all knowledge-free arms together (anti-echo included) take <= .10 of pay.
  Then M1b is crossed on instrument I (the delayed-credit brain) against a zero of measured-chance information. The claim carries its limits: one brain, one chamber, one lesson length; the default brain still does not take in content (EXP-52, EXP-61); a knowledge-free arm (anti-echo) earns about its information, a boundary for Noesis payout design.
- KILL: any knowledge-free arm's mean worth >= know-2's.
- VOID: the zero admission check fails.
- Anything else: BOUNDARY, failing criterion named. Also reported, not decisive: anti-echo's worth and pay share; EXP-62e's rule (zero including anti-echo) on the same data.

**Cost.** About an hour at 4 workers on an idle machine (EXP-62e: 216 students x 10 twins in 3,784 s). Starts after EXP-71 and EXP-72 finish.

## Summary
- Question: does transfer price skill on the delayed-credit brain against a zero built only from arms whose labels are right at chance, with the weakest real teacher still out-earning anti-echo?
- Setup: EXP-62's harness on Cadence v0.84.3 (identity gate IDENTICAL on EXP-62e student 0; the harness does not run on 0.85+, which refuses `working_memory_scale`). 216 fresh students (seeds 8_200_000+), lesson 80, 10 arms, zero = mean of {null, untaught, random}. 4,764 s at 4 workers (shared CPU).
- Prediction: see the pre-registration above (know-1..4 near +.075 / +.15 / +.26 / +.42; CONFIRM expected; main risk untaught's upper bound).
- Result: zero .439. know-1..4 +.057 / +.163 / +.269 / +.436 (SEM .010-.012), ordered, Spearman .638 (n 864). Zero admission: labels right .200 [.196, .204] (null, n 40,291) and .203 [.199, .207] (random, n 40,333): admitted. Margin upper bounds: null +.017, untaught +.014, random +.002, wrong-chain -.064, echo -.120 (all < .03125). know-1 beats null / untaught / random by 4.30 / 4.58 / 5.66 SEM and anti-echo by 4.0 SEM (anti-echo worth +.014, SEM .009; its labels right .253). Knowledge-free arms take .023 of pay. No kill.
- Reported, not decisive (as pre-registered): EXP-62e's original rule on the same data (zero including anti-echo, anti-echo inside the margin test) also gives CONFIRM: anti-echo upper bound +.021 against .031, know-1 beats anti-echo by 3.99 SEM, fake pay .013.
- Verdict: CROSSED (CONFIRM by the pre-registered rule): M1b on instrument I (the delayed-credit brain, Cadence v0.84.3) against a zero of measured-chance information.

## Reflection
- What it means: the skill price replicates a fifth time on a fifth disjoint student set, and this time every criterion holds. M1b is crossed on one instrument. Limits, unchanged by the crossing: one brain (delayed-credit), one chamber, one lesson length, a pinned old Cadence (v0.84.3; the harness needs a port to run on current releases); the default brain still does not take in content (EXP-52, EXP-61); anti-echo, which needs no task knowledge, still earns a little (+.014), in proportion to the information the corrective schedule leaks to it.
- Process: this was the fifth zero-point attempt and broke EXP-62e's "no further redesign" commitment, on Will's go, disclosed before data. The decisive check of that history came out in its favour and against its necessity at once: EXP-62e's original rule also passes on this data. So the crossing does not depend on the redesign. A fresh draw passed the old rule too, and EXP-62e's .002 miss was sampling noise around a real but small anti-echo edge. The new rule passes with wide margins; the old one sits near its noise floor on anti-echo.
- Lesson: when a near-miss is followed by a rule change, also score the new data under the old rule. If both pass, the rule change was not doing the work, and saying so is the honest report.
- Next: port the EXP-62 harness to the current Cadence API and re-cross on a current release (otherwise M1b is pinned to v0.84.3); then the next rung (instrument dependence, EXP-62b line) on the current API.
