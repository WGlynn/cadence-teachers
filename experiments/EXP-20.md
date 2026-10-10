# EXP-20: teacher brains that learn from their own live Shapley credit (closed loop on real students)

- Date: 2026-10-09 (script and only output timestamped 2026-10-09 00:14 / 00:17) | Cadence version: not recorded in the output; program log iter13/iter14 headers give 0.78.0 / `750c8ef` for this period | Program iter: none of its own (named only as a script in iter14 Evidence)
- Script: `exp/EXP-20_learning_teachers.py` | Evidence: `exp/EXP-20-run99.json` (a 2-round smoke run, RUN=99, N=100). No full-run output exists.

## Summary
- Question: if each of two teachers is itself a Cadence brain choosing which lesson to give, and its only reward is the Shapley credit its lesson earns in a freshly taught student, do the teachers learn to give the complementary lessons?
- Setup: two teacher brains (Brain.compose, 1 constant input, 5 actions, 16-unit module). Menu: null, key, door, lamp (wrong object), spam (rewards any interaction). Each round a fresh key-door student is taught by each coalition {}, {T1}, {T2}, {T1,T2} (N=100 trips per slot, interleaved, missing slot = null trips), tested on clean full-task trips (EXP-19 test_fed), and each teacher is paid 2 x its 2-player Shapley value. Default ROUNDS=40. Every round needs 4 freshly trained and tested students.
- Prediction (docstring, written before running): "Prediction if the loop works: teachers converge on complementary {key, door} and never on spam. Honest risk: coordination game with 2 pure equilibria + noisy credit; may not converge in R rounds."
- Result: only a smoke run exists (run 99, 2 rounds): round 0 lamp/lamp, round 1 spam/key, v12 = 0.00 and both phi = 0.00 in both rounds; greedy end policy key / lamp. That is a plumbing check and says nothing about the question.
- Verdict: VOID as an experiment (never run at size). SUPERSEDED by EXP-21 (measure the full lesson payoff table once on 12 real students) plus EXP-20b (teacher brains play many cheap rounds against that measured table).

## Reflection
- What it means: nothing is known from EXP-20 itself. The closed live loop (payoffs re-measured on a new student every round) has still never been run; EXP-20b answers a cheaper lookup version of the question.
- Process: the design was too expensive per round to run as written. For scale, EXP-21 took about 870 to 1180 s per student to train and test 15 coalitions at N=300 (`exp/EXP-21-s*.out`: first students 945 to 1045 s, second students 866 to 1179 s), and EXP-20 needs 4 students per round for 40 rounds. Swapping to a measured table was right on cost, but it removed the "live" part, which iter14 admits ("Payoffs are looked up from 12 measured students, not re-measured live each round"). The smoke-run file is not labeled as a smoke run anywhere except by its round count. The script's `teach` and `student_score` helpers became shared infrastructure (EXP-21 and EXP-22 import this file), so later results depend on this code.
- Lesson: when every round of a learning loop needs a freshly trained student, measure the payoff table once and let the learners play the table, but report it as a table game, not as the live loop.
- Next: EXP-21 (measured table) and EXP-20b (learning teachers on the table), logged together as iter14.
