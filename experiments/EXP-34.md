# EXP-34: informed partner choice (can brains learn whom to teach?)

- Date: 2026-10-09 | Cadence version: unrecorded in outputs (iter25 notes the clone was still v0.78.0 / `750c8ef` that day) | Program iter: iter21 (base world), iter22 (FIX=1 rerun)
- Script: `exp/EXP-34_informed_partner_choice.py` (env `FIX=1` adds the EXP-33 notes + drift-check + rehearse) | Evidence: `exp/EXP-34.out`, `exp/EXP-34.json`, `exp/EXP-34-fix.out`, `exp/EXP-34-fix.json`

## Summary
- Question: when each brain can see how much of its known set each peer lacks, does a learned chooser pick needy
  students and does neediest-first teaching beat random partner choice?
- Setup: EXP-32 market (pay = student's measured gain on the true rule, budget-balanced). N=8, K=32, M=16, 16 rounds.
  Arms: RANDOM peer; ORACLE (peer lacking the most of the teacher's known set); INFORMED (Cadence chooser whose input is
  each peer's lacking share, learning from its pay). Run 1: original world, 6 seeds. Run 2 (FIX=1): EXP-33 fix world, 8 seeds.
- Prediction: "ORACLE clearly beats RANDOM; INFORMED closes most of the gap." For the FIX rerun, only the iter21 note
  was written beforehand: "re-run partner choice ON TOP of the fix (ceiling gone, choice may now matter)".
- Result:
  Run 1 (6 seeds): final RANDOM 0.841 (SEM 0.041), picked-the-neediest 0.53; ORACLE 0.824 (0.041), 1.00;
  INFORMED 0.809 (0.019), 0.42. ORACLE led early (round 2: 0.75 vs 0.70; round 4: 0.83 vs 0.79), then all sat near 0.82.
  Run 2 FIX (8 seeds): final RANDOM 0.981 (0.003), 0.27; ORACLE 0.991 (0.003), 1.00; INFORMED 0.982 (0.003), 0.25.
  ORACLE reached 0.96 by round 8 vs RANDOM round 12 (logged as ~25% faster, consistent across seeds).
- Verdict: Run 1 NULL on final knowledge (ceiling-bound), SUPERSEDED by the FIX rerun. FIX rerun: SUPPORTIVE for
  neediest-first (faster, small final edge 0.991 vs 0.981); NULL for the learned chooser (it equals random). Prediction
  half met: ORACLE beats RANDOM on speed only; INFORMED did not close the gap at all.

## Reflection
- What it means: partner choice was not the bottleneck while the network was capped by stale teaching; once that cap
  was removed, choosing the neediest student mainly speeds up the start. A chooser learning from per-round pay did not
  learn to follow a visible need signal: pay per round is too noisy to learn from at this scale.
- Process: Run 1 was run in a world already known to plateau (EXP-31; EXP-33 ran at the same time and finished
  after it, by file times), so the effect window was at a ceiling and the
  final-knowledge comparison could not show a difference; no window pilot. Seed count changed 6 to 8 between runs. The
  "~25% faster" figure is read off mean curves; no per-seed time-to-threshold statistic is in the outputs. The FIX rerun
  had no formal prediction written before running. Version not stamped.
- Lesson: fix the binding constraint first, then measure the secondary knob; and do not ask a learner to discover a
  rule from a reward signal noisier than the effect it must learn.
- Next: design rule adopted (Will, iter22): teaching is neediest-first, hard-wired, not learned. The routing-by-self-
  reported-need attack surface was named and queued as EXP-36.
