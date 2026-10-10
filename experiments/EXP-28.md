# EXP-28: teacher vs world (is teaching redundant for key-door?)

- Date: 2026-10-09 | Cadence version: unrecorded | Program iter: iter18
- Script: `exp/EXP-28_teacher_vs_world.py` | Evidence: `exp/EXP-28.out`, `exp/EXP-28.json`

## Summary
- Question: do Cadence brains learn the key-door task as well from the world's own reward as from parent grading, at matched trip budgets?
- Setup: key-door corridors (EXP-19 harness), 8 students per arm, same student seeds (400000+s) in both arms. Arms: world (+1 for opening the door holding the key, -0.25 wrong presses) vs teacher (parent grading from `exp24_brains/founder_2.npz`, EXP-22 run B: +1 when the move matches the parent's, -0.25 otherwise). Budgets M = 40, 100, 300, 600 trips. Score = clean full-task pass (EXP-19 test, pass = score >= 0.9). One parent brain, one run.
- Prediction: "teacher wins clearly at small M (dense per-move feedback); the gap closes by M=600. If the arms are equal at every M, teaching is redundant for this skill." (script docstring, written before running)
- Result: students passing, world vs teacher: M=40 1/8 vs 8/8; M=100 3/8 vs 8/8; M=300 5/8 vs 8/8; M=600 7/8 vs 5/8. Counts only, no SEM (pass/fail on 8 students).
- Verdict: SUPPORTIVE. Matches the written prediction; not retracted. The unexplained drop of taught students at M=600 was followed up by EXP-30, which confirmed it (over-teaching).

## Reflection
- What it means: on this task teaching is not redundant: it is a large speed and reliability multiplier at small budgets, and the world catches up by about 600 trips. It does not raise the ceiling (consistent with EXP-26: student at most as good as its teacher). The drop of taught students at 600 (8/8 to 5/8) was the surprise.
- Process: the prediction was written first, and the budget sweep moved the world arm across the whole window (1/8 to 7/8). The teacher arm sat at ceiling (8/8) for three of four budgets, so the size of the teaching advantage there is only a lower bound. Only 8 students and one parent brain, so the 600-trip reversal (7/8 vs 5/8) was within noise on its own. Key-door was already known to be very easy to teach (EXP-24: per-step grading plus a visible key is a lookup), so this is the easy case for teaching. Cadence version was not stamped.
- Lesson: a redundancy check needs matched budgets and the same students, and a budget sweep so at least one arm moves through the window, not a single point.
- Next: followed up by EXP-30 (iter19, teacher arm swept 300 to 1500 trips) to test whether the 600-trip drop was over-drilling or noise.
