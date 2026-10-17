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
PENDING (after the run)

## Reflection
PENDING (after the run)
