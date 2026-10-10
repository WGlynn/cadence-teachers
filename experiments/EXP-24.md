# EXP-24: Calibrate teaching strategies on key-door parent grading

- Date: 2026-10-09 | Cadence version: unrecorded (iter17 carries no stamp; iter16 and iter25 both stamp 0.78.0 / 750c8ef) | Program iter: iter17
- Script: `exp/EXP-24_strategy_calibration.py` | Evidence: `exp/EXP-24-M40.out`, `exp/EXP-24-M40.json`, `exp/EXP-24-M100.out`, `exp/EXP-24-M100.json`

## Summary
- Question: do different grading STRATEGIES (same parent skill) teach the key-door task to a child at different rates, so that teaching ability could be a trait selection acts on?
- Setup: key-door corridor (EXP-19/22 harness), parent grades every child step (reward "match" if the child copies the parent's greedy move, penalty "miss" otherwise). 4 passing founder parents (first 4 of candidates 2-7 with fed score >= 0.9), 3 student seeds per parent = 12 students per strategy, pass = test_fed >= 0.9. Strategies: plain, harsh, soft, nofloor, door-drill (start holding the key 40% of trips), and reward strength variants faint (0.2), mid (0.5), strong (2.0). Two budgets: M=100 and M=40 teaching trips. The M=100 run had only the first 6 strategies (mid and strong are absent from its .out and .json; why they were missing, and whether they were added to the script later, is not recorded).
- Prediction: none written before running. The docstring only states a decision rule: "If child pass rate varies by strategy, teaching ability is a real trait that selection can act on (EXP-25)."
- Result: M=100: plain, harsh, soft, nofloor, door-drill 12/12 each; faint 6/12. M=40: plain, harsh, soft, nofloor, door-drill, strong 12/12 each; mid 11/12; faint 6/12. No SEM computed; 12 students per strategy, one set of 4 parents.
- Verdict: NULL (at ceiling). Program log iter17: "Key-door is too easy to teach: per-step grading + visible key = a lookup. Not a usable teaching trait." Not later retracted; the teaching-trait search moved to EXP-26 (tutor focus).

## Reflection
- What it means: on key-door with per-step parent grading, the grading SHAPE (harsh vs soft, floor grading, door drilling) makes no visible difference; only reward strength matters, and only when it is weak (0.2 gives 6/12, 0.5 gives 11/12 at 40 trips, 1.0 and above gives 12/12). Per-step grading against a parent who sees the key turns teaching into copying a lookup table, so there is no room for teaching skill to show.
- Process: the effect window was at ceiling: 12/12 for most arms even at the smaller 40-trip budget, so the experiment could not separate strategies. The two budgets were not run with the same strategy set (M=100 lacks mid and strong), so the budget comparison is only partial. No prediction was written before the run, although iter17 introduced that rule. Small samples (12 per arm, 4 parents) with no SEM, though at 12/12 that hardly matters.
- Lesson: before asking whether strategies differ, check that the task leaves headroom at the chosen budget; a task where any reasonable teacher scores 100% cannot reveal a teaching trait.
- Next: look for a skill that is genuinely hard to teach (EXP-25 memory door), then a trait that is invisible to the teacher's own doing (EXP-26 tutor focus).
