# EXP-12d: Settle-budget sweep to tell credit starvation from a fundamental XOR failure

- Date: 2026-10-08 | Cadence version: 0.78.0 | Program iter: iter7
- Script: `exp/EXP-12d_xor_credit_discriminator.py` | Evidence: `exp/EXP-12d-discriminator.out` (incomplete: only the settle_budget 48 row printed; the program log records "exp/EXP-12d (timeout)")

## Summary
- Question: is the deep-XOR 0.00 of EXP-12c caused by too little settling (credit not reaching the front column), which Dongyang's method would make cheap, or is it fundamental?
- Setup: deep P6-H6 held fixed, 3000 XOR steps, seeds 7, 11, 23, settle_budget planned at 48, 120 and 240, plus a per-context action dump for seed 7 at budget 240.
- Prediction: written before running, in the docstring: "0.00 is the signature of the front (perception) column never learning the bit-features" and "If XOR acc RISES with budget -> credit-starvation confirmed -> deep synergy needs cheap-deep-credit = Dongyang's method is directly our lever. If it stays ~0 at large budget -> not a settling problem."
- Result: settle_budget 48: 0.00, 0.00, 0.00 (mean 0.00), repeating EXP-12c at more steps. Budgets 120 and 240 and the action dump: not recorded (the run timed out).
- Verdict: VOID (did not complete) and SUPERSEDED by EXP-12e (action dump at budget 48, 1500 steps, 3 seeds: all `None`; a deep copy-b1 control learns to 1.00 on seeds 7 and 11) and EXP-12f (budgets 100 and 220, 800 steps, 1 seed: 0% None, constant action [0,0,0,0], acc 0.50). The prediction's premise was wrong: the 0.00 was no action at all, and adequate settling did not produce XOR. iter7 verdict: Dongyang's speedup is not our lever.

## Reflection
- What it means: on its own, nothing beyond confirming that settle_budget 48 gives 0.00 at 3000 steps. Its question was answered by the smaller follow-ups.
- Process: 3 budgets x 3 seeds x 3000 steps at large settle budgets was too expensive and timed out. The diagnostic that mattered (the action dump) was only taken for seed 7 at budget 240, so it needed the whole budget 120 row and a 3000-step budget 240 run to finish first, and it never ran. The hypothesis was built on the EXP-12c misreading (`None` counted as wrong).
- Lesson: run the cheap diagnostic first (dump actions, measure the None-rate) and the expensive sweep only after it; order cells so a timeout still leaves the decisive number.
- Next: EXP-12e (cheap action dump, polarity check and copy-b1 control) and EXP-12f (lean 1-seed budget unlock with None-rate tracking).
