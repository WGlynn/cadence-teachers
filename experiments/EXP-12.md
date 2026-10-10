# EXP-12: Synergy-harness smoke (copy-b1, copy-b2, XOR from scratch, twin) on a factored-input creature

- Date: 2026-10-08 | Cadence version: 0.78.0 (commit not recorded for this run) | Program iter: iter7
- Script: `exp/EXP-12_smoke_synergy.py` | Evidence: `exp/EXP-12-smoke.out`

## Summary
- Question: does a factored-input creature with a perception bottleneck and a task cue learn the two witness tasks (copy-b1, copy-b2) and the held-out XOR task from scratch, and does the twin fork stay exact?
- Setup: inputs c1, c2 (one-hot bits) and cue (one-hot 3); perception column with P patches reads only c1, c2; policy column (2 patches) reads perception + cue. Reinforcement settings as EXP-11 (discount 0.0, exploration 0.1, reward_scale 4.0, batch 4), settle_budget 64. P in {4, 6, 8}, seed 7 only. Copy tasks 400 steps, XOR 800 steps, greedy accuracy over the 4 contexts.
- Prediction: none written before running. The docstring gives the pass rule: "If all four hold at some perception-patch count P, the full synergy harness is buildable."
- Result (from `EXP-12-smoke.out`, 1 seed each): copy-b1 1.00 and copy-b2 1.00 at P=4, 6, 8. XOR from scratch 0.50 (P=4), 0.75 (P=6), 0.50 (P=8). Twin exact True at all three P (snapshot 24,947 / 25,266 / 25,606 bytes).
- Verdict: NULL on the XOR prerequisite (the pass rule failed: XOR did not learn at any P); SUPPORTIVE on the copy tasks and the twin. The XOR failure was confirmed and widened by EXP-12b to 12f and the supervised EXP-14/14b (iter7 final verdict: the creature does not represent XOR on the architectures tried). The synergy goal this smoke served was later met by different designs: EXP-18 (data-channel synergy, iter12) and EXP-19 (learned sequential composition, iter13). XOR-style synergy is still open.

## Reflection
- What it means: single-bit tasks are easy for this creature; XOR, the irreducible combination task the synergy design needed, was not learned. The 0.75 at P=6 is one context above chance on one seed and is not evidence of partial learning.
- Process: one seed per cell with 4 contexts, so XOR accuracy can only take the values 0, .25, .5, .75 or 1 and one seed cannot separate 0.75 from chance. Accuracy counts a `None` action as wrong; the None-rate was not measured here, so it is not known whether any XOR context returned `None`. The same metric became a real confound in EXP-12c. The smoke did its job: it found the wall before the full 4-condition x F-sweep x seeds harness was built.
- Lesson: check that the held-out task is learnable at all (the ceiling) before designing an attribution probe around it.
- Next: EXP-12b, an architecture x budget x 3-seed search for an XOR ceiling.
