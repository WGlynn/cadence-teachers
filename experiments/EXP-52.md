# EXP-52: Noesis-lite v1.1, priced against a null contribution of the same form

- Date: 2026-10-13 | Cadence version: 0.83.0 (`23dba71`) | Program iter: iter35 (program evidence, logged 2026-10-16)
- Script: `exp/EXP-52_noesis_lite_null_counterfactual.py` | Evidence: `exp/EXP-52-pilot.*`, `exp/EXP-52-full.json/.jsonl/.out`

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
- Result (3 seed blocks x 12 students x 7 teachers, each lesson on two independent students: 72 worth samples per teacher per counterfactual; per-state accuracy on unseen weather after 20 attempts alone):

  | teacher | taught acc | worth vs null (SEM) | pay share vs null | worth vs no teacher (SEM) |
  |---|---|---|---|---|
  | know-1 | .647 | -.019 (.042) | .058 | +.188 (.045) |
  | know-2 | .668 | +.057 (.045) | .295 | +.232 (.045) |
  | know-3 | .648 | +.012 (.045) | .163 | +.223 (.039) |
  | know-4 | .661 | +.013 (.044) | .275 | +.167 (.048) |
  | random | .589 | -.073 (.044) | .159 | +.104 (.046) |
  | wrong-chain | | -.205 (.041) | .050 | +.005 (.044) |
  | echo | | -.268 (.043) | .000 | -.090 (.038) |

  Mean accuracy of the null twins is about .65 and of the untaught twins about .46. Check held (random vs null -.073, within 2 SEM of zero). P1 FAILED on pay, held on means: every fake's mean worth is at or below zero (random -.07, wrong-chain -.21, echo -.27), but finalization noise still pays fakes .209 of the pot. P2 FAILED (genuine .791). P3 FAILED (means not ordered by k; Spearman .06, n=288). P4 FAILED (know-4 +.013). P5 HELD (vs no teacher, random +.104, 2.3 SEM: EXP-49's effect reproduces).
- Verdict: BOUNDARY. 1 of 5 held (plus the check). The form-matched null does what it was built for on average: it removes the fakes' positive worth and prices harmful teaching below zero. What it reveals is the deeper limit: in this lesson protocol (40 attempts, labels only on executed mistakes in guided windows), a teacher that knows all four stages is worth no more than one that labels at random (.661 vs .648 accuracy; both about .2 above no teacher). The student learns from being corrected, not from what it is told, so there is no information transfer for a market to pay for, and pay cannot follow skill. Decision rule: P1 held on means and failed on pay; P3 failed; the measure separates harm from help but not knowledge from noise here.

## Reflection
- What it means: EXP-49's failure was half fixed and half explained. Fixed: against a null of the same form, fakes no longer earn on average. Explained: genuine teachers earned in EXP-49 for the same reason the random teacher did, the correction event itself, not its content. At 40 attempts with sparse corrections, the memory student's gain from a perfect teacher equals its gain from a random one. For Noesis this is the sharpest version of the lesson so far: before pricing a contribution's information, check that the receiving process can take information in through that channel at all; a measure can be correct and still have nothing to measure.
- Process: pre-registered and pushed before the pilot; the pilot already showed know-4 near zero against the null, and the design was kept, not tuned; the untaught twin reproduced EXP-49 inside the same runs, which pins the comparison. Limits: one lesson length (40); EXP-46's caregiver arm at 120 attempts reached .94, so label content may matter at longer budgets (not tested with a random-label control there); skill set by oracle subsets, not by trained teachers; the .125 finalize bar on single-student worths is too loose for this noise.
- Lesson: test that the channel carries content before building a market on it: compare a perfect teacher with a random one on the same protocol first.
- Next: EXP-53, does label content matter at all: know-4 vs random-label teachers at 40, 120 and 240 attempts on the same chamber. If content starts to matter at longer budgets, Noesis-lite needs longer lessons; if it never does, Cadence's teaching path in this protocol carries little content, which is worth telling upstream.
