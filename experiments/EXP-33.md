# EXP-33: forgetting fix for the peer-network plateau (notes, rehearse, drift-check, bigger brain)

- Date: 2026-10-09 | Cadence version: unrecorded in outputs (iter25 notes the clone was still v0.78.0 / `750c8ef` that day) | Program iter: iter21
- Script: `exp/EXP-33_forgetting_fix.py` | Evidence: `exp/EXP-33.out`, `exp/EXP-33.json`, smoke `exp/smoke/EXP-33-smoke.out`

## Summary
- Question: why do EXP-31 peer networks plateau around 0.78-0.84, and is the cause forgetting / stale teaching or brain capacity?
- Setup: EXP-31 PEER world (random pairs, both directions, specialist rule). N=8 brains, K=32 contexts, M=16 lesson steps,
  16 rounds, 6 seeds. Each brain keeps NOTES (external record of the answer it had when it learned each item). Arms:
  base; rehearse (M/2 self-practice steps on own known set after each lesson, graded against notes); drift (a teacher
  only teaches items whose current answer still matches its notes); both; big (base with modules (32,16), twice the size).
- Prediction: "rehearse+drift lifts the plateau toward 0.95; if only `big` helps, the limit was capacity, not forgetting."
- Result (final knowledge, SEM over 6 seeds; forgetting = share of previously-correct known items wrong after a lesson):
  base 0.790 (0.039), forgetting 0.042; rehearse 0.940 (0.010), 0.017; drift 0.982 (0.005), 0.016;
  both 0.991 (0.002), 0.008; big 0.816 (0.037), 0.036. Base curve peaks at 0.80 and sits at 0.78-0.79 afterwards.
- Verdict: CROSSED (prediction confirmed and exceeded: both reached 0.991, not just 0.95; big alone barely moved).
  Still current; no later iteration retracted it. Its fix (notes + drift-check + rehearse) became the base world for
  EXP-34 FIX, EXP-35, EXP-35b and EXP-36.

## Reflection
- What it means: the plateau was mostly brains teaching items they had already forgotten (stale teaching), not lack of
  capacity. The single biggest fix is drift-check (0.790 to 0.982). The provenance record that pedigree pay needs is the
  same record that stops knowledge rotting.
- Process: clean and well powered for the fixes (rehearse, drift and both sit many SEM above base). The capacity
  comparison is weaker: big vs base (0.816 vs 0.790, SEM about 0.04 each) is within one SEM, so a small capacity
  effect is not ruled out. A 1-round, 1-seed smoke (arms both and big only) ran first.
  Caveats: (1) rehearse and both give the student M/2 extra training steps per lesson, so part of their gain could be
  extra practice rather than the notes; drift adds no steps and is the largest single fix, which limits that confound,
  but it was not controlled. (2) Capacity was tested at one larger size only (2x). (3) Notes are an external record,
  not inside the brain (stated honest floor in iter21). (4) Cadence version not stamped in the outputs.
- Lesson: before blaming capacity for a ceiling, check whether the system is propagating stale state; a record of what
  was learned and its answer at the time is cheap and decisive.
- Next: rerun partner choice on top of the fix (EXP-34 FIX=1), then the pedigree-share controller with a DISCOVER move (EXP-35).
