# EXP-74: does switching on learning_surprise mid-training give normalized teaching an oversized step?

- Date: 2026-10-25 | Cadence version: 0.88.0, main `b6fdc83` | Program iter: none (mechanism probe for EXP-71's late collapse; Cadence group thread 2026-10-25)
- Script: `exp/EXP-74_calm_switch_step_spike.py` | Evidence: `exp/EXP-74-<seed>.jsonl` (one row per lesson), `exp/EXP-74.log`

## Summary
- Question: is the late collapse in EXP-71 caused by an oversized weight step when the calm rule switches `learning_surprise` on? In EXP-71, founder 59101 converged under Bernhard's calm rule: taught .99 and held .83 at 2048, with calm on from lesson 1864. By 4096 it had collapsed: taught .39, with 169 of 192 answers on one action. Founder 59204 entered calm at 1682 and also regressed.
- What the code does (`learning.py` at 0.88.0, `_update`): with `teaching="normalized"`, each lesson's contrast is averaged over the taught rows. It is then divided, per synapse, by a running RMS of past contrasts (forgetting factor .99).
- The hypothesis (not yet measured): under every-row teaching, a mostly-right batch averages a few large wrong-row contrasts with many smaller right-row ones, so the running RMS settles small. With surprise on, only wrong rows are taught, so the averaged contrast is undiluted. Divided by the small RMS, it makes a large step until the RMS catches up. The probe measures whether right rows really contribute small contrasts; if they do not, the hypothesis fails here.
- Setup: replay of EXP-71's H2 training for 59101, 59204 and 59203 (the control, converged and held), 4096 lessons, Bernhard's runner and calm rule unchanged. Each lesson logs rows taught, wrong count on its 16 patterns, the running level, the surprise flag, and the learner's `scale_step` (mean absolute weight step) and `bias_step`. Taught and held accuracy on EXP-71's panels at 2048 and 4096 check the replay.
- Prediction (written before running):
  - Replay check: taught and held at 2048 and 4096 equal EXP-71's for each founder.
  - SPIKE (mechanism supported) needs two things, in both 59101 and 59204. First, the step jumps: in the 50 lessons after calm first engages, the mean `scale_step` is at least twice the mean over the 50 lessons before. Only lessons that taught at least one row count, because a surprise lesson with no wrong row runs no update. Second, the brain gets worse soon after: the running level rises back above .02 within 200 lessons of the switch.
  - REJECTED if that ratio is below 1.25 for both.
  - Otherwise INCONCLUSIVE. The control 59203 is reported. If it spikes too without collapsing, the spike is not sufficient, and the write-up says so.
- Result: PENDING
- Verdict: PENDING

## Reflection
- What it means: PENDING
- Process: PENDING
- Lesson: PENDING
- Next: PENDING
