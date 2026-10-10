# EXP-21: full lesson payoff table measured on real Cadence key-door students

- Date: 2026-10-09 | Cadence version: 0.78.0 / `750c8ef` (iter14 header; not stamped in the output) | Program iter: iter14
- Script: `exp/EXP-21_lesson_payoff_table.py` | Evidence: `exp/EXP-21-s{0,2,4,6,8,10}.json` and `.out` (2 students each, 12 total)

## Summary
- Question: what does every coalition of lessons (null, each single lesson, every unordered pair including same-lesson pairs, over {key, door, lamp, spam}) actually do to a real Cadence key-door student?
- Setup: 15 coalitions (null; 4 singles + null; 10 pairs) x 12 student seeds (50000 to 50011). Each cell is a fresh founder at the protocol-3 operating point, N=300 trips per slot, interleaved, scored on clean full-task trips (fed with zero wrong presses, EXP-19 test_fed). About 870 to 1180 s per student (first student in each file 945 to 1045 s, second 866 to 1179 s), 6 files run in parallel, 2 students each. The table feeds EXP-20b.
- Prediction: none written before running.
- Result (raw scores from the .out files; means and SEM computed from the json, v = score minus that student's null score):
  - v(key+door) = +0.819 (SEM 0.111, n=12). 10/12 students score 1.00; students 9 and 11 score 0.00.
  - v(key + null) = +0.147 (SEM 0.111): students 3 (0.93) and 6 (1.00) solved the task from key lessons plus null trips; key+key solved it for 0/12.
  - Every other coalition (door alone, lamp, spam, key+key, key+lamp, key+spam, door+door, and the rest) = -0.014 (SEM 0.014): all raw scores are 0.00; the -0.014 comes only from student 5's null score of 0.17.
- Verdict: SUPPORTIVE as a measured table (iter14: "Only key+door pays: v(AB) +0.82 (10/12 students clean)"). Not retracted. It is a measurement, not a hypothesis test.

## Reflection
- What it means: on this world the lesson game is a pure complement: key and door are near-worthless alone and worth about 0.82 together, and a bad partner lesson (lamp, spam, or a second key) wipes out a good one. That structure is why every credit rule in EXP-20b converges the same way.
- Process: (1) iter14 calls the 14 other coalitions "~0"; key + null is +0.147 because 2/12 students solved the task from it while key + key (twice the key practice) solved it for none. The log flags it as unexplained; it was never followed up. (2) Only 12 students, and 2/12 never learn the chain under any coalition (consistent with EXP-19 founders that never learn), so student-side failure is baked into the table. (3) Scores are nearly binary per student (1.00 or 0.00), so the table carries little graded signal. (4) About 3.3 hours of process time (11746 s summed over the 6 files; about 36 minutes wall clock in parallel) for one small table, with no pilot or written prediction (this predates the iter17 RUN GATE).
- Lesson: measure the payoff table before designing a credit-rule contest on it; this one shows in advance that the rules cannot disagree (no free-rider lesson exists).
- Next: EXP-20b played on this table; iter14 queued a free-rider game (one lesson that teaches the whole task) to separate Shapley from equal split.
