# EXP-12f: does more settling budget unlock deep XOR under RL

- Date: 2026-10-08 | Cadence version: 0.78.0 (commit not recorded in the iter7 entry) | Program iter: iter7
- Script: `exp/EXP-12f_xor_budget_unlock.py` | Evidence: `exp/EXP-12f-unlock.out`

## Summary
- Question: if the deep creature gets more settling budget, does it stop returning None on XOR, start getting feedback, and learn XOR (which would make Dongyang's cheap-deep-settling method our lever)?
- Setup: same deep creature as EXP-12e (P6-H6, fan_in 9, tolerance 1e-3), XOR under RL reward, settle_budget in {100, 220}, 1 seed (7), 800 steps. Instrumented the None rate in the first and second half of training, then final greedy actions and acc.
- Prediction: written in the docstring before running: "None-rate drops with budget AND acc climbs => settling-bound => Dongyang's cheap-settling IS our lever" versus "None-rate stays ~1.0 at high budget => XOR un-settleable on this arch ... NOT our lever."
- Result: settle_budget 100: None 0% (first half), 0% (second half), final actions [0, 0, 0, 0], acc 0.50. settle_budget 220: identical, None 0% / 0%, actions [0, 0, 0, 0], acc 0.50. Single seed, no SEM.
- Verdict: SUPPORTIVE (1 seed) of "settling was not the wall": neither pre-written branch occurred; None vanished but the creature collapsed to a constant action. Its RL-only caveat was then closed and the conclusion SUPERSEDED by EXP-14/14b (supervised training also fails to fit XOR), which form the iter7 final verdict.

## Reflection
- What it means: the None in EXP-12e was a settling-budget artifact of sb=48. With adequate settling the creature trains, but under this RL reward it settles on always answering 0, which scores exactly chance on XOR. So faster settling would not help: Dongyang's speedup is not our lever for synergy.
- Process: (1) One seed and one step count (800, shorter than EXP-12e's 1500); the iter7 log itself flags the sb100/220 rows as 1 seed and not robust. (2) The outcome fell outside both pre-written branches, so the decision had to be made on an unplanned third outcome; the docstring should have listed "None drops, acc stays at chance". (3) RL hyperparameters (reward_scale 4.0, exploration 0.1, discount 0.0, batch 4) were untuned, so this alone could not separate "cannot represent XOR" from "RL reward cannot teach it"; that is why EXP-14 was needed. (4) Greedy probes reset after each act but not before the first (pre iter8 #164 fix); not rerun after the fix. (5) The None rate at sb=48 during training was never measured, so "budget fixed the None" rests on comparing the final probe of EXP-12e to the training rate here.
- Lesson: write all plausible outcomes into the decision rule, including "the blocker disappears but nothing improves"; a removed blocker is not the same as a working mechanism.
- Next: led to EXP-14 (supervised XOR) to separate a representation wall from an RL-teaching failure.
