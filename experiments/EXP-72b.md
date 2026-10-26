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
- Result (Windows, numpy 2.4.2, OMP_NUM_THREADS=1; finished 22:46 CT). Held, H2 (EXP-72) vs H1 (this run), same founders 59101 / 59201 / 59202 / 59203 / 59204:
  - 1024: H2 .64 / .84 / .90 / .86 / .85 (mean .817) vs H1 .38 / .81 / .93 / .59 / .80 (mean .702). H1 taught .41 / 1.00 / 1.00 / .72 / 1.00 (two founders not yet fitted). Difference +.115 (SEM .062), H2 ahead in 4 of 5.
  - 2048: H2 mean .859 vs H1 .866 (H1 taught 1.00 in all five). Difference -.006 (SEM .028).
  - 4096: H2 .72 / .82 / .96 / .83 / .93 (mean .853) vs H1 .79 / .81 / .95 / .78 / .88 (mean .842). Difference +.011 (SEM .022), H2 ahead in 4 of 5.
  - H1 at 4096: taught 1.00 and modal share .39 in all five. Erasing role0 gives .29 to .34, role1 .33 to .41, all records .31. So a single held head's answer uses both relevant facts.
- Verdict: NO HEAD GAIN (pre-registered rule: mean difference at 4096 below .02). P1 holds (H1 taught >= .95 at 4096 in 5 of 5). For the record, H2 is ahead in 4 of 5 founders at 4096, by a small amount.

## Reflection
- What it means: on V0.5B with stable teaching, two held heads learn the taught pairs faster (+.115 held at 1024, when two one-head brains had not yet fitted), but once both arms fit, one head generalizes to the held pairs as well as two (.842 vs .853 at 4096). One head's answer depends on both relevant records (either erasure drops to chance), so a single held read already combines two facts here. Two caveats: the task needs only two facts and has two distractors; and the calm-rule comparisons (Bernhard's pilot H2 .73 vs H1 .58 at 1024; EXP-71) measure speed and stability as much as reach.
- Process: pre-registered and pushed before data (4373de1), after seeing EXP-71 and EXP-72 (disclosed). Same founders and stream as EXP-72; one flag changed. Five founders: the 4096 difference has SEM .022, so a gain of a few points is not excluded.
- Lesson: compare architectures at matched fit, not at matched lesson count; an early lead can be speed rather than reach.
- Next: report to the group with EXP-72; a harder V0.5B (three relevant facts, or more distractors) is where a second head could matter, and is the natural next arm for Huncho's or Bernhard's runner.
