# CAL-1b: does the learned v(S) price a novel harmful fake when training spans that harm?

> Pre-registration written 2026-11-14 before any CAL-1b data, under Will's delegation of the V(S) program (2026-11-13: "you decide the Vs program"; CAL-1b approved as the next run the same day, FRONTIER 2026-11-13). The Pre-registration section is fixed at its commit; Status, Summary and Reflection are filled in after the run.

- Date: pre-registered 2026-11-14 | Cadence version: 0.94.0, the same library source CAL-1 ran on. It is imported from a separate copy of the code at tag `v0.94.0` (`~/_cadence_v0940`), not from the clone the monitor keeps current. | Program iter: iter59 (off-ladder)
- Script: `exp/CAL-1b_calibration_vs.py` (harness), `exp/CAL-1b_analysis.py` (analysis) | Evidence: `exp/CAL-1b-*`

## Pre-registration (written 2026-11-14, before any CAL-1b data)

**Question.** CAL-1 (BOUNDARY, 2026-11-13) priced teachers before they taught: rho .928, skill .838. It priced each of its four trained fake classes within one state of what they deliver (random came closest to the bar: overpriced +.012, upper bound +.032 against 1/16). It overpriced the one novel fake, wrong-map, by +.098, which failed criterion 6. Its reflection named two possible causes, both found after the verdict:
- (a) A harm no trained class had. wrong-map's extra harm tracks WAIT labels, and no trained class labels WAIT consistently.
- (b) A map that cannot go below its training range. The isotonic map stops at the lowest trained level (-.1215), and 11 of 16 wrong-map instances realized less.

CAL-1b asks two things. First, when the training block holds a fake that carries that harm, so the trained range reaches below wrong-map, does the same procedure price wrong-map within one state? Second, on the same rows, which change is enough on its own: the harm in training, or a forecast with no floor?

