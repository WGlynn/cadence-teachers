# EXP-12b: XOR-ceiling search over depth and width

- Date: 2026-10-08 | Cadence version: 0.78.0 | Program iter: iter7
- Script: `exp/EXP-12b_xor_ceiling.py` | Evidence: `exp/EXP-12b-ceiling.out` (incomplete: only the first of five configs printed)

## Summary
- Question: is there an architecture and training budget where the equilibrium Reinforcement creature learns XOR from scratch to about 1.0, giving the synergy probe a usable ceiling?
- Setup: same factored c1/c2/cue creature as EXP-12, settle_budget 64. Five configs planned: shallow P6, shallow P12, deep P6-H6, deep P8-H8, deep P12-H12 (deep adds a hidden column between perception and policy). 2000 XOR steps, seeds 7, 11, 23.
- Prediction: none written before running. The docstring gives the decision rule: "If some config hits ~1.0 reliably, that is the substrate for the synergy harness. If nothing clears ~0.8 across seeds, that is the honest boundary: this substrate cannot cleanly represent XOR."
- Result: only shallow P6 completed: per-seed 0.25, 0.75, 0.50, mean 0.50. The other four configs are not recorded (the output stops after the first row; the program log cites the script without an .out, and the deep configs were rerun separately as EXP-12c).
- Verdict: NULL for the one config that finished (shallow P6 at chance, mean 0.50 over 3 seeds). The rest of the planned search did not complete and was SUPERSEDED by EXP-12c (deep configs) and finally by the iter7 verdict from EXP-12e/12f and EXP-14/14b (XOR not learned on any architecture tried).

## Reflection
- What it means: going from 800 to 2000 steps and adding seeds did not move shallow XOR off chance. It answered nothing about depth or width because those rows never ran.
- Process: the run did not finish and the cause (timeout or kill) is not recorded. A likely reason is size (five configs x 3 seeds x 2000 steps), but that is an inference, not a recorded fact. The program log lists only the script for EXP-12b, not the .out, and still cites "shallow 2-col caps ~0.50 (EXP-12/12b)" from this single row. The one completed row agrees with EXP-12. The None-rate was not measured.
- Lesson: size a sweep to the time actually available, print each row as it lands (it did), and record when and why a run was cut short.
- Next: EXP-12c reran only the deep configs, with settle_budget lowered to 48.
