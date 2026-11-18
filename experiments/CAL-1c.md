# CAL-1c: does training on several consistent-wrong forms let the learned v(S) price a wrong form it never saw?

> Will's go 2026-11-18 ("yes"), the Will-gated V(S) rung the program has waited on since CAL-1b. The Pre-registration section is fixed at its commit; Status, Summary and Reflection are filled in after the run.

- Date: pre-registered 2026-11-18 | Cadence version: 0.94.0, pinned from a separate copy at tag `v0.94.0` (`~/_cadence_v0940`), the library source CAL-1 and CAL-1b ran on, not the clone the monitor keeps current | Program iter: iter62 (off-ladder)
- Script: `exp/CAL-1c_calibration_vs.py` (harness), `exp/CAL-1c_analysis.py` (analysis), `exp/run-CAL-1c.sh` (chain) | Evidence: `exp/CAL-1c-*`

## Pre-registration (written 2026-11-18, before any CAL-1c data)

**Question.** CAL-1 and CAL-1b both ended BOUNDARY on criterion 6. In both, a learned v(S) graded by calibration beat consensus and priced the fakes it was trained on. In both, it overpriced the one fake it had not seen. In CAL-1 that fake did more harm than anything in training (wrong-map, +.098). In CAL-1b it combined harms in a new way (wrong-map, +.110 in every cell of the cause table), even though a pure WAIT fake was in training and was itself priced within +.017. CAL-1b's lesson: training on one pure harm teaches that harm, not harm in general, so a test of generalization needs training that spans the kind of harm with several forms.

CAL-1c gives training three consistent-wrong forms: WAIT at every stage, wrong-chain's map, and fixed non-WAIT wrong maps that cover every stage and wrong action. It then asks whether the same procedure prices a held-out wrong form that no trained teacher has within one state, and whether it keeps its calibration on everything else. For the Noesis design this is the direct test of whether a calibration-graded judge holds against a new kind of fake, within the scope stated under "What CAL-1c cannot show".

