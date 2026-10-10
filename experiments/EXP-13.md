# EXP-13: profile the settle bottleneck (speed vs settle_budget on a shallow creature)

- Date: 2026-10-08 | Cadence version: 0.78.0 (commit not recorded in the iter7 entry) | Program iter: iter7
- Script: `exp/EXP-13_settle_profile.py` | Evidence: `exp/EXP-13-profile.out`

## Summary
- Question: on our shallow creatures, how much per-step time does settling cost, and does cadence's existing settle_budget knob already buy most of the available speedup without hurting learning?
- Setup: equilibrium Reinforcement creature, 2 columns (perception P=6 -> policy 2), fan_in 9, tolerance 1e-3, seed 7. Task copy-b1 (4 contexts), 300 RL steps. settle_budget swept over 64, 32, 16, 8, 4, 2. Measured ms per training step (one wall-clock run each) and copy-b1 greedy accuracy after training.
- Prediction: the docstring states a decision rule but no expected outcome: "If low settle_budget is ~as accurate and much faster, that is the 1-line speedup and Dongyang's algorithmic port is unnecessary at our depth. If accuracy collapses as budget drops, the sweeps are load-bearing and the linearised mode is worth porting." No prediction of which branch was written.
- Result: sb64 18.8 ms, acc 1.00 | sb32 17.9 ms, 1.00 | sb16 13.8 ms, 1.00 | sb8 7.6 ms, 0.50 | sb4 4.3 ms, 0.50 | sb2 1.8 ms, 0.25. One seed, one timing run per row, no SEM. The program log summarizes this as 64 -> 16 = 1.36x free, with a correctness floor near 16 sweeps.
- Verdict: SUPPORTIVE (1 seed): at our shallow depth the existing knob gives about 1.36x at no accuracy cost, and Dongyang's method is not needed for shallow creatures. Not retracted. Whether sb16 was then adopted as a default is not recorded.

## Reflection
- What it means: settling is not a large lever at 2 columns. Going from 64 to 32 sweeps barely changes time (18.8 vs 17.9 ms), which suggests the solve usually hits tolerance well before 64 sweeps, so the budget above that is unused. Below 16 sweeps the creature stops working.
- Process: (1) One seed and one timing sample per row on a shared machine; ms numbers carry unmeasured noise. (2) copy-b1 is an easy task at ceiling (1.00), so it can only detect collapse, not a mild quality loss. (3) Accuracy has 0.25 resolution (4 contexts), and the scorer counts a None action as wrong; the same low budget is used in both training and the eval probe, so the 0.50 / 0.25 rows cannot tell "did not learn" from "learned but could not settle to an action at probe time". (4) Probes are not reset before the first one (pre iter8 #164 fix). (5) The ms/step timer covers whole training steps, and a step whose action is None skips feedback and is cheaper; the None rate during training was not recorded, so the timings at the low budgets (8, 4, 2) may partly reflect skipped feedback rather than cheaper settling. (6) Only the 2-column wiring was profiled; deep stacks, where Dongyang's method applies, were not timed.
- Lesson: profile the actual bottleneck before porting someone else's speedup; on this substrate the free knob covered the shallow case.
- Next: fed the iter7 verdict that Dongyang's speedup is not our lever at shallow depth; the deep case was then examined via EXP-12e/12f and EXP-14b.
