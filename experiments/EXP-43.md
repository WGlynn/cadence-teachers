# EXP-43: grades that judge the guess: can a Cadence brain learn text from a teacher's grades alone?

- Date: 2026-10-10 | Cadence version: 0.80.0 (`19bee92`) | Program iter: iter33 (pending)
- Script: `exp/EXP-43_judged_grades.py` | Evidence: `exp/EXP-43-full.json/.jsonl`, `exp/EXP-43-full.out` (PENDING) | Text: Alice ch.1 (train), ch.2 (held out), as EXP-42

## Summary
- Question: EXP-42's levers 1 + 2 together. Does more experience (10 passes, not 3), or a richer grade, let a Cadence brain that never hears the answer reach a model that is told every character? The richer grade: EXP-42's right/wrong grade is noisy (even the best next character is wrong most of the time, so the best guess and a bad guess both mostly hear -1). A teacher who knows the language can grade the guess itself instead of its luck.
- Setup: the teacher reads the book alongside the student; after grading each guess it is told the character (online counts, backing off to shorter contexts it has not seen) and scores a guess by how often that character has followed this context: its best = +1, never seen here = -1, linear between. The score depends only on the text before the guess. Grades on the student's own guess: outcome (+1 right / -1 wrong, EXP-42), judged (the teacher's score), partial (the mean of the two). Cadence arms (modules (32, 16), arousal on, one-step episodes, EXP-42's seeds): outcome-w1, partial-w1, judged-w1 (last character in, bigram teacher), judged-w3 (last 3 characters in, 4-gram teacher). 10 passes over ch.1; greedy held-out accuracy from a saved copy after passes 1, 3, 10; then ch.2 with learning on (prequential). 3 seeds. Baselines: majority; the teachers' own accuracy (teacher-2 = told-the-answer bigram, teacher-4); a tabular epsilon-greedy learner on the same grades (optimistic start). Chain printed per pass for every arm: grade -> mean reward -> agree (the student's guess = the teacher's best) -> accuracy.
- Honest floor, before any number: the teacher was told the characters, so the knowledge comes from supervision; what this measures is how much of a teacher's knowledge passes to a student through grades alone, the quantity the teaching game prices. With one character of context the student's ceiling is its teacher, by construction.
- Prediction (written before the pilot and the full run; a 600-character smoke run of the code was seen first, too short to read):
  - (P1) More passes alone do not get there: outcome-w1 after 10 passes stays more than .03 below teacher-2 on held-out text.
  - (P2) A judged grade does, for one character: judged-w1 comes within .02 of teacher-2.
  - (P3) Partial credit helps: partial-w1 beats outcome-w1 by more than 2 SEM.
  - (P4) The breakaway shot: judged-w3 beats teacher-2, so a brain never told a character predicts held-out text better than a model told every character but seeing only one.
  - (P5) judged-w3 stays more than .05 below its own teacher (teacher-4).
  - (P6) With 3 characters of context the tabular learner beats Cadence on the same judged grades (a table stores the teacher's best for every context it has seen; a (32, 16) brain cannot hold about 2,000 contexts).
  - Check, not a prediction: outcome-w1 passes 1-3 reproduce EXP-42's w1 numbers exactly (same seeds, same grades).
- Breakaway = P4 holds. Result: PENDING. Verdict: PENDING.

## Reflection
- PENDING (after the run).
