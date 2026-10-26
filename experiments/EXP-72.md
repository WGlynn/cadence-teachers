# EXP-72: does teaching only wrong rows from the first lesson stop V0.5B's late collapse onto one action?

- Date: 2026-10-25 | Cadence version: 0.88.0, main `b6fdc83` | Program iter: none (off the V(S) ladder; tests one candidate cause of Bernhard's "output collapses to one action in the harder examples", Cadence group 2026-10-25)
- Script: `exp/EXP-72_v05b_surprise_from_start.py` (EXP-71's script with one change, see below) | Evidence: `exp/EXP-72-<seed>-H2.jsonl`, `exp/EXP-72.log`

## Summary
- Question: in EXP-71, under Bernhard's calm-teaching rule, three of five founders learned and then regressed between 1024 and 2048 lessons. Founder 59201 fell from .70 to .36 taught, with 187 of 192 taught answers on one action. The rule switches to `learning_surprise` (teach only the rows the brain got wrong) while the running wrong rate is below .02, and back to every row above it. The two founders that converged entered it (59203 at lesson 1260, 59101 at 1864) and ended with level .0014 and .0016. Two of the three that regressed (59201, 59202) never entered it by 2048, so every lesson taught every row, including rows they already answered right. The third (59204) entered it at 1682 and still regressed (level .28 at 2048), so the every-row account does not cover all three. Does `learning_surprise=True` from lesson 0 prevent the collapse? This tests one candidate cause on V0.5B; we do not know which examples Bernhard means.
- Why we expect it might: EXP-55 (on 0.83) found that every-row lessons made a right-answer teacher worse than a random one through readout saturation, and #197's `learning_surprise` removed the harm (+.19). Upstream's own reading of "collapse onto one action" is a motor-readout saturation latch.
- Setup: identical to EXP-71: same five founders (59101, 59201-59204), H2 only (`recall_heads=2`), same lesson stream (`default_rng(1000 + seed)`), same evaluation panels, same checkpoints (256 to 4096) and readings. The one change: the brain is retuned to `learning_surprise=True` before lesson 0, and the calm switch is never applied (the running wrong level is still logged). The comparison arm is EXP-71's H2 run on the same founder.
- Disclosure: written after seeing EXP-71's H2 checkpoints up to 2048 (not 4096, and not its H1 arm).
- Prediction (written before running):
  - P1: no founder's taught accuracy falls by more than .10 between consecutive checkpoints from 1024 on (EXP-71 calm: three of five did between 1024 and 2048).
  - P2: the modal action share on the taught panel is at most .50 for every founder at 2048 and at 4096 (EXP-71 calm at 2048: 59201 .97, 59202 .75, 59204 .66).
  - P3 (reported, direction only): mean held accuracy at 2048 and at 4096 at least EXP-71 calm's on the same founders.
  - Risk: teaching only wrong rows from the start may slow early learning, so 256 to 512 may sit below EXP-71.
  - Verdict rule: PREVENTS if P1 and P2 hold. DOES NOT PREVENT if two or more founders collapse (modal share >= .60 with taught < .60 at any checkpoint from 1024 on). Otherwise PARTIAL, with the per-founder table.
- Result: PENDING
- Verdict: PENDING

## Reflection
- What it means: PENDING
- Process: PENDING
- Lesson: PENDING
- Next: PENDING
