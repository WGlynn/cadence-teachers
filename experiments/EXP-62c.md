# EXP-62c: price against the best fake in a declared class (fresh seeds)

- Date: 2026-10-17 | Cadence version: 0.83.0 + Unreleased, main `6499e56` (`~/_cadence_study`) | Program iter: iter37
- Script: `exp/EXP-62c_best_fake_zero.py` (runs EXP-62's harness unchanged under declared settings) | Evidence: `exp/EXP-62c-full.*`

## Pre-registration (written 2026-10-17 before the run)

**Question.** With the committed zero declared in advance as the best fake in a declared class, does measured transfer price skill on the content-taking brain, on students it has never seen?

**Why.** EXP-62 (BOUNDARY 4/5) failed only its zero-point criterion: anti-echo (label anything except the action that just failed) priced at +.023 against the random-label null, and worth tracked label correctness across all arms (r .99). The corrective schedule fires only after a mistake, so it tells any labeller which action was wrong. The declared class is "labellers that see only what the schedule gives them"; anti-echo is the best member of that class (uniform over the actions not yet ruled out). Setting the zero there fixes the zero point by argument, not by fitting.

**Setup.** EXP-62's harness exactly (delayed-credit brain, weather chamber, corrective schedule, 20 attempts alone through `step`, per-state greedy accuracy on unseen weather), with:
- committed zero CF = anti-echo (declared now, no pooled rule);
- lesson length 80, chosen from EXP-62's full data before this run (know-4 mean accuracy .845 at 80 over 72 students, under the .90 ceiling; larger know-k steps than at 40);
- 72 fresh students, seeds 6_400_000 + student (disjoint from EXP-62's 6_200_000 + student and its pilot);
- arms: null, untaught (= abstain), know-1..4, random, wrong-chain, echo, anti-echo. Fakes for the criteria: random, wrong-chain, echo, abstain (anti-echo is the zero).
- pay: batches of 6 students per teacher, finalized iff batch mean worth > 0 and mean / SEM > 2.

**Prediction.** EXP-62's lesson-80 data re-scored against anti-echo (exploratory, those were seen students) gave know-1..4 +.028 / +.089 / +.203 / +.359, Spearman .529, random -.082, wrong-chain -.122, echo -.163, abstain -.061: CONFIRM on all five criteria. On fresh seeds I expect the same shape: CONFIRM, with know-1 near zero (about +.03) as the weakest point; the ordering know-1 < know-2 is the main risk.

**Decision rules (same as EXP-62, with the zero declared):**
- CONFIRM if all hold: know-1 < know-2 < know-3 < know-4 and pooled Spearman(worth, k) >= .3 (n = 288); know-4 >= .2 against anti-echo; every listed fake (random, wrong-chain, echo, abstain) has mean <= 0; fakes take <= .10 of pay. Then M1b is crossed: transfer prices skill on instrument I (delayed-credit brain) against zero N (best fake in the declared schedule-only class).
- KILL: any listed fake's mean worth >= know-2's mean worth.
- Anything else: BOUNDARY, with the failing criterion named.

## Summary
- Question: with the zero declared in advance as the best fake in the schedule-only class (anti-echo), does transfer price skill on the content-taking brain on fresh students?
- Setup: EXP-62's harness, lesson 80, 72 fresh students (seeds 6_400_000 + student), committed zero = anti-echo; fakes random, wrong-chain, echo, abstain. Run 1,339 s.
- Prediction: CONFIRM (from EXP-62's lesson-80 data re-scored against anti-echo), weakest point know-1 near zero. Missed: the zero itself came in low.
- Result: know-1..4 +.073 / +.162 / +.300 / +.436 (SEMs .017-.022), ordered; Spearman .612 (n 288); wrong-chain -.071, echo -.095; random +.027 (SEM .021), abstain +.032 (SEM .022); fake pay .034 (random .012, abstain .022). Anti-echo accuracy .423 vs null .435 vs untaught .455: anti-echo fell BELOW the random-label null this time (-.012), where in EXP-62 it sat above it (+.023 at 40, +.031 at 80).
- Criteria: ordered yes, Spearman yes, know-4 >= .2 yes, every fake <= 0 NO (random, abstain), fake pay <= .10 yes; no kill.
- Exploratory (same data): know-1 beats every uninformative arm, paired: random +.046 (2.2 SEM), untaught +.041 (2.3), null +.061 (3.2), anti-echo +.073 (3.6). Against a pooled zero (mean of null, untaught, random, anti-echo) every uninformative arm sits within +-.02 (<= 1.4 SEM) and know-1 is +.055 (SEM .015).
- Verdict: BOUNDARY (4/5, the zero-point criterion again, this time failed from the other side).

## Reflection
- What it means: the skill price replicates on fresh students and is the strongest yet (Spearman .61; even know-1 clears every uninformative arm by more than 2 SEM). What did NOT replicate is EXP-62's reading that anti-echo carries a measurable extra bit: on fresh seeds it priced below the null. The uninformative arms (null, untaught, random, anti-echo) form a band about +-.03 wide at n = 72, and their order shuffles between runs. So the zero point is fuzzy at that scale, and no single fake is a stable zero.
- Process: the decision rule was the weak part. "Every fake mean <= 0" against one noisy fake as zero is a max-of-noisy-estimates test: when the fakes are equal in truth, a zero that draws low makes all of them look positive, so it fails often by chance. EXP-62 failed it with anti-echo high; EXP-62c failed it with anti-echo low. That is a criterion design flaw, recorded here; it does not change either verdict. The exploratory paired and pooled reads are post hoc.
- Lesson: set the zero as the pooled mean of a declared uninformative class, not a single fake, and test fakes against it with a noise allowance (no fake above zero by more than 2 SEM) plus a separation test (the weakest genuine contributor beats every fake by 2 SEM, paired). A point-estimate "every fake <= 0" rule needs far more students than the effect it is guarding.
- Next: EXP-62d pre-registered now with that criterion, on fresh seeds, queued for the next loop fire (not run today).
