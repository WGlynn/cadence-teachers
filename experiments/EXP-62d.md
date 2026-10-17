# EXP-62d: pooled zero with a noise allowance and a separation test

- Date: 2026-10-17 (pre-registered; to run at the next loop fire) | Cadence version: record at run time | Program iter: iter38
- Script: to be `exp/EXP-62d_pooled_zero.py` (EXP-62's harness; analysis adds the pooled zero) | Evidence: `exp/EXP-62d-full.*`

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
PENDING (after the run)

## Reflection
PENDING (after the run)
