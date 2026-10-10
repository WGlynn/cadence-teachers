# EXP-12c: Does depth let the equilibrium creature learn XOR?

- Date: 2026-10-08 | Cadence version: 0.78.0 | Program iter: iter7
- Script: `exp/EXP-12c_xor_deep.py` | Evidence: `exp/EXP-12c-deep.out`

## Summary
- Question: does adding a hidden column (perception, then hidden, then policy) let the creature learn XOR, and so is Dongyang's deep-settling speedup a relevant lever?
- Setup: deep configs P6-H6, P8-H8, P12-H12; settle_budget 48 (lowered from 64); policy reads hidden + cue. 2000 XOR steps, seeds 7, 11, 23. Greedy accuracy over 4 contexts, with a `None` action counted as wrong.
- Prediction: none written before running. The docstring gives only the reading rule: "a clean ~1.0 means depth represents XOR, a stuck ~0.5 means this substrate/rule can't and synergy needs a different design."
- Result: P6-H6 per-seed 0.00, 0.00, 0.00 (mean 0.00); P8-H8 0.00, 0.00, 0.00 (mean 0.00); P12-H12 0.50, 0.00, 0.00 (mean 0.17).
- Verdict: SUPERSEDED in interpretation. iter7 first read the 0.00 as "systematically wrong, the signature of the front/perception column never learning". EXP-12e then showed the deep P6-H6 creature returns action `None` on every context at settle_budget 48 (3 seeds, 1500 steps; it never qualifies an action, so it never trains), and EXP-12f showed that at settle_budget 100 and 220 (1 seed, 800 steps) it acts but collapses to a constant action (acc 0.50). The None reading is inferred from those separate runs, not from an action dump of the EXP-12c creatures themselves; P12-H12 seed 7 scored 0.50 here, so not every EXP-12c creature was necessarily all-None. The numbers stand; the "front layers never learn" reading was wrong. Final XOR status per iter7 (with EXP-14/14b): not learned on any architecture tried.

## Reflection
- What it means: going deep at settle_budget 48 looked worse than shallow, but for a mechanical reason (no settled action), not a learned wrong mapping. Depth did not unlock XOR.
- Process: the accuracy metric mixed "chose the wrong action" with "chose no action", which produced a misleading 0.00 and a plausible but wrong mechanism story that then motivated EXP-12d. settle_budget was changed from 64 (EXP-12/12b) to 48 at the same time depth was added, so two knobs moved at once. 3 seeds, 4 contexts per eval.
- Lesson: when accuracy is below chance, dump the raw actions before building a theory, and count `None` separately from wrong.
- Next: EXP-12d (settle_budget sweep as a credit-starvation test), then the action dump in EXP-12e.
