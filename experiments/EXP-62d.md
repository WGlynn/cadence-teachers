# EXP-62d: pooled zero with a noise allowance and a separation test

- Date: pre-registered 2026-10-17, run 2026-10-19 | Cadence version: v0.84.3, main `8dc92d8` (`~/_cadence_study`); run gate below | Program iter: iter38
- Script: `exp/EXP-62d_pooled_zero.py` (EXP-62's harness unchanged; analysis adds the pooled zero) | Evidence: `exp/EXP-62d-full.*`, run gate `exp/GATE62-v0843-full.jsonl`

## Pre-registration (written 2026-10-17, before any EXP-62d data)

**Question.** With the zero set as the pooled mean of a declared uninformative class and fakes judged with a noise allowance, does transfer price skill on the content-taking brain on fresh students?

**Why.** EXP-62 and EXP-62c both met every criterion except "every fake mean <= 0" measured against a single fake as zero. EXP-62 failed it with anti-echo high (+.023); EXP-62c failed it with anti-echo low (random +.027, abstain +.032 above it). The uninformative arms form a band about +-.03 wide at n = 72 whose order shuffles between runs, so that rule is a max-of-noisy-estimates test that fails by chance. This replaces it, stated before seeing new data. This is a redesign after two BOUNDARY results and is labelled as such.

**Setup.** EXP-62's harness exactly (delayed-credit brain, weather chamber, corrective schedule, 20 attempts alone through `step`, per-state greedy accuracy on unseen weather), lesson 80, 72 fresh students (seeds 6_600_000 + student, disjoint from all earlier runs). Arms: null, untaught, know-1..4, random, wrong-chain, echo, anti-echo.
- Zero Z = per-student mean accuracy of the declared uninformative class {null, untaught, random, anti-echo}. Worth = arm minus Z on the same student.
- Pay: worth vs Z, batches of 6 students per arm, finalized iff batch mean > 0 and mean / SEM > 2; fake pay share = pay to {null, untaught, random, anti-echo, wrong-chain, echo} / total.

**Prediction.** From EXP-62c re-read against the pooled zero (exploratory): know-1..4 about +.055 / +.145 / +.283 / +.418, uninformative arms within +-.02, wrong-chain about -.09, echo about -.11, know-1 above every uninformative arm by 2.2 to 3.6 SEM paired. Expect CONFIRM. Main risk: the separation test (know-1 vs random / untaught was only 2.2 / 2.3 SEM in EXP-62c).

**Decision rules.**
- CONFIRM if all hold: know-1 < know-2 < know-3 < know-4 and Spearman(worth, k) >= .3 (n = 288); know-4 >= .2; no fake (uninformative or misleading) has mean worth above 0 by more than 2 SEM; know-1 beats every uninformative arm by at least 2 SEM, paired; fakes take <= .10 of pay. Then M1b is crossed: transfer prices skill on instrument I (delayed-credit brain) against zero N (the pooled uninformative class).
- KILL: any fake's mean worth >= know-2's.
- Anything else: BOUNDARY, failing criterion named.

## Summary
- Question: with the zero set as the pooled mean of a declared uninformative class and fakes judged with a noise allowance, does transfer price skill on the content-taking brain on fresh students?
- Setup: EXP-62's harness, lesson 80, 72 fresh students (seeds 6_600_000 + student), zero = per-student mean of {null, untaught, random, anti-echo}. Run 1,191 s at 4 workers on v0.84.3. Run gate before the run: the harness reproduced EXP-62c's students 0 and 1 (run on `6499e56`) bit-identically on `8dc92d8`, actions and labels in all 10 arms, so the version bump between pre-registration and run does not touch this instrument.
- Prediction (written before the run): know-1..4 about +.055 / +.145 / +.283 / +.418, uninformative arms within +-.02, CONFIRM; main risk the separation test.
- Result: zero = .458. know-1..4 +.070 / +.140 / +.249 / +.421 (SEMs .016-.020), ordered, Spearman .636 (n 288). Uninformative arms: null -.017 (SEM .013), random -.017 (.012), anti-echo +.005 (.011), **untaught +.029 (SEM .011, 2.57 SEM)**. Misleading: wrong-chain -.089, echo -.172. Separation (paired): know-1 beats null by 4.4 SEM, random 3.9, anti-echo 3.3, untaught 2.07. Fake pay share .007 (anti-echo .007; untaught never finalized a batch).
- Criteria: ordered + Spearman yes; know-4 >= .2 yes; no fake above zero by more than 2 SEM **NO (untaught)**; know-1 beats every uninformative arm by 2 SEM yes; fake pay <= .10 yes. No kill.
- Exploratory (not pre-registered): pooling EXP-62, 62c and 62d at lesson 80 (216 students, same harness, three disjoint seed sets) under this rule, every uninformative arm sits within +-.015 of the zero (largest +1.40 SEM, anti-echo), know-1 is +.065 (7.2 SEM) and beats every uninformative arm by at least 4.7 SEM. The pairwise gaps among uninformative arms change sign between runs (untaught minus anti-echo: -.061, +.032, +.024), and pooled, untaught minus the random-label arms is about +.018.
- Verdict: BOUNDARY (4/5, the zero-point criterion, failed this time by abstain).

## Reflection
- What it means: the skill price replicates a third time on a third disjoint set of students, with the tightest ladder yet (Spearman .64) and the separation test passing: the weakest genuine teacher beats every uninformative arm. What still fails is the zero-point criterion, and a different arm trips it each run (anti-echo high in EXP-62, random and abstain high against anti-echo in EXP-62c, abstain high against the pool here). Pooled over 216 students the uninformative arms are equal to within +-.015. So the instrument separates skill from noise, but at n = 72 the uninformative arms do not stay inside 2 SEM of one another, and a 2-SEM rule over four of them will keep catching one.
- Process: pre-registered before data and run as written; the version-bump gate removed the one confound that arose between pre-registration and run. The weak point is the decision rule's power, not the measure, and three successive rule redesigns after three BOUNDARYs is itself a forking-paths risk. So the next run must not change the rule again, only add students. The 216-student pooled read is post hoc (the rule was written after two of those three runs were seen) and is labelled exploratory; it does not cross M1b.
- Lesson: a significance test that a fake is positive is the wrong test for 'the fake is worth nothing that matters'. Within-student permutation of the real data (arms made equal in truth) shows the 2-SEM rule over this four-arm class false-fails about 9% of the time at n 72 and at n 216 alike, and any small real gap (abstain vs random labels pools to about +.02) makes it fail more as n grows. The right test is non-superiority against a declared margin, powered for the whole class. Decide that before the data, once.
- Next: EXP-62e (pre-registered in experiments/EXP-62e.md): 216 fresh students (seeds 6_800_000+), the same zero, and a non-superiority margin of 1/32 (half of one of the 16 states) on every fake's upper bound; under exact equality it false-fails about 1% at n 216. Declared the last zero-point redesign; EXP-62b (instrument dependence) follows either way.
