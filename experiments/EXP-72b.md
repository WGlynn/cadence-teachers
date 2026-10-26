# EXP-72b: under stable teaching, do two held heads beat one on V0.5B?

- Date: 2026-10-25 | Cadence version: 0.88.0, main `b6fdc83` | Program iter: none (Cadence group thread; Bernhard's 0.88 release note "it should now learn to attend to multiple learned facts", Huncho's V0.5B frozen run)
- Script: `exp/EXP-72b_v05b_h1_surprise.py` (EXP-72's script unchanged, `--heads 1`) | Evidence: `exp/EXP-72b-<seed>-H1.jsonl`, `exp/EXP-72b.log`

## Summary
- Question: when teaching is stable (learning_surprise from lesson 0, EXP-72), does `recall_heads=2` beat `recall_heads=1` on V0.5B's held pairs?
- Why: under the calm rule (EXP-71), H2 beat H1 on held at 1024 lessons in 4 of 4 fresh founders, but by 4096 H1 was ahead on average (.63 vs .53 over all five), because both arms collapsed and H2 collapsed more. Bernhard's pilot (H2 .73 vs H1 .58 at 1024) and Huncho's frozen run compare heads under that same rule. EXP-72 ran H2 only.
- Setup: EXP-72 exactly (same five founders 59101, 59201-59204, lesson stream, panels, checkpoints 256-4096, readings), `recall_heads=1`. The comparison arm is EXP-72's H2 run on the same founder. Disclosure: written after seeing EXP-71 complete and EXP-72's H2 arm.
- Prediction (written before running): our prior favours two heads (Bernhard's held-heads benchmark: two heads answer 96-98% of untaught one-action pairs vs 59-76% for one; EXP-71 at 1024: H2 > H1 in 4 of 4), but V0.5B's single-head brains reached held .92 in two founders under the calm rule at 4096.
  - P1: H1 taught >= .95 at 4096 in at least 4 of 5 founders (stable teaching works for one head too).
  - HEADS HELP if EXP-72 H2 held at 4096 > EXP-72b H1 held at 4096 in at least 4 of 5 founders (paired) and the mean difference is at least .05.
  - NO HEAD GAIN if the mean difference is below .02, or H1 >= H2 in at least 3 of 5 founders.
  - Otherwise MIXED, with the per-founder table. Also reported at 1024 and 2048.
- Result: PENDING
- Verdict: PENDING

## Reflection
- What it means: PENDING
- Process: PENDING
- Lesson: PENDING
- Next: PENDING
