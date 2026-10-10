# EXP-14: can the equilibrium substrate learn XOR with supervised training

- Date: 2026-10-08 | Cadence version: 0.78.0 (commit not recorded in the iter7 entry) | Program iter: iter7
- Script: `exp/EXP-14_xor_supervised.py` | Evidence: `exp/EXP-14-supervised.out`

## Summary
- Question: is the XOR failure under RL (EXP-12f) a representation wall of the substrate, or just RL reward failing to teach it? Test with supervised `bootstrap` on labeled (input, target) pairs.
- Setup: equilibrium Cortex, fan_in 9, parameter_prior 0.3, tolerance 1e-3, settle_budget 96. `bootstrap` with max_error 0.3, epochs 60, checks = the same 4 points (representability test, no held-out set). Control: copy-b1 shallow P6, seeds 7, 11. XOR shallow (perception -> response): P in {4, 6, 12}, seeds 7, 11. XOR deep (perception -> hidden -> response): (P, H) in {(6, 6), (12, 12)}, seeds 7, 11.
- Prediction: written in the docstring before running, as a decision rule: "If XOR passes and predicts correctly -> the substrate CAN represent XOR; RL reward was the blocker ... If bootstrap won't converge / predicts wrong -> XOR is genuinely hard for this substrate, and the XOR-channel synergy design needs replacing." Control "must pass if harness is sane".
- Result: control copy-b1: passed=True, acc 1.00 on both seeds (preds 0.08/0.06/0.81/0.81 and 0.14/0.04/0.88/0.86). XOR shallow: passed=False and acc 0.50 on all 6 runs; seed 7 preds about -0.14/-0.10/0.04/0.10, seed 11 preds about 0.94/0.95/0.90/0.92, essentially identical across P 4, 6 and 12. XOR deep: the first deep run (P6-H6, seed 7) crashed at predict with SettlementError (stationarity 0.00246297 vs tolerance 0.001 at 96 sweeps), and the script stopped, so the other 3 deep runs never ran.
- Verdict: shallow half NULL (supervised training does not fit XOR on the shallow wiring; this stands). Deep half VOID (crash, no data), SUPERSEDED by EXP-14b, which reran deep with more settling budget.

## Reflection
- What it means: the shallow XOR failure is not an RL artifact; supervised training with a passing control also fails. The shallow creature outputs a near-constant or weakly linear response, which is what a model without a two-bit interaction produces on XOR.
- Process: (1) Bug: only `bootstrap` was wrapped in try/except, not `predict`, so one settle failure killed the remaining deep runs; fixed in EXP-14b. (2) Width P had essentially no effect (same seed gives nearly the same preds at P4, P6 and P12), which was not investigated; it may mean extra patches are not being used under fan_in 9, so the "width sweep" is weaker evidence than it looks. (3) Two seeds per cell and fixed hyperparameters (epochs 60, max_error 0.3, parameter_prior 0.3); no sweep of training length. (5) The docstring promised a "linear-vs-XOR contrast" control; only copy-b1 was run. (4) The deep crash had stationarity 0.00246, about 2.5x the 0.001 tolerance, which the EXP-14b docstring called "CLOSE to converged"; that reading motivated the (later falsified) hypothesis that deep XOR was only settling-limited.
- Lesson: wrap every call that can raise in a sweep, not just the training call, or one failure silently truncates the experiment.
- Next: led to EXP-14b (deep XOR supervised with settle_budget 256 and 512).