**What is unchanged from CAL-1.** Everything not listed under "What changes": the student side (EXP-77b's instrument through EXP-62's code: delayed-credit brain, founder lateral, weather chamber, corrective schedule, lesson 80, 20 attempts alone, 16 unseen states), the composite zero Z (per-student mean of null, untaught, random), worth W (mean over a teacher's students of taught accuracy minus Z), teachers with a fixed identity, the 192-label probe, the 21 probe features, the predictors (L, S1, S2, K, A, N0) and their procedures, the metrics, the paired bootstrap, the noise ceiling, the blocks (training 8 groups x 3 students, held-out 8 x m, audition 1 per held-out group, full crossing within groups), the pilot rule, and the probe-only identities (16 probe-gamer know-4s, 64 wrong-chain clones). CAL-1.md's Pre-registration section is the reference for each.

**What changes.**
1. **A new trained fake class, wait:** a teacher that labels WAIT (action 4) at every context, on the probe and in every lesson. It is consistent, confident and never right, like wrong-chain, and it carries the harm CAL-1's post hoc check tied to wrong-map. In CAL-1, wrong-map instances with two WAIT stages realized W -.332 (n 2), so wait is expected below every CAL-1 trained class.
2. **Pool per group of 24** (graded slots give way; the trained fakes keep 2 per group each):

   | class | training (192) | held-out (192) | per group, training / held-out |
   |---|---|---|---|
   | graded | 80 | 64 | 10 / 8 |
   | know-1, know-2, know-3, know-4 | 8 each | 8 each | 1 each / 1 each |
   | random, wrong-chain, echo, anti-echo, wait | 16 each | 16 each | 2 each / 2 each |
   | wrong-map | 0 | 16 | 0 / 2 |

   wrong-map stays the one class absent from training, drawn exactly as in CAL-1 (a fixed wrong action per stage, WAIT included, drawn per instance from its identity seed).
3. **Fresh seeds** (nothing below 12_000_000 is used; checked against `exp/*.py`, no file names any number in these ranges):
   - Students, spaced by 10: training 12_100_000 + 10s (s = 0 to 23), held-out 12_200_000 + 10s (s = 0 to 8m - 1), audition 12_300_000 + 10g (g = 0 to 7), pilot 12_900_000 + 10s (s = 0 to 3).
   - Teacher identities: training 13_000_000 + t, held-out 13_100_000 + t, probe-only 13_200_000 + t, pilot 13_900_000 + t.
   - Lesson label noise: 40_000_000 + 1000 x id + j (id: training 0 to 191, held-out 200 to 391, pilot 500 to 523; j the student's index in its block, audition j = 900 + g).
   - Probe noise: 50_000_000 + id; probe-only identities 50_000_700 + t.
   - Analysis: permutations seed 1, bootstraps seed 0 (as CAL-1).
4. **Criterion 6 covers six fake classes:** random, wrong-chain, echo, anti-echo, wait, wrong-map. K1 covers the same six.
5. **The version is pinned, not taken from the clone.** The monitor moved `~/_cadence_study` to 0.99.0 on 2026-11-14. Two upstream changes break the V2 gate there by construction. 0.95.2 changed how a lesson starts (its free phase now starts from the stream's activity, not from rest). 0.95.0 put the recall memory in every brain the harness composes. The monitor's tag bisect found 0.95.1 IDENTICAL and 0.95.2 DIFFERS. CAL-1b imports 0.94.0 from `~/_cadence_v0940/src`, CAL-1's library source, so that CAL-1b and CAL-1 share one instrument. Every run line sets `PYTHONPATH=~/_cadence_v0940/src` and prints the imported version and path; a run that imports anything else is void.

**Primary procedure (the verdict).** CAL-1's procedure unchanged, on CAL-1b's rows: L = ridge on the 21 standardized probe features, penalty by leave-one-group-out CV over the 8 training groups, isotonic map (clipped at its ends) fitted on the out-of-fold scores, all 192 training teachers including the 16 wait instances.

**Cause separation (registered, reported beside the verdict, not part of it).** Four forecasters for L on the same rows, with wrong-map's criterion-6 test (mean(forecast minus W) + 1.645 SE < 1/16) read for each:

| | isotonic map (CAL-1's, clipped) | raw ridge output (no map) |
|---|---|---|
| training with wait (192 teachers) | **primary** | L-raw |
| training without wait (176 teachers: the 16 wait instances dropped; the rest of the procedure unchanged) | L-nowait (CAL-1's training classes on fresh seeds) | L-nowait-raw |

The raw ridge output is the final model's held-out prediction used directly as the forecast. It is already in units of W (the ridge is fitted to W), so it is the one forecast in the procedure without a floor: it extrapolates linearly. Readings, fixed now:
- L-nowait is CAL-1's procedure and training classes on fresh seeds. It is expected to fail on wrong-map as CAL-1 did; if it passes, CAL-1's failure did not replicate and the separation below is read with that caveat.
- Primary passes and L-nowait-raw fails: the missing harm in training was the cause; removing the floor alone does not fix it.
- L-nowait-raw passes: the floor was a sufficient cause; the ridge already scored wrong-map low enough and only the map hid it.
- Primary and L-nowait-raw both pass: either change alone is enough.
- Primary fails: putting the harm in training did not make the procedure price wrong-map within one state (what is left is generalization to a new combination of known harms, or a floor that still binds).
- Also reported: the same four cells for the held-out wait class (under the without-wait training it is a second novel fake, below the trained range by construction), L's per-stage weights on the WAIT share in both trainings, and the training floor (the isotonic map's lowest level) in both.

**Decision rules (as CAL-1, with the six fake classes).**
- VOID, before any run: V1, the construction audit (`exp/EXP-77b_construction_audit.py`, unchanged) prints ADMITTED BY CONSTRUCTION and CAL-1b's zero arms call EXP-62's audited entry point (inspect check); V2, CAL-1b's twin on EXP-77b student 0 (seed 9_000_000) reproduces the null, untaught, random (zero and teacher paths), know-4, wrong-chain, echo and anti-echo arms of `exp/EXP-77b-full.jsonl`, on the pinned 0.94.0. Either failing means no run.
- VOID, after the run: V3, split-half reliability of held-out W below .5; V4, held-out know-4 mean W below .10; V5, any row imported a Cadence other than 0.94.0 from `~/_cadence_v0940`.
- CONFIRM if all hold: 1. rho_L >= .5. 2. rho_L minus rho_S has its 95% interval above 0, for S1 and S2. 3. MSE_L minus MSE_S has its 95% interval below 0, for S1 and S2. 4. rho_L above N0's 99th percentile and MSE_L below its 1st percentile (1,000 refits). 5. L's skill against climatology has its 95% interval above 0. 6. For each of random, wrong-chain, echo, anti-echo, wait and wrong-map: mean(forecast_L minus W) + 1.645 SE < 1/16.
  Then: with the harm in training, the learned v(S) prices every fake class within one state, including one absent from training, and CAL-1's miss is attributed by the cause table.
- KILL: K1, any of the six fake classes' mean L forecast >= the know-2 class's; K2, S1 or S2 beats L on both metrics with both intervals excluding 0.
- BOUNDARY: anything else, failing criteria named. Readings fixed now: failing 6 on wrong-map only means the procedure still misprices a novel fake although training spans its harm; failing 6 on wait only means a trained class sitting at the bottom of the range is itself mispriced (the isotonic map's lowest block mixes wait with other classes); failing 2 or 3 against S2 only means consensus prices as well as learning from outcomes, as in CAL-1's reading.
- Reported, not decisive: every CAL-1 reported item (A and K against L, within-class rho, L ordering know-1 to 4, S2 coordinated, probe-gamer, hindsight ratio, Brier for [W >= 1/32], L on 1, 3, 6, 12 probe labels per context, student-level bootstrap, the exploratory per-zero report) and the cause table above. L-archive is not repeated (it reads EXP-77b's lessons, which do not change).

**Pilot rule (CAL-1's).** One group of 24 held-out-style teachers (8 graded, know-1 to 4, 2 each of random, wrong-chain, echo, anti-echo, wait and wrong-map) x 4 pilot students plus zero twins, 108 twins. Chain print per teacher. PILOT STOP if P1 know-4 W < .10, P2 SD of the 24 mean W < .05, or P3 projected reliability at m = 8 < .7. m = 6 if projected reliability at m = 6 >= .7, else 8. Pilot data never enters the verdict. Added for CAL-1b: the pilot prints the two wait teachers' W; if both are above -.1215 (CAL-1's training floor), wait does not extend the range and the run stops for a redesign (P4).

**Prediction (planning numbers, written before data).**
- wait: W -.35 to -.50 (below every CAL-1 trained class; CAL-1's two-WAIT wrong-maps -.332).
- wrong-map: W about -.18 (CAL-1 -.183).
- Training floor with wait: below -.25; without wait: about -.12 (CAL-1 -.1215).
- rho_L about .92, rho_S2 about .90; L beats S2 by a small margin as in CAL-1; skill about .85 (a wider W range raises climatology's MSE).
- Cause table, wrong-map criterion 6: L-nowait fails (about 85%); primary passes (about 60%); L-raw passes (about 60%); L-nowait-raw fails (about 60%), because a ridge trained without a consistent WAIT class has weak weights on WAIT shares.
- wait under the without-wait training: overpriced by more than wrong-map was in CAL-1 (forecast at the floor, about -.12, against W about -.4).
- Verdict: CONFIRM about 50%; BOUNDARY on criterion 6 (wrong-map or wait) about 40%; anything else about 10%.

**Cost.** CAL-1's: 2,160 twins at m = 6 (training 648, held-out 1,296, audition 216), CAL-1 measured 1.37 s per twin at 4 workers on 0.94.0, so about 50 min; about 60 min at m = 8. Pilot about 3 min, gate about 15 s, analysis a few minutes (the cause table adds three ridge fits). Run detached at 4 workers on this PC.

**What CAL-1b cannot show.** All of CAL-1's limits stand (strategic teachers, the anchor moves, no time, narrow scope, not M2 or M3, students a fixed draw, S2 is plurality agreement, an honest world). Added: (1) wait is a single deterministic class, so "training spans the harm" means one class carries it in pure form; a forecaster that prices wrong-map right here may still misprice a harm spread thinly over many classes. (2) The cause table is one set of rows, not four runs; the four cells share students and teachers, so they separate causes within this draw, not across draws. (3) The version is 0.94.0, not current upstream; whether a learned v(S) prices teachers on 0.95.2's lesson law is a separate question (a later run).

**Where CAL-1b sits in the program.** Off-ladder, as CAL-1: no milestone moves on any verdict. A CONFIRM is the CAL-1 CONFIRM that CAL-2 waits on, on the same instrument, with the harm in training named as the condition; a BOUNDARY keeps CAL-2 waiting.

## Status
- 2026-11-14: pre-registration written, before any CAL-1b data; to be committed and timestamped (stamp_commit.py) before V1.

## Summary
- (filled in after the run)

## Reflection
- (filled in after the run)