**What is unchanged from CAL-1 and CAL-1b.** Everything not listed under "What changes": the student side (EXP-77b's instrument through EXP-62's code: delayed-credit brain, founder lateral, weather chamber, corrective schedule, lesson 80, 20 attempts alone, 16 unseen states), the composite zero Z (per-student mean of null, untaught, random), worth W (mean over a teacher's students of taught accuracy minus Z), teachers with a fixed identity, the 192-label probe, the 21 probe features, the predictors (L, S1, S2, K, A, N0) and their procedures, the metrics, the paired bootstrap, the noise ceiling, the blocks (training 8 groups x 3 students, held-out 8 x m, audition 1 per held-out group, full crossing within groups), the pilot rule P1 to P4, the probe-only identities (16 probe-gamer know-4s, 64 wrong-chain clones), and the exploratory per-zero report. CAL-1.md's Pre-registration section is the reference for each; CAL-1b.md for the wait class and P4.

**What changes.**
1. **Two new map classes.** A map teacher gives the same wrong label every time it is at a given stage, on the probe and in every lesson. It is consistent, confident and never right, like wrong-chain, whose map is [1, 2, 3, 0] (at each stage it names the next stage's right action).
   - **nowait-map (trained, and also held out as new instances):** each stage's label is one of the three wrong actions other than WAIT.
     - Training instances (16): the 16 maps are drawn together so that each stage's labels are spread evenly over its three wrong actions, which puts every (stage, wrong action) pair in 5 or 6 training maps. The draw is a seeded shuffle per stage (seed 15_050_000), repeated until the 16 maps are distinct and none is wrong-chain's map. The k-th training instance in block order gets the k-th map.
     - Held-out and pilot instances: drawn per instance from the identity seed, one non-WAIT wrong action per stage, redrawn from the same stream until the map equals no training map and is not wrong-chain's map.
     - Why joint and balanced, disclosed: the analysis was tested on synthetic rows before any data (see Prior knowledge). With 16 independently drawn maps, one cell (stage 3 labelled 1) appeared in a single training map, its ridge weight was barely identified, and held-out maps that used it were extrapolated far. Balancing removes that artifact of the draw; it does not change the procedure.
   - **mixed-map (held-out only, the novel form):** CAL-1's wrong-map draw (a fixed wrong action per stage from the four wrong actions, WAIT included, from the identity seed), redrawn from the same stream until the map has at least one WAIT stage and at least one non-WAIT stage. No trained teacher mixes WAIT with other wrong labels: wait labels WAIT everywhere, wrong-chain and nowait-map never label WAIT. So every mixed-map is a form absent from training, and its maps are disjoint from every trained map by construction. It replaces wrong-map: with CAL-1's draw on these seeds, 7 of the 16 held-out wrong-maps would have had no WAIT stage, the same form as the trained nowait-map.
2. **Pools of 28 per group.** CAL-1's 12 graded per training group (10 held-out) are kept, so the range stretch is not confounded with a smaller graded pool as it was in CAL-1b; the four new slots go to wait and nowait-map.

   | class | training (224) | held-out (224) | per group, training / held-out |
   |---|---|---|---|
   | graded | 96 | 80 | 12 / 10 |
   | know-1, know-2, know-3, know-4 | 8 each | 8 each | 1 each / 1 each |
   | random, wrong-chain, echo, anti-echo, wait, nowait-map | 16 each | 16 each | 2 each / 2 each |
   | mixed-map | 0 | 16 | 0 / 2 |

   Order within a group: graded, then know-1 to 4, then the fakes in pairs in the order of the table. The graded count matches CAL-1 (96); the graded share of training is 43% (CAL-1 50%, CAL-1b 42%). The forms table below has a cell (L-cal1) that is CAL-1's training pool exactly.
3. **Fresh seeds** (nothing in these ranges appears in any `exp/*.py` or `exp/*.sh`; checked 2026-11-18):
   - Students, spaced by 10: training 14_100_000 + 10s (s = 0 to 23), held-out 14_200_000 + 10s (s = 0 to 8m - 1), audition 14_300_000 + 10g (g = 0 to 7), pilot 14_900_000 + 10s (s = 0 to 3).
   - Teacher identities: training 15_000_000 + t, held-out 15_100_000 + t, probe-only 15_200_000 + t, pilot 15_900_000 + t; the training nowait-map balance 15_050_000.
   - Teacher ids: training t (0 to 223), held-out 300 + t, pilot 600 + t. Lesson label noise: 60_000_000 + 1000 x id + j (j the student's index in its block; audition j = 900 + g). Probe noise: 70_000_000 + id; probe-only identities 70_000_700 + t.
   - Analysis: permutations seed 1, bootstraps seed 0 (as CAL-1).
4. **Criterion 6 and K1 cover seven fake classes:** random, wrong-chain, echo, anti-echo, wait, nowait-map, mixed-map.
5. **Version and threads.** Cadence 0.94.0 imported from `~/_cadence_v0940/src`, as CAL-1b (the monitor clone is at 0.101.0; 0.95.2 changed how a lesson starts, so the V2 gate fails there by construction). Every run line sets `PYTHONPATH=~/_cadence_v0940/src`; every row records the imported version and path. BLAS threads are pinned to 1 (OMP, OpenBLAS, MKL, NumExpr), set in the chain and inside the harness before NumPy loads; V2 checks identity under that setting.
6. **V6, an identity audit before any run** (`MODE=ids`, no brain involved): training nowait-maps hold no WAIT, are distinct, are not wrong-chain's map, and cover every (stage, non-WAIT wrong action) cell with counts within 1 per stage; no mixed-map is in training; every held-out and pilot mixed-map mixes WAIT and non-WAIT stages; no held-out or pilot map equals a training map, wait's map or wrong-chain's map.

**The identities, drawn when this was written** (identity draws are deterministic functions of the seeds and involve no student; they are not outcomes). Maps are written stage 0 to 3; 4 is WAIT.
- Training nowait-map (16): 1031 3230 1210 2202 3301 2011 2030 1212 3001 2211 1332 1310 2032 3200 3302 1330. Cell counts (stage x action 0 to 4): [0, 6, 5, 5, 0], [5, 0, 6, 5, 0], [5, 5, 0, 6, 0], [6, 5, 5, 0, 0].
- Held-out nowait-map (16): 1202 3300 3210 3312 2201 3332 2332 1311 1012 3201 1200 3332 2310 2001 1331 3031.
- Held-out mixed-map (16): 2414 2411 3412 4034 4234 4204 1304 4011 1342 1240 2341 1004 2334 2402 4214 4404. WAIT stages: 10 with one, 5 with two, 1 with three.
- Pilot: nowait-map 1011 1331; mixed-map 3314 1401.

**Primary procedure (the verdict).** CAL-1's procedure unchanged, on CAL-1c's rows: L = ridge on the 21 standardized probe features, penalty by leave-one-group-out CV over the 8 training groups, isotonic map (clipped at its ends) fitted on the out-of-fold scores, all 224 training teachers.

**The forms table (registered, reported beside the verdict, not part of it).** L's whole procedure refitted on the same rows with training instances of named classes dropped, each read for criterion 6 on every fake class, plus its floor, rho, MSE on all held-out teachers and MSE on the honest classes (graded and know-k, 112 held-out teachers):

| cell | training | what it is |
|---|---|---|
| primary | all 224 | the verdict |
| L-nomap | 208, no nowait-map | CAL-1's pool plus wait: the range stretch with the graded count kept |
| L-nowait | 208, no wait | CAL-1's pool plus the non-WAIT maps |
| L-cal1 | 192, neither | CAL-1's training pool exactly (classes, counts, shares), on fresh seeds |

Also: the primary's raw ridge output on mixed-map (no map, no floor), and MSE of primary minus L-cal1 on the honest classes and on all held-out teachers, with a paired bootstrap 95% interval (held-out teachers resampled within group, 2,000, seed 0, models fixed).

Readings, fixed now:
- Novel form (mixed-map):
  - R1. Primary passes and L-nomap fails: the non-WAIT maps in training are what priced the novel form (spanning the kind worked where one pure harm did not).
  - R2. Primary and L-nomap both pass: on these rows the non-WAIT maps were not needed; the pass comes with the rest of the design (CAL-1's 96 graded teachers, the wait class, fresh seeds).
  - R3. Primary fails: training on several consistent-wrong forms did not make the procedure price the novel form within one state.
  - R4. L-cal1 passes: the CAL-1 and CAL-1b failure on the novel class did not replicate on these seeds (the novel class here is mixed maps only); R1 to R3 are read with that caveat.
  - R5. Primary fails on nowait-map (a trained form, new maps): the procedure does not price new instances of a trained consistent-wrong form within one state, so the binding limit is the forecaster's form (additive in per-stage label shares), not only which forms training covers.
- Near the bar (random and anti-echo, the two classes CAL-1b newly overpriced):
  - N1. Primary passes both: adding wait and nowait-map to CAL-1's training pool, its 96 graded teachers kept, does not cost calibration near the bar on these rows; CAL-1b's failures there go with its smaller graded pool or its draw, not with the range stretch alone.
  - N2. Primary fails one or both and L-cal1 passes the failing ones: adding the consistent-wrong forms costs calibration near the bar on these rows; L-nomap (the stretch alone) and L-nowait say which form, if one alone does.
  - N3. Primary fails one or both and L-cal1 fails them too: these classes fail near the bar on these seeds even with CAL-1's exact training pool; the stretch is not shown to be the cause.
- Honest classes (MSE primary minus L-cal1): H1, interval above 0: training on the consistent-wrong forms cost calibration on honest teachers; H2, interval below 0: it improved it; H3, interval spans 0: no change shown.

**Decision rules (as CAL-1 and CAL-1b, with seven fake classes).**
- VOID, before any run: V6 (the identity audit) fails; V1, the construction audit (`exp/EXP-77b_construction_audit.py`, unchanged) does not print ADMITTED BY CONSTRUCTION, or CAL-1c's zero arms do not call EXP-62's audited entry point (inspect check); V2, CAL-1c's twin on EXP-77b student 0 (seed 9_000_000) does not reproduce the null, untaught, random (zero and teacher paths), know-4, wrong-chain, echo and anti-echo arms of `exp/EXP-77b-full.jsonl` on the pinned 0.94.0 with BLAS threads at 1. Any failing means no run.
- VOID, after the run: V3, split-half reliability of held-out W below .5; V4, held-out know-4 mean W below .10; V5, any row imported a Cadence other than 0.94.0 from `~/_cadence_v0940`.
- CONFIRM if all hold: 1. rho_L >= .5. 2. rho_L minus rho_S has its 95% interval above 0, for S1 and S2. 3. MSE_L minus MSE_S has its 95% interval below 0, for S1 and S2. 4. rho_L above N0's 99th percentile and MSE_L below its 1st percentile (1,000 refits). 5. L's skill against climatology has its 95% interval above 0. 6. For each of random, wrong-chain, echo, anti-echo, wait, nowait-map and mixed-map: mean(forecast_L minus W) + 1.645 SE < 1/16.
  Then: with training spanning the consistent-wrong kind, the learned v(S) prices every fake class within one state, including a form no trained teacher has, and keeps its edge over consensus. That is the CAL-1-family CONFIRM CAL-2 waits on, with the condition named.
- KILL: K1, any of the seven fake classes' mean L forecast >= the know-2 class's; K2, S1 or S2 beats L on both metrics with both intervals excluding 0.
- BOUNDARY: anything else, failing criteria named. Readings fixed now:
  - failing 6 on mixed-map: training on several consistent-wrong forms still does not price the novel form within one state (the forms table says more);
  - failing 6 on nowait-map: reading R5;
  - failing 6 on random or anti-echo only: the judge prices the novel form but not the classes near the bar; the N readings say whether the stretch is the cause;
  - failing 6 on wait, wrong-chain or echo: a trained class at the bottom of the range is mispriced (the isotonic map's low blocks mix classes);
  - failing 2 or 3 against S2 only: consensus prices as well as learning from outcomes, as in CAL-1's reading.
- Reported, not decisive: every CAL-1b reported item (A and K against L, within-class rho, L ordering know-1 to 4, L's weights, S2 coordinated, probe-gamer, hindsight ratio, Brier for [W >= 1/32], L on 1, 3, 6 probe labels per context, student-level bootstrap, the exploratory per-zero report), the forms table, plus three new items: two-sided calibration per fake class (|mean(L minus W)| + 1.645 SE < 1/16, "priced within one state both ways"; a class that passes criterion 6 but fails this is underpriced: safe against the fake, not calibrated on it); consensus overpricing per fake class (S2 through its own isotonic map, read as criterion 6 reads L); mixed-map by its number of WAIT stages (forecast, W, n). L-archive is not repeated.

**Pilot rule (CAL-1b's, with P5).** One group of 28 held-out-style teachers (10 graded, know-1 to 4, 2 each of random, wrong-chain, echo, anti-echo, wait, nowait-map, mixed-map) x 4 pilot students plus zero twins: 124 twins. Chain print per teacher (class, identity, S1, S2, K, W per student, mean). PILOT STOP if P1 know-4 W < .10, P2 SD of the 28 mean W < .05, P3 projected reliability at m = 8 < .7, P4 both wait teachers' W above -.1215 (CAL-1's training floor), or P5 both nowait-map teachers' mean W above -1/16 (the new trained form carries no harm, so the design's premise fails; redesign). m = 6 if projected reliability at m = 6 >= .7, else 8. Pilot data never enters the verdict. Nothing else may change after the pilot.

**RUN GATE.** (1) Prediction: below. (2) Window: the pilot's P2 to P5 check that worth spreads, the wait class stretches the range, and the new trained form carries harm. (3) Variance: P2 and P3. (4) Metric: a forecaster that prices everything low passes criterion 6 but fails criteria 3 and 5. (5) Chain: probe labels, features, L's score, the isotonic map, the forecast, graded against realized W; the pilot prints each link per teacher.

**Prior knowledge (flagged).**
- Read for planning: CAL-1.md and CAL-1b.md in full and `exp/CAL-1b-full-analysis.out` (the per-class table, the cause table, L's weights). The post hoc WAIT-count tables in both write-ups were read: CAL-1b's wrong-maps with 0, 1, 2, 3 WAIT stages realized W -.196 (n 3), -.195 (n 8), -.270 (n 4), -.208 (n 1), and L forecast them at -.005, -.100, -.127, -.351; CAL-1's at -.113 (n 3), -.174 (n 11), -.332 (n 2).
- The analysis was tested before any data on synthetic rows from a world written for the test (class-level worth, stage-weighted graded worth, normal noise), in a scratch directory outside the repo; none of it is evidence about the instrument and none of it is committed. It found the cell-coverage artifact named under "What changes" (with independent draws, held-out nowait-maps were overpriced by about +.17 in that world; with the balanced draw, about +.09). The remaining gap in that world came from the forecaster's form: a ridge additive in per-stage label shares could not fit every class of a world where harm is not linear in those shares, which is why R5 is registered. The balanced draw was chosen because of that test; the procedure was not changed.
- The 16 held-out mixed-maps and their WAIT counts were drawn and listed when this was written.

**Prediction (planning numbers, written before data).**
- Realized W: wait -.40 to -.50; nowait-map about -.15 (between wrong-chain, -.08 to -.13 in CAL-1 and CAL-1b, and CAL-1b's no-WAIT wrong-maps, -.196); mixed-map about -.20; random about -.03; anti-echo about -.01.
- rho L about .93, S2 about .90; L beats S2 on rank and MSE (about 75%); skill about .85.
- Primary on mixed-map: a forecaster additive across stages prices a map with one WAIT stage near nowait-map plus a quarter of the wait gap (about -.22) and with two or three WAIT stages lower (about -.30 to -.37), against realized worth near -.20 to -.27. So mixed-map is expected to be underpriced if anything: criterion 6 passes (about 65%), the two-sided reading fails (about 50%).
- Primary on nowait-map (new maps of a trained form): criterion 6 fails about 45% (the synthetic test showed the forecaster's form can miss new maps).
- Near the bar: random and anti-echo each fail about 35%.
- Forms table: L-cal1 fails mixed-map (about 85%); L-nomap fails mixed-map (about 60%); R1 about 40%; H3 about 55%, H1 about 35%.
- Verdict: CONFIRM about 25%; BOUNDARY about 70% (most likely on nowait-map or near-the-bar classes; on mixed-map about 35%); anything else about 5%.

**Cost.** 2,480 twins at m = 6 (training 24 x 31 = 744, held-out 48 x 31 = 1,488, audition 8 x 31 = 248); 2,976 at m = 8. At CAL-1b's measured 1.61 s per twin at 4 workers: about 67 min at m = 6, about 80 min at m = 8. Pilot 124 twins, about 3.5 min; V2 about 20 s; analysis about 2 to 4 min (four zeros, 1,000 refits each, plus the forms table). Run detached at 4 workers in one process tree; nothing else heavy alongside. If the pilot's rate projects over 3 hours, stop after the pilot and report the projection.

**What CAL-1c cannot show.** All of CAL-1's and CAL-1b's limits stand (strategic teachers and the probe-gamer, the anchor moves, no time, narrow scope, not M2 or M3, students a fixed draw, S2 is plurality agreement, an honest world, the pinned version). Added: (1) the novel form is new as a combination, not as a family: every mixed-map is a fixed per-stage map, and its probe features are per-stage one-hots on cells that trained teachers use. So a pass shows that the learned price composes across stages, not that it extrapolates to a new family of fake (context-dependent maps, or teachers that behave differently when probed). (2) The forms table is one set of rows, not four runs; its cells share students and teachers. (3) The training maps are balanced by design; a market whose fakes cluster on a few cells would give the forecaster less coverage than this. (4) Sixteen instances per class: per-WAIT-count readings are small groups.

**Where CAL-1c sits in the program.** Off-ladder, as CAL-1 and CAL-1b: no milestone moves on any verdict. A CONFIRM is the CAL-1-family CONFIRM CAL-2 waits on, on the same instrument, with "training spans the consistent-wrong kind" named as the condition; a BOUNDARY keeps CAL-2 waiting, and the forms table says whether the next rung is about training coverage or about the forecaster's form.

## Status
- 2026-11-18: pre-registration written, before any CAL-1c data. Harness, analysis and chain written from CAL-1b's with only the registered changes, and committed with this file. V6 identity audit PASS when written (the maps above). To be timestamped (stamp_commit.py) before V1.
- 2026-11-18 15:07 CT: pre-registration committed `34a04cc` together with the harness, analysis and chain. The Pre-registration section has not changed since that commit. Timestamp: `stamp_commit.py ~/cadence-lab 34a04cc CAL-1c` printed "stamped CAL-1c 34a04cc on 3 calendars" (OpenTimestamps; the tool publishes to WGlynn/provenance). Two automatic checkpoint commits (`7521008` at 14:55, `71bb6d1` at 15:04) caught the scripts mid-edit before that; both came before any CAL-1c data.
- V6 identity audit PASS (`exp/CAL-1c-v6-ids.out`). V1: `exp/EXP-77b_construction_audit.py` unchanged, ADMITTED BY CONSTRUCTION (`exp/CAL-1c-v1-audit.out`); inspect check PASS (`exp/CAL-1c-v1-inspect.out`). V2: CAL-1c's twin on EXP-77b student 0 (seed 9_000_000) on the pinned 0.94.0 with BLAS threads at 1: IDENTICAL on all eight arm paths (15 s; `exp/CAL-1c-v2-gate.out`).
- Pilot (one group of 28 x 4 students, 124 twins, 200 s, 1.61 s per twin at 4 workers): know-4 W +.427; SD of the 28 mean W .213; v_b .0403, v_w .0203; projected reliability .922 at m = 6, .941 at m = 8; the two wait teachers W -.432 and -.432 (P4 clear); the two nowait-map teachers -.182 and -.151 (P5 clear); mixed-map (reported only) -.182 and -.104. No stop; m = 6 by the rule (`exp/CAL-1c-pilot.out`, `CAL-1c-pilot.json`, chain log `exp/CAL-1c-chain-pilot.log`). Projected full run: 2,480 twins, about 67 min, under the 3-hour stop.
- Full run started 15:11:52 CT at m = 6, 4 workers, detached; probes for all 528 instances written to `exp/CAL-1c-full-probes.json` before any twin ran.

## Summary
- PENDING (filled in after the run).

## Reflection
- PENDING (filled in after the run).
