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
- Result (Windows 10, CPython 3.12.10, numpy 2.4.2, OMP_NUM_THREADS=1; all 10 jobs finished 22:25 CT). Taught / held / modal share on the taught panel, H2 then H1:
  - 59101: H2 1024 .64/.51/.56, 2048 .99/.83/.39, 4096 .39/.35/.88 (calm from 1864). H1 4096 1.00/.92/.39 (calm from 2342).
  - 59201: H2 2048 and 4096 .36/.38/.97 (never calm). H1 4096 .65/.61/.64.
  - 59202: H2 1024 .94/.86/.38, 2048 .58/.51/.75, 4096 .68/.51/.65 (never calm). H1 4096 .39/.31/1.00.
  - 59203: H2 2048 and 4096 1.00/.96/.39 (calm from 1260). H1 4096 1.00/.92/.39.
  - 59204: H2 1024 .89/.76/.42, 4096 .50/.43/.89 (calm from 1682). H1 4096 .52/.36/.88.
  - Means over all five: H2 held .672 at 1024 and .526 at 4096; H1 held .451 at 1024 and .626 at 4096.
- G0: FAILED. Founder 59101 at 1024 reads taught .64 / held .51 against Bernhard's pilot .66 / .65 (controls also differ). Most likely a different floating-point path (his machine vs Windows with numpy 2.4.2; not isolated). The fresh-founder readings below are within one machine.
- Predictions: P1 HOLDS (H2 held/taught >= .85 at 1024 in 4 of 4 fresh founders). P2 FAILS (H2 held at 4096 > at 1024 in 1 of 4). P3 HOLDS (H2 > H1 held at 1024 in 4 of 4). Generalization-limited rule: 0 of 4. P4 (collapse, reported): yes. A modal share of .60 or more on the near-balanced taught panel appears at 1024 or later in 17 founder-arm checkpoints, in both arms. 59202's H1 ends with every answer on one action.
- Verdict: MIXED (P1 and P3 hold, P2 fails, not generalization-limited).

## Reflection
- What it means: held follows taught closely wherever taught is high (ratio .85 or more at 1024; 59203 1.00/.96 at 4096). So on V0.5B the conjunction generalizes once the taught pairs are fitted; generalization is not the ceiling. P2 failed for a different reason: under the calm rule the fit itself does not stay, and taught collapses toward one action after being learned, in both arms. EXP-72 shows that teaching only wrong rows from lesson 0 removes it for H2. The heads comparison depends on training length under this rule: H2 > H1 at 1024 in 4 of 4, but H1 ahead on average at 4096 because H2 collapsed more. So "two heads beat one" needs a comparison under stable teaching (EXP-72b).
- Process: pre-registered and pushed before data (2b10a49). G0 failed, most likely from platform differences (not isolated), and was declared non-voiding in advance. Readings were taken on deepcopies, and EXP-74's copy-free replay reproduced the 2048 numbers exactly for three founders, so the readings did not perturb training. The verdict rule's P2 assumed training is stable, and it was not, so P2 measured stability, not generalization. Ran beside other jobs (up to 13 processes on 6 cores); this affects time only.
- Lesson: before reading "does more training help generalization", check the fit stays fitted; a collapse reads as a generalization failure if only held is watched. Read the choice histogram, not just accuracy.
- Next: EXP-72 (surprise from lesson 0, H2): PREVENTS. EXP-72b (same for H1) for the heads question. EXP-74 for the mechanism of the calm-rule collapse.
