# EXP-75: is V0.5B's late collapse caused by nudged phases that take zero steps?

- Date: 2026-10-25 | Cadence version: 0.88.0, main `b6fdc83` | Program iter: none (mechanism test for EXP-71/74; Cadence group thread 2026-10-25)
- Script: `exp/EXP-75_v05b_tolerance.py` (Bernhard's runner and calm rule; one change: `learning_tolerance=0.0003`) | Evidence: `exp/EXP-75-<seed>.jsonl`, `exp/EXP-75.log`

## Summary
- Question: does the solver tolerance cause the collapse onto one action under the calm rule?
- What EXP-74 showed (exploratory, not predicted): from about lesson 1300 a growing share of taught lessons run a nudged phase of 0 steps. The phase's starting residual (about .0025) is already within `learning_tolerance` (.003). `_equilibrate_local` (brain.py at 0.88.0) loops only while some row's residual exceeds the tolerance, so the nudged state never relaxes toward the label. In 59101 and 59204 the share reached 100%, the wrong count climbed to about 8.5 of 16, and the weight step decayed to 1e-28 and 1e-40: learning stopped while half the rows were wrong. The control 59203 also had 49% zero-step lessons around 1536-1792, but reached 0 wrong by about 2048 and calm then taught nothing. EXP-74's pre-registered hypothesis, an oversized step at the calm switch, was REJECTED (ratios .55 and .43).
- Setup: Bernhard's runner and calm rule exactly (EXP-71, EXP-74), H2, five founders 59101, 59201-59204, 4096 lessons, with `learning_tolerance=0.0003` (10x lower, below the ~.0025 starting residual). Per-lesson log as EXP-74 (rows taught, nudged and free steps and residuals, step sizes, wrong count, level, surprise). Taught and held accuracy plus modal share on EXP-71's panels at 256-4096. The comparison is EXP-71/74 on the same founders.
- Disclosure: written after seeing EXP-71, EXP-72 and EXP-74. A lower tolerance also makes the free phase settle more tightly, so this changes more than the nudged phase. A pass shows the tolerance is a sufficient lever, not that the zero-step phase alone is the mechanism.
- Prediction (written before running):
  - P1 (the lever works): from lesson 1024 on, at most 5% of taught lessons run a zero-step nudged phase, in every founder (EXP-74 at .003: 22% to 100% in collapsed windows).
  - P2 (the consequence): at most 1 of 5 founders collapses (modal share >= .60 with taught < .60 at any checkpoint from 1024 on). EXP-71 at .003: 4 of 5 under that definition.
  - Verdict rule: CONFIRMS if P1 and P2 hold. If P1 holds and P2 fails, zero-step phases are not the cause: REFUTES. If P1 fails, the tolerance is not the lever: INCONCLUSIVE.
- Cost: unknown, since tighter settling needs more solver steps. Five jobs beside EXP-72b and EXP-73.
- Result: PENDING
- Verdict: PENDING

## Reflection
- What it means: PENDING
- Process: PENDING
- Lesson: PENDING
- Next: PENDING
