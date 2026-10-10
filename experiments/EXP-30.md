# EXP-30: over-teaching (does parent grading hurt at large budgets?)

- Date: 2026-10-09 | Cadence version: unrecorded | Program iter: iter19
- Script: `exp/EXP-30_overteaching.py` | Evidence: `exp/EXP-30.out`, `exp/EXP-30.json`

## Summary
- Question: is the EXP-28 drop of taught students at 600 trips (8/8 to 5/8) real over-drilling that grows with budget, or noise?
- Setup: same harness, parent and student seeds as EXP-28 (key-door, parent `exp24_brains/founder_2.npz`, 8 students). Teacher arm only; the world arm was not run (the output shows "world 0/0"). M = 300, 600, 1000, 1500 trips. Score = clean full-task pass (score >= 0.9).
- Prediction: "if the 600-trip drop (8/8 -> 5/8) grows with M, over-drilling is real; flat = the dip was noise." (script docstring, first line, written before running; the rest of the docstring is a stale copy of the EXP-28 prediction)
- Result: teacher pass at M=300 / 600 / 1000 / 1500 = 8/8, 5/8, 2/8, 1/8. The per-student scores at 300 and 600 reproduce EXP-28 exactly (same seeds). Counts only, no SEM.
- Verdict: SUPPORTIVE. Over-drilling is real and monotone in this setup; mechanism unknown. Not retracted.

## Reflection
- What it means: more parent grading is not always better; past a point it destroys the clean full-task pass. Design consequence recorded in the program log: cap teaching budgets, or pay on gain at the best stopping point, not on effort.
- Process: good: a direct follow-up of an anomaly with a written decision rule, and the shared budgets reproduced EXP-28 bit for bit (a free determinism check). Weak: no world-reward control at 1000 and 1500, so we cannot say whether long training of any kind degrades students or only parent grading does. One parent brain and 8 students. No mechanism probe (what the failing students actually do). The script is a near copy of EXP-28: its printed header still says "EXP-28 teacher vs world" and it saves brains to the same `e28_*` temp file names. Its JSON output defaults to `EXP-28.json` (env OUTJ), so a run without OUTJ set would have overwritten the EXP-28 evidence; `EXP-28.json` on disk still holds the EXP-28 data (it has the world arm and M=40 rows), so that did not happen here. Cadence version not stamped.
- Lesson: when reusing a script for a follow-up, keep the control arm on, and rename headers and temp paths so outputs cannot be confused.
- Next: the program log records the design consequence "cap teaching budgets, or pay on gain at the best stopping point, not on effort." Open and not queued in the sources: the mechanism, and a world-arm control at large M.
