# EXP-71: Attention V0.5B, fit-limited or generalization-limited, and do misses pile onto one action?

- Date: 2026-10-25 | Cadence version: 0.88.0, main `b6fdc83` | Program iter: none (off the V(S) ladder; answers the Cadence group thread of 2026-10-25)
- Script: `exp/EXP-71_v05b_fit_vs_generalize.py` (imports Bernhard's runner unchanged, vendored at `exp/v05b/`, cadence-stone-age PR #1 commit `5f038a3`) | Evidence: `exp/EXP-71-<seed>-H<k>.jsonl`, `exp/EXP-71.log`

## Summary
- Question: V0.5B is Bernhard's identifiable split of the conjunctive task: the answer is (role0 + role1) % 3, with 9 values per role. First, is held accuracy capped by how well the brain fits the taught pairs, or by generalizing from them? Second, when the brain misses, does its output collapse onto one action? That second part is Bernhard's open problem: "output collapses to one action in the harder examples".
- Why: in his 4-founder pilot at 1024 lessons, H2 held nearly tracks H2 taught (.65/.66, .68/.75, .72/.84, .86/.92). If held follows taught, the conjunction already generalizes and the ceiling is fitting; that changes what V0.5B's frozen run should report and where the next lever is.
- Setup: his `run_v05b.py` functions unchanged (compose, warm, Recall-written banks, calm teaching, 16 taught patterns per lesson, his evaluation panels of 192 taught + 192 held from `default_rng(99)`). His `train()` is unrolled only to pause at checkpoints 256, 512, 1024, 2048, 4096 lessons; every reading is taken on a deepcopy, so the training path should be his (G0 checks this at 1024). At each checkpoint we read taught and held accuracy. We also count how often each action is chosen, and the largest share is the modal share. We read accuracy per true action and the heads' top roles. At 1024 and 4096 we add his causal controls: erase role0, erase role1, erase the distractors, erase every record, and clone one head's address. Arms H2 (`recall_heads=2`) and H1 (`recall_heads=1`). Founders: **59101** (reproduction gate, his pilot founder) and fresh founders **59201, 59202, 59203, 59204**, declared here before any run. Windows 10, CPython, `OMP_NUM_THREADS=1`.
- Prediction (written before running):
  - G0 (reproduction, not a verdict gate): founder 59101 at 1024 reproduces his JSON accuracies exactly. Mac vs Windows floating point may break bit-exactness; any difference is recorded as platform drift and does not void the fresh-founder readings.
  - P1: on the fresh founders at 1024, H2 held / taught >= .85 in at least 3 of 4.
  - P2: H2 held at 4096 > H2 held at 1024 in at least 3 of 4 fresh founders.
  - P3: H2 > H1 on held at 1024 in at least 3 of 4 fresh founders (replicates the pilot's direction).
  - P4 (collapse, no direction claimed): reported, not predicted. Collapse is defined as a modal share of predicted actions >= .60 on a panel whose labels are near-balanced (each action about a third).
  - Verdict rule: FIT-LIMITED if P1 and P2 hold. GENERALIZATION-LIMITED if H2 taught >= .95 at 4096 while H2 held <= taught - .15, in at least 3 of 4 fresh founders. Otherwise MIXED, with the per-founder table.
- Result: PENDING
- Verdict: PENDING

## Reflection
- What it means: PENDING
- Process: PENDING
- Lesson: PENDING
- Next: PENDING
