# EXP-29: two partial teachers (can a student beat each of its teachers?)

- Date: 2026-10-09 | Cadence version: unrecorded | Program iter: iter19
- Script: `exp/EXP-29_two_partial_teachers.py` | Evidence: `exp/EXP-29.out`, `exp/EXP-29.json`

## Summary
- Question: can a student taught by two teachers who each know only half the rule end up better than either teacher, and does it matter whether teachers stay inside what they know?
- Setup: K=32 two-action bandit (EXP-26 harness), fixed rule. Teacher A trained only on contexts 0..15 (seed 811), teacher B only on 16..31 (seed 812); a single teacher pair. Students: 8 per arm per budget, M graded steps from each teacher, interleaved. Arms: spec (each teacher teaches only its own half), over (each teacher teaches any context, including the half it only guesses), soloA (only teacher A, own half, M steps total). M = 32, 64, 128 per teacher. Score = student greedy accuracy on the true rule.
- Prediction: "(a) student ~1.0 > each teacher (~0.75); (b) no better than a teacher (contradictions on the unknown halves); (c) ~0.75. If (a) >> (b), knowing the limits of your own knowledge is a teaching skill." (script docstring, written before running)
- Result: teachers: A own-half 1.00, full 0.91; B own-half 1.00, full 0.72 (A guessed its unknown half well by luck). Student accuracy, mean (SEM), 8 students: M=32 spec 0.844 (0.046), over 0.664 (0.022), soloA 0.625 (0.050); M=64 spec 0.891 (0.051), over 0.645 (0.008), soloA 0.660 (0.046); M=128 spec 0.898 (0.026), over 0.680 (0.015), soloA 0.629 (0.040).
- Verdict: SUPPORTIVE. (b) confirmed: overconfident teachers cancel out and the student lands near one teacher alone. (a) only partly: the specialist student beats B (0.72) and the teacher average (0.81) but only ties A (0.91) and never approaches 1.0. (c) came in lower than predicted (0.63 to 0.66, not 0.75). Not retracted; the specialist rule was carried into EXP-31 and EXP-32.

## Reflection
- What it means: knowing the limits of your own knowledge is a teaching skill worth about 0.2 accuracy here (spec about 0.84 to 0.90 vs over about 0.65 to 0.68). Whether two partial teachers can produce a student who exceeds the best teacher is still not shown, because teacher A turned out much better than designed.
- Process: the "~0.75 per teacher" assumption was not checked before the student runs; A came out at 0.91, which removed most of the room for the student to beat both teachers. The spec student flattens near 0.89 to 0.90 from M=64 to M=128, so something other than budget caps it (not investigated). Budgets are not matched across arms: soloA gets M steps while spec and over get 2M. Only one teacher pair, so teacher quality is a single draw. The docstring WINDOW line sweeps M, but no pilot is recorded. Cadence version not stamped.
- Lesson: when a prediction depends on a teacher being at a given level, measure the teacher first and re-draw it if it lands outside the design; match total budgets across arms.
- Next: the specialist rule (teach only what you know) became the teaching rule in the peer network experiments (EXP-31, EXP-32).
