# EXP-23: rung 3, selecting parents by teaching vs by doing

- Date: 2026-10-09 | Cadence version: 0.78.0 / `750c8ef` (iter16 header; not stamped in the output) | Program iter: iter16
- Script: `exp/EXP-23_selection_by_teaching.py` | Evidence: `exp/EXP-23.out`, `exp/EXP-23.json`, `exp/exp23_brains/` (192 saved brains)

## Summary
- Question: is teaching ability heritable, and does selecting on it beat selecting on doing?
- Setup: 12 founder candidates (half lesson-trained, half end-to-end), 9/12 passed; the first P=6 passing became the population. Each generation every member raises K=3 children by parent-grading (EXP-22 run B, M=200 trips). A parent's teaching score = fraction of its children that pass. Next population = 6 of the 18 children. DO arm: child's own pass, ties random. TEACH arm: child's own pass, ties broken by the parent's teaching score. 5 generations, same founders and same child seeds per slot in both arms.
- Prediction: none written before running.
- Result: identical in both arms. Pop pass 1.00 every generation; pop teaching 0.94, 0.94, 0.94, 1.00, 0.94 in both (0.94 = 17 of 18 children passing). Parent to child teaching correlation -0.08 in DO (n=24 pairs), undefined in TEACH (no variance). Per iter16, re-testing all saved children showed the 4 failing children sit in the same seed slots in both arms, under different parents.
- Verdict: NULL. It also triggered the RETRACTION of EXP-22's "doing != teaching" sub-claim. Superseded as the teaching-trait test by iter17 pilots (EXP-24 to EXP-26) and the EXP-27 evolution runs on a tutor FOCUS trait.

## Reflection
- What it means: in this setup, selecting by teaching is the same as selecting by doing, because among passing parents teaching ability has no variance: grading copies the parent's whole policy, and child failure is set by the child's random init. Teaching ability has to be a real, varying, heritable trait before selecting on it can matter.
- Process: (1) the design had no variance in the thing being selected: every parent passed, nearly every parent's teaching score was 1.00, and the TEACH arm's tie-break almost never had anything to break. A cheap pilot, or EXP-22's own numbers (94% per-generation fidelity, 82/88 children copying the parent's full policy), pointed to this before the run. (2) Child seeds depend only on the slot (generation, parent index, child index), not on the parent; this is what made the student-side cause visible, and it is also why both arms are near-copies. (3) Small: P=6, K=3, 5 generations, about 17 minutes. (4) No written prediction. This experiment is the named example in the RUN GATE ("VARIANCE: the thing being selected or compared actually varies (no EXP-23 repeat)") and part of why iter17 made a pilot plus written prediction mandatory.
- Lesson: before a selection experiment, confirm the trait being selected actually varies across individuals and is not dominated by noise on the other side (student seed); otherwise the arms cannot differ.
- Next: iter16 named two routes: teachers that differ in STRATEGY (what to show / how to grade), or a harder skill where off-path guidance matters. iter17 piloted these (EXP-24 grading strategies: key-door too easy; EXP-25 memory door: not learned; EXP-26 tutor FOCUS: a graded trait, child acc .625 to .688), leading to EXP-27.
