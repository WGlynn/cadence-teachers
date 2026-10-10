# EXP-39: teaching a prerequisite chain (the "Stone Age COLD" problem)

- Date: 2026-10-10 | Cadence version: 0.80.0 (`19bee92`) | Program iter: iter30 (pending)
- Script: `exp/EXP-39_prerequisite_chain.py` | Evidence: `exp/EXP-39-full.out`, `exp/EXP-39-full-B*.json/.jsonl`, pilot `exp/EXP-39-pilot-B*.jsonl`

## Summary
- Question: a developer reported that Cadence collapses onto one action instead of learning gather wood -> gather stone -> craft fire -> warm up. Does putting the inventory in the observation, grading every move, and teaching backwards (our advice, based on a 2-step chain) fix a 4-step chain?
- Setup: inventory state (wood, stone, fire), 4 actions, at most 8 moves per episode; Cadence brain at the key-door protocol-3 operating point living through `step`; budgets B = 40 / 150 / 500 / 1500 episodes; 12 seeds; arms SPARSE-FWD, SPARSE-BWD, GRADE-FWD, GRADE-BWD, GRADE-BWD-BLIND (see the script docstring). Test: a frozen copy acts greedily from empty; success = warmed up within 6 moves; policy accuracy over the 5 reachable states.
- Prediction (pre-registered; revised after the 4-seed pilot, before the full run): "GRADE-FWD >= GRADE-BWD at B=40 (dense grading makes backward starts unnecessary); both graded arms solve >= 11/12 from B=150. SPARSE-BWD stays near 0/12 at every budget and collapses onto WARM/CRAFT (the reported failure mode, caused by the reverse curriculum under sparse reward); SPARSE-FWD rises only at the largest budget (6-11/12 at B=1500). BLIND 0/12 everywhere."
- Result: PENDING (full run in progress).
- Verdict: PENDING.

## Reflection
- PENDING (written when the run finishes).
