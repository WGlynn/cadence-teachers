# EXP-52: Noesis-lite v1.1, priced against a null contribution of the same form

- Date: 2026-10-13 | Cadence version: 0.83.0 (`23dba71`) | Program iter: none (teaching track; follow-up to EXP-49's BOUNDARY)
- Script: `exp/EXP-52_noesis_lite_null_counterfactual.py` | Evidence: `exp/EXP-52-pilot.*`, `exp/EXP-52-full.json/.jsonl/.out` (PENDING)

## Summary
- Question: EXP-49's market, priced against an untaught twin, paid a random-label teacher +.18 (random labels knock a stuck student loose) and did not rank skill. Priced instead against a twin taught by a random-label teacher (a null contribution of the same form), do fakes price at zero and does pay follow how much a teacher knows?
- Setup: as EXP-49 (weather chamber; 40-attempt lessons under seen weather; 20 attempts alone through `live`; per-state greedy accuracy under unseen weather; each lesson replicated on an independent student; finalize if both worths exceed .125). Three twins per student from the same seed and world draws: taught by the teacher, taught by the random-label null, untaught (EXP-49's counterfactual, reproduced in the same runs). Teachers: know-k for k = 1..4 (labels the right action at the k stages it knows, a random subset per lesson, and a random action elsewhere; skill = k/4), and the fakes random, wrong-chain, echo. 3 seed blocks x 12 students x 7 teachers = 72 worth samples per teacher per counterfactual.
- RUN GATE: (1) prediction below, written before the pilot. (2) Window: a pilot of one seed block with 3 students per teacher at exact run conditions; EXP-49 sets the expected noise (single-student worth swings near a full point). (3) Variance: the three twins share the student seed and world draws; replication uses an independent student. (4) Metric: mean worth and pay share per teacher under each counterfactual; Spearman of worth against k over know-k lessons. (5) Chain: teacher -> label stream -> taught / null / untaught accuracy -> worth -> finalized pay.
- Prediction (written before the pilot):
  - Check, not a prediction: against the null, the random teacher's mean worth is within 2 SEM of zero (it is the null, with different draws).
  - (P1) Against the null, every fake's mean worth is <= 0 (random about 0, wrong-chain and echo below), and the fakes' combined pay share is <= .10.
  - (P2) Against the null, genuine (know-k) teachers take >= .85 of pay.
  - (P3) Against the null, worth rises with knowledge: mean worth is ordered know-1 < know-2 < know-3 < know-4, and Spearman(worth, k) over know-k lessons is >= .3.
  - (P4) Against the null, know-4 is worth >= .2.
  - (P5) Against no teacher (EXP-49's counterfactual, same runs), the random teacher is again worth > 0 by more than 2 SEM.
- Decision rule (written before the pilot): P1-P3 hold -> the form-matched null fixes EXP-49's failure, and v2 (stake, standing, colluding verifiers) is built on it; P1 holds but P3 fails -> fakes are priced out but skill is not ranked at this sample size, and pay needs aggregation over more receivers before it can scale with skill; P1 fails -> the null is not enough, and the measure needs a second guard.
- Pilot (1 seed block, 3 students per teacher, exact run conditions, `exp/EXP-52-pilot.out`), read before the full run: against the null, random sits at +.01, wrong-chain -.20, echo -.22, but know-4 is also near zero (-.05) and Spearman(worth, k) is -.18 (n=24); against no teacher know-4 +.31 and random +.21. Single-student worths stay noisy (SEMs .10-.24 at n=6). Nothing at a floor or ceiling; no design change. The full run reuses the pilot's block-0 rows and adds 9 students per teacher in block 0 and blocks 1-2.
- Result: PENDING. Verdict: PENDING.

## Reflection
- PENDING (after the run).
