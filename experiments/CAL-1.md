# CAL-1: calibration-graded v(S) in the teacher market

> Pre-registered `b70748c` on 2026-11-13 with Will's go. The Pre-registration section below is unchanged since that commit; the header lines, Status, Summary and Reflection were filled in after the run.

- Date: pre-registered 2026-11-13 (`b70748c`; drafted 2026-10-27), run the same day | Cadence version: 0.94.0, clone `4cb9c29` (release `2a32a98` plus a test-only commit); V2 identity gate IDENTICAL to EXP-77b's 0.89.0 student 0 | Program iter: iter58 (off-ladder)
- Script: `exp/CAL-1_calibration_vs.py` (harness), `exp/CAL-1_analysis.py` (analysis; committed `8f600ae` before any full-run row was read) | Evidence: `exp/CAL-1-*` (audit, v1, gate, pilot, full jsonl, probes, analysis json and out)

## Pre-registration (DRAFT, written 2026-10-27, before any CAL-1 data)

**Question.** Can a v(S) price a teacher before it teaches? Precisely: before a teacher teaches anyone, can a v(S) that learned from earlier teachers' realized student gain predict a new teacher's worth from that teacher's labels on a fixed probe set, better than signals that use no outcomes (how consistent its labels are, how often it agrees with other teachers), when graded on held-out teachers and fresh students, and without overpricing any fake class, including one it never saw in training?

**Why this run exists, disclosed.** On 2026-10-27 Noesis adopted calibration as its success measure: valuations today graded against independent use later (Noesis `docs/research/calibration-is-homeostasis.md`). Will, the same day: "if v(S) can learn then that means more discovery between cadence teachers and v(S)". The program named CAL-1 as a Will-gated candidate. ETM's C1 ran the same idea on crates.io and found that a plain count of independent users forecast reuse better than Noesis's propagation rule. So a calibration test can rank rival v(S) rules, and the simpler rule can win. The teacher market is the version without lag: worth is realized in minutes as student gain, the fakes are controlled, and independence is controlled (fresh students). In the V(S) transfer track (EXP-08 to EXP-77b), no run has graded a before-teaching forecast against realized worth. EXP-15 scored teachers with an outcome-free peer-prediction rule (the family S2 belongs to), but it compared which mechanism ranked the genuine teacher above a ring; it did not grade a forecast. The nearest other pieces are outside the track. EXP-36 used a probe on a committed copy as a defence against fake need, and its sandbagger fooled the probe, which is the same weak point as CAL-1's probe-gamer. In EXP-32/34 a brain learned whom to teach from the pay it earned, and that learned choice matched random partners. Existing support: EXP-62e priced anti-echo in proportion to the information it carried (about 38% of know-1's information edge, about 38% of its worth edge). Disclosed: this draft was written after reading EXP-77b's full-run data for planning numbers (listed under Prior knowledge) and before any CAL-1 data. The drafter chose the probe, the features and the model; none was tuned on data.

**Preconditions.**
1. Will's go, given by committing this file.
2. EXP-77b's committed verdict is CONFIRM. CAL-1 forecasts worth on the instrument and zero that EXP-77b grades. If EXP-77b's verdict is anything else, CAL-1 does not start and this draft is revised.
3. Cadence is still 0.89.0 (`81345d8`), checked 2026-10-27. If the live clone has moved, the identity gate (V2) runs on the new version first.

**Setup: the student side is EXP-77b.** Delayed-credit brain (`scales={'trace': 12.0}`, founder lateral), weather chamber, corrective schedule (a label only after an executed mistake in a guided window), lesson 80, 20 attempts alone through `step`, per-state greedy accuracy over 16 states on unseen weather. The zero Z is the per-student mean of {null, untaught, random}, admitted by construction (EXP-77b's audit). A teacher's **realized worth W** is the mean over its students of (taught accuracy minus Z on the same student).

**Setup: what is new is the teacher.**
- **A teacher is an instance with a fixed identity.** From EXP-62 to EXP-77b, a "know-2" was redrawn on every student, because its known stages came from the student's label seed. In CAL-1 each instance draws its identity once from its own seed. It keeps that identity on every student and on the probe. Only the per-label noise is reseeded per lesson.
- **Classes.**
  - know-k (k = 1 to 4): a fixed set of k known stages. At those stages it labels the right action; elsewhere a uniform random action (EXP-52's rule).
  - **graded (new):** one reliability p_i per stage, each drawn uniform on [0, 1]. At stage i it names the right action with probability p_i, otherwise a uniform random action. know-k is the corner case p in {0, 1}^4, and random is p = 0. This gives a continuous spread of worth to predict, not just four rungs.
  - random, wrong-chain, echo, anti-echo: the market harness's fake classes, unchanged. random and wrong-chain are the market's versions of EXP-08's fake_random and fake_wrong. echo comes from EXP-49/52 and anti-echo from EXP-62.
  - **wrong-map (new, held-out only):** a fixed wrong action per stage, drawn per instance from the four wrong actions (WAIT included). It has the same form as wrong-chain (consistent, confident, never right), but its map is drawn fresh per instance. At any one stage it agrees with wrong-chain 1 time in 4, and all four stages coincide 1 time in 256. It is the one fake class absent from training. It is new to the estimator, not a new kind of attack: its features lie in the span of the trained fakes (echo's wrong-label shares cover every wrong action).
- **Pool.** Teachers are taught in groups of 24, stratified as below. Within a group, teachers and students are fully crossed: every teacher in the group teaches every student of the group.

| class | training (192) | held-out (192) | per group, training / held-out |
|---|---|---|---|
| graded | 96 | 80 | 12 / 10 |
| know-1, know-2, know-3, know-4 | 8 each | 8 each | 1 each / 1 each |
| random, wrong-chain, echo, anti-echo | 16 each | 16 each | 2 each / 2 each |
| wrong-map | 0 | 16 | 0 / 2 |

- **Blocks.**
  - Training: 8 groups x 3 students (24 students).
  - Held-out: 8 groups x 6 students (48 students, or 64 at 8 per group if the pilot rule says so).
  - Audition: one extra student per held-out group (8 students).

  Every student also gets the three zero twins. Groups spread the student draw over 80 students. In a single fully crossed block, every W would share the same few students' teachability offset.
- **Probe.** Before any teaching, each instance labels a fixed probe set: 16 contexts (stage i, executed wrong action a), with i = 0 to 3 and a any of the four actions other than the right one, 12 times each. That makes 192 probe labels, about one lesson's worth (EXP-77b lessons gave 148 to 226 labels). The labeller is called exactly as in a lesson, `lab(c, a)` after a mistake, on a stub whose `right()` returns the stage's right action. No brain is involved, so probes cost no compute. Probe noise has its own seed. The probe is balanced over stages; lessons are not (in EXP-77b about 30 / 37 / 28 / 5% of know-4's labels fell at stages 0 to 3).

**What an estimator may see before a teacher teaches (the design question, settled here).**
- **Allowed:**
  - the instance's own probe labels, with each probe's context (which stage, and which wrong action was "executed");
  - the probe labels of every other instance in the same block (S2 uses these);
  - for L only, earlier teachers' probe labels together with their realized W on earlier students (the training block).
- **Not allowed:** the right answers (the RIGHTS map), any outcome of the teacher being priced, and any held-out student.
- Two references break these rules on purpose and are not competitors: the answer key K and the audition A.
- Why probes and not lesson streams: an estimator can demand a probe before teaching. A lesson's label stream exists only after a student has been spent.

**Predictors.** Each one produces a score per teacher. Each score is oriented by the sign of its training-block Spearman with W before any held-out metric. Every predictor except A becomes a worth forecast through an isotonic map (score to W, direction from that sign). The map is fitted on the training block and applied to held-out scores, which is C1's procedure. Held-out scores outside the training range are clipped to the map's ends.
- **S1, consistency (confidence):** the mean over the 16 contexts of the share of its 12 labels that equal the context's most frequent label. It reads no outcome and no answer. It rewards a teacher that always says the same thing: know-4, but also wrong-chain, echo and wrong-map, which score 1.0 by construction.
- **S2, peer agreement (consensus):**
  - For each context, take the plurality label over all other teachers in the same block; ties go to the lowest action index.
  - The score is the teacher's share of labels equal to that plurality, averaged over contexts.
  - This is the peer-prediction family's signal (M4's axis). In an honest-majority pool it comes close to the answer key, with all stages weighted equally.
- **N0, L's form-matched null:** L's whole procedure (features, penalty choice, out-of-fold scores, isotonic map, final fit), refitted with the training W permuted across training teachers, 1,000 times. It has L's form and inputs with the link to outcomes broken.
- **L, learned v(S):** ridge regression from 21 probe features to W.
  - Features: per stage, the share of probe labels naming each of the 5 actions (20 numbers), plus the share of labels equal to the executed action (1).
  - None of the features reads the right answers. Which label is right at a stage, and how much each stage is worth, can only come from the training W.
  - Features are standardized on the training block.
  - The penalty is chosen from 13 values (10^-3 to 10^3 in half-decade steps) by leave-one-group-out cross-validation over the 8 training groups, so a fold never splits a student.
  - The out-of-fold predictions are L's training scores for its isotonic map. The final model is fit on all 192 training teachers.
- **References, reported but not competitors:**
  - **A, audition:** W measured on the group's one audition student, which is a single test lesson on a separate calibration student. It is used raw: unbiased, no map.
  - **K, answer key:** the share of probe labels naming the right action. It reads T, so no estimator without the answers has it.

**Students and seeds.**
- **Already used, so avoided** (from the evidence files where a seed field is logged, and from the code where it is not):
  - EXP-49: 1_000_000 to 3_006_115 (1_000_000 x (market + 1) + 1000 x teacher + 10 x student, and + 5); its teacher brains use 100_000 x (market + 1) + n.
  - EXP-52: 3_000_000 to 3_006_115, 6_000_000 to 6_006_115 and 9_000_000 to 9_006_115 (3_000_000 x (block + 1) + 1000 x teacher + 10 x student, and + 5).
  - EXP-53, 54, 55, 58 and 61: 5_000_000 + 1000 x lesson + student (lessons 40 to 120).
  - The EXP-62 family:

    | run | full | pilot or sweep |
    |---|---|---|
    | EXP-62 | 6_200_000 to 6_200_071 | 6_330_000 to 6_410_002 |
    | EXP-62c | 6_400_000 to 6_400_071 | none |
    | EXP-62d | 6_600_000 to 6_600_071 | none |
    | EXP-62e | 6_800_000 to 6_800_215 | none |
    | EXP-62b | 7_000_000 to 7_000_047 | 7_090_000 to 7_090_002 |
    | EXP-62f | none | 7_190_000 to 7_190_002 |
    | EXP-62g | 7_200_000 to 7_200_047 | sweep 7_280_000 to 7_280_005; pilot 7_290_000 to 7_290_002 |
    | EXP-62h | 7_400_000 to 7_400_719 | 7_490_000 to 7_490_023 |
    | EXP-62i | 7_500_000 to 7_500_719 | 7_590_000 to 7_590_023 |

  - EXP-73: 8_200_000 to 8_200_215.
  - EXP-77: 8_400_000 to 8_400_215; pilot 8_470_000 to 8_470_005.
  - EXP-77b: 9_000_000 to 9_000_215; pilot 9_070_000 to 9_070_005; audit label draws 77_000_001 to 77_000_003.
  - Others: EXP-05 uses 9_005_000 and 9_005_200; seeds under 100_000 appear throughout EXP-01 to EXP-76 and the V0.5B runners; 123_456_789 appears in the tests.
  - Each student seed S also seeds label streams at S + 1 and S + 2.

  **CAL-1 uses nothing below 10_000_000.**
- **CAL-1 seeds:**
  - Student seeds are spaced by 10, so a zero arm's label seeds (S + 1, S + 2) never equal another student's seed. In the EXP-62 family they do: student k's random-label stream is student k + 1's world stream.
    - Training: 10_100_000 + 10s (s = 0 to 23).
    - Held-out: 10_200_000 + 10s (s = 0 to 47, or 0 to 63).
    - Audition: 10_300_000 + 10g (g = 0 to 7).
    - Pilot: 10_900_000 + 10s (s = 0 to 3).
  - Teacher identities: training 11_000_000 + t (t = 0 to 191), held-out 11_100_000 + t, probe-only identities 11_200_000 + t, pilot 11_900_000 + t.
  - Lesson label noise: 20_000_000 + 1000 x id + j. Here id is the global teacher id (training 0 to 191, held-out 200 to 391, pilot 500 to 523) and j is the student's index in its block (audition students use j = 900 + g).
  - Probe noise: 30_000_000 + id (probe-only identities use 30_000_700 + t).
  - Analysis: permutations use seed 1, bootstraps seed 0.
  - The script sets every seed explicitly. It does not inherit the EXP-62 family's pilot offset: under TAG=pilot that harness adds 1000 x lesson to the seed, which is why EXP-77's and EXP-77b's pilots actually ran on 8_470_000+ and 9_070_000+.

**Metrics** (on the 192 held-out teachers).
- **Rank:** Spearman rho(score, W).
- **Proper score:** the mean squared error (MSE) of the worth forecast against W. Squared error is a proper scoring rule for a forecast of the mean. Skill = 1 minus MSE / MSE of climatology, where climatology forecasts the training block's mean W for every teacher.
- **Noise:** a paired bootstrap over held-out teachers, stratified by group: 2,000 resamples, seed 0, with the maps and fitted models held fixed. Intervals are 95% percentile intervals on the differences.
- **Fake overpricing, per class:** the mean over the class's 16 held-out instances of (forecast minus W), with SE = the SD over instances / 4.
- **Noise ceiling:** split-half reliability of W: students 0 to 2 against 3 to 5 of each group, Spearman between the halves, Spearman-Brown corrected. No predictor can do much better than its square root.
- **Reported only:**
  - the hindsight MSE (an isotonic map fitted on the held-out block itself) and the out-of-sample to hindsight ratio;
  - the Brier score for B = [W >= 1/32] under the same isotonic procedure (C1's binary form);
  - each class's mean forecast and mean W;
  - L's per-stage weights;
  - rho on the graded teachers alone and on the know-k teachers alone.

**Pilot rule.**
- **Size:** one group of 24 held-out-style teachers (10 graded, know-1 to 4, and 2 each of random, wrong-chain, echo, anti-echo and wrong-map) x 4 pilot students, plus the zero twins: 108 twins, about 3 minutes. Pilot data never enters the verdict.
- **Chain print (RUN GATE line 5), per class:** class and p, then probe signals (S1, S2 within the pilot pool, K), then W per student and mean, then the between-teacher and within-teacher (student) variance.
- **PILOT STOP** (no full run; recorded) if any of these holds:
  - P1: know-4's W is below .10.
  - P2: the SD of the 24 teachers' mean W is below .05 (nothing to predict).
  - P3: the projected reliability v_b / (v_b + v_w / m), from a one-way variance split of the pilot W, is below .7 at m = 8.
- **Students per held-out teacher:** m = 6 if the projected reliability is at least .7 at m = 6; otherwise m = 8 (64 held-out students, about 11 more minutes). Nothing else may change after the pilot.

**Prediction.** These are planning numbers, not results.
- Reliability of W: about .8.
- rho:
  - L: .75 to .85.
  - S2 and K: .6 to .75, within about .03 of each other.
  - S1: near 0 (between -.2 and +.3). Three confident fake classes sit at the bottom of worth while scoring top on consistency.
  - A: .5 to .65, because one student is noisy.
  - N0's 99th percentile: about .2.
- **Where L's edge over S2 should come from: stage weights.** In EXP-77b's data (see Prior knowledge), knowing stage 0 is worth about +.23, stage 1 +.10, stage 2 +.07 and stage 3 +.01. An equal-weight count of known stages ranks the know-k twins at Spearman .56, against .67 for the stage-weighted fit (in sample). S2 and K weight stages equally.
- **Fakes:** the four trained classes are forecast within a few hundredths of their W. wrong-map is forecast near wrong-chain and echo, because in L it is "right at no stage" that predicts low worth, whatever wrong label is given.
- **Expected verdict** (a judgment, not resampled): CONFIRM about 60%; BOUNDARY on criterion 2 or 3 against S2 about 30%; anything else about 10%.
- **Reported items:**
  - the probe-gamer is overpriced by about know-4's worth (+.3 to +.4), by construction;
  - S2 on the coordinated pool loses most of its rank, with wrong-chain moving to the top;
  - L's forecasts order know-1 < know-2 < know-3 < know-4;
  - L beats K on rank.

**Decision rules.**
- **VOID, checked before any run:**
  - V1: the construction audit (`exp/EXP-77b_construction_audit.py`, unchanged; it audits the EXP-62 labeller entry point that CAL-1's zero arms call) does not print ADMITTED BY CONSTRUCTION, or CAL-1's zero arms do not call that entry point (a one-line `inspect` check).
  - V2, identity gate: CAL-1's twin, run on EXP-77b student 0 (seed 9_000_000, EXP-62's labeller seeds), does not reproduce the actions and labels of the null, untaught, random, know-4, wrong-chain, echo and anti-echo arms in `exp/EXP-77b-full.jsonl`. know-1 to 3 differ by design: their known stages now come from the identity seed.
- **VOID, checked after the run:**
  - V3: the split-half reliability of held-out W is below .5 (the target is too noisy to grade any predictor).
  - V4: the held-out know-4 class's mean W is below .10 (the instrument did not price skill on these students).
- **CONFIRM** if all of these hold:
  1. rho_L >= .5.
  2. L beats S1 and S2 on rank: rho_L minus rho_S has its 95% interval above 0, for each.
  3. L beats S1 and S2 on the proper score: MSE_L minus MSE_S has its 95% interval below 0, for each.
  4. L beats its form-matched null: rho_L is above the 99th percentile, and MSE_L below the 1st percentile, of N0's 1,000 refits.
  5. Calibration holds out of sample: L's skill against climatology has its 95% interval above 0.
  6. No fake class is overpriced: for each of random, wrong-chain, echo, anti-echo and wrong-map, mean(forecast_L minus W) + 1.645 SE < 1/16 (one state of the 16 read).
     - Why one state and not EXP-62e's half state: a class mean of 16 instances carries about .015 SE of realized-worth noise at m = 6.
     - Under that noise, half a state would false-fail a perfectly calibrated forecaster about a quarter of the time per class; one state false-fails it under 1% per class.

  Then: on this instrument, a v(S) trained on earlier teachers' realized transfer forecasts new teachers' worth from their probe labels better than confidence and consensus do, out of sample. It also pays no fake class, including one outside its training, more than one state above what that class delivers. What that would make possible: routing students to teachers before any student is spent, with realized transfer kept as the grade of the forecaster. That is the shape Noesis's calibration measure asks for.
- **KILL** if either holds:
  - K1: any fake class's mean L-forecast is >= the know-2 class's mean L-forecast. The learned price would pay a fake like a two-stage teacher.
  - K2: S1 or S2 beats L on both metrics, with both intervals excluding 0 (reversed, in C1's terms).
- **BOUNDARY:** anything else, with the failing criteria named. Two readings are fixed now:
  - Failing 2 or 3 against S2 only means: in an honest-majority pool, consensus prices as well as learning from outcomes, and the learned edge is not shown.
  - Failing 6 on wrong-map only means: the learned v(S) prices the fakes it was trained on and misprices a new one.
- **Reported, not decisive** (readings fixed now):
  - **A and K against L.**
    - If MSE_L <= MSE_A, L forecasts as well as one audition student per teacher, at no student cost.
    - If rho_L > rho_K, L knows more than the answer key: which stages are worth teaching.
  - **S2, coordinated:** S2 recomputed with 64 probe-only wrong-chain clones added to the reference pool. The clones cost nothing, because wrong-chain is deterministic. The clones then hold the plurality at every context. L does not read the pool, so it is unchanged by construction. This is M4's point, made on the teacher market.
  - **Probe-gamer:** 16 synthetic teachers, each pairing a probe-only know-4 identity's probe labels with a held-out random-class instance's measured W. Analysis only, no compute. The expected result is a large overpricing, by construction. No ex-ante estimator can see a teacher that behaves one way when probed and another way when teaching; only the realized grade catches it.
  - **L-archive:** L's procedure fitted on EXP-77b's logged lessons and applied to the held-out probes.
    - Training data: 216 students x 8 teacher arms, one student per row.
    - Features come from each lesson's label stream, not from probes; the domain shift from lessons to probes is disclosed.
    - It tests a v(S) trained on a genuinely earlier run.
  - **Other reported analyses:**
    - the hindsight ratio and the Brier score for [W >= 1/32];
    - the per-class table for every predictor and L's per-stage weights;
    - L refitted on 1, 3 or 6 probe labels per context;
    - a student-level bootstrap of W.

**Prior knowledge (flagged).**
- **EXP-77b's full-run data was read for planning.** `exp/EXP-77b-full.jsonl` (216 students, 0.89.0) was on disk. Its official write-up is another agent's and governs. What was read:
  - 60.3 s per 10-twin student per worker (range 53 to 75);
  - per-student SD of worth: .14 to .19 for know-k, about .08 for the random-label arms;
  - labels per lesson: 148 (know-4) to 226 (wrong-chain);
  - share of know-4's labels at stages 0 to 3: about 30 / 37 / 28 / 5%.
- **The drafter's own computations on that data** (Z = mean of null, untaught and random):
  - Per-arm worth: know-1 to 4 +.075 / +.157 / +.249 / +.385; anti-echo +.015; wrong-chain -.099; echo -.155.
  - Per-stage worth, from OLS over 864 know-k twins (known sets rebuilt from each student's label seed and checked against the logged labels): stage 0 +.226, stage 1 +.103, stage 2 +.073, stage 3 +.011 (SE about .011).
  - Spearman of worth against the number of known stages: .56, against .67 for the fitted stage weights, in sample.
  - The prediction that L beats S2 rests on these stage weights, which were seen before it was written.
- **Earlier results:**
  - EXP-62e: anti-echo's labels name the right action .25 of the time against .20 for random labels, and it is priced at about 38% of know-1's edge.
  - C1: the plain count beat Noesis's propagation rule on crates.io.
  - EXP-32/34: a learned partner chooser matched random; the program hard-wired neediest-first instead. This is a standing caution that a learned rule can lose to a fixed one.
  - EXP-36: a sandbagger that fools the probe bounds what probe-based defences can do.
- **Not known:** anything about probes, graded teachers, wrong-map, S1, S2, L, or any CAL-1 seed.

**Cost.**
- **Measured rate on 0.89.0:** EXP-77b ran 2,160 twins in 3,284 s at 4 workers, about 1.52 s of wall time per twin.
- **Full run:**
  - At m = 6: 2,160 twins (training 648, held-out 1,296, audition 216), about 55 min.
  - At m = 8: 2,592 twins, about 66 min.
- **Overheads:**
  - the audit: seconds;
  - the identity gate: about 100 s;
  - the pilot: 108 twins, about 3 to 4 min;
  - the analysis (1,000 refits and 2,000 bootstraps): a few minutes.
- **Total:** about 60 to 75 minutes at 4 workers on this PC (Ryzen 5 1600, 16 GB), run detached. Memory use is as in EXP-77b (one brain per worker at a time). Probes cost nothing.

**What CAL-1 cannot show.**
1. **Strategic teachers.** Every fake is a fixed rule that labels the same way on the probe as in a lesson. Four of the five fake classes are in training, so pricing them right is interpolation. Only one novel class (wrong-map) tests generalization, and it lies in the same feature span. A teacher that games the probe defeats any ex-ante estimator by construction; the probe-gamer line shows how badly. The forecast is not a price. The price stays the realized transfer, and calibration is how the forecaster is graded.
2. **The anchor moves; it does not go away.** L learns the answer key and the stage weights from realized transfer on the same task T. M5's outside ingredients (T, I and N) are all still assumed, plus a fourth: earlier realized transfer on the same task.
3. **No time.** "Held-out" means new teacher instances on fresh students from the same distribution, not a later period. Nothing drifts between training and grading, whereas C1 had a real time split.
4. **Narrow scope.** One instrument, one chamber, one lesson length, one task, and synthetic skill (per-stage reliability). Learning teachers (EXP-19/20) and teachers whose students go on to teach (CAL-2) are not included.
5. **Not M3 and not M2.** CAL-1 does not test isomorphism invariance (M3), and it does not test interior-feature matching in the wash_sim sense (M2). The probe features read no answers, but they are the teacher's own outputs on the task's contexts, not graph statistics.
6. **Students are a fixed draw** in the primary bootstrap, which resamples teachers only. Student-level resampling is reported, not decisive.
7. **S2 is plurality agreement,** not an incentive-compatible peer-prediction mechanism.
8. **Honest world.** Nobody is paid, so nobody adapts to the estimator.

**Where CAL-1 sits in the program.** Off-ladder: no milestone moves on any verdict, and CAL-1 presupposes M1b on this version (precondition 2). It is the program's first test of THE PROBLEM's second irreducible piece: a learned v(S) on exogenous realized-use labels, here earlier teachers' realized student gain. It touches M4 (S2 and its coordinated variant) and M5 (it names a fourth outside ingredient) without crossing either. A CONFIRM would justify proposing a calibration rung (forecast before, graded after, against form-matched nulls); whether to add one is Will's call. CAL-2 (multi-generation) would build on it.

**What would change in the harness (sketch only; no script is written).** The student side reuses EXP-62's `twin()`, `live_world`, the greedy read and the zero arms unchanged. Jobs are single twins (block, student, teacher), run through EXP-73's pool and checkpoint loop. Each row logs the identity, the probe labels, the lesson's label stream, the actions and the accuracy. The analysis is a separate script on the saved rows; sklearn's `Ridge` and `IsotonicRegression` (sklearn 1.9.0 is installed) or about 20 lines of numpy. The new pieces:

```python
def make_teacher(kind, ident_seed):            # identity drawn once; kept on every student and on the probe
    r = np.random.default_rng(ident_seed)
    p = m = None                                # p and m are indexed by the right action, which is the stage (RIGHTS = [0, 1, 2, 3])
    if kind.startswith("know-"):
        known = set(r.choice(4, size=int(kind[5:]), replace=False).tolist())
        p = [float(i in known) for i in range(4)]
    elif kind == "graded":
        p = r.uniform(0.0, 1.0, 4).tolist()
    elif kind == "wrong-map":
        m = [int(r.choice([x for x in range(5) if x != i])) for i in range(4)]

    def labeller(noise):                        # noise = default_rng(lesson or probe seed)
        if p is not None:
            return lambda c, a: c.right() if noise.random() < p[c.right()] else int(noise.integers(5))
        if m is not None:
            return lambda c, a: m[c.right()]
        return E62.labeller(kind, noise)        # random, wrong-chain, echo, anti-echo: the existing code
    return labeller


class Stub:                                     # a probe context; the labeller reads only right() and the action
    def __init__(self, i): self.i = i
    def right(self): return RIGHTS[self.i]


def probe(lab, R=12):
    return [(i, a, int(lab(Stub(i), a))) for i in range(4) for a in range(5) if a != RIGHTS[i] for _ in range(R)]


def features(pr):                               # 21 numbers; none reads RIGHTS
    f, same = np.zeros((4, 5)), 0
    for i, a, t in pr:
        f[i, t] += 1
        same += t == a
    return np.r_[(f / f.sum(1, keepdims=True)).ravel(), same / len(pr)]
```

## Status (2026-10-27)
- 2026-11-13: GO. Will delegated the V(S) choice ("you decide the Vs program"); Jarvis chose CAL-1 over CAL-2 and the standalone zero test. Reasons: CAL-1 is the direct test of the success measure Noesis adopted (a forecast made before, graded against realized worth after) and of the open moat item (a learned v(S) on realized-use labels); CAL-2 needs a learned v(S) first, so it waits on a CAL-1 CONFIRM; the zero test's question is mostly inside CAL-1 already, since Z averages null, untaught and random. Amendments, written before any CAL-1 data: (a) exploratory only, report W and each criterion under each single zero (null, untaught, random) beside the composite Z; the verdict still uses Z. (b) Version: EXP-77b crossed on 0.89.0 and the installed library differs; the V2 identity gate is the version check. If V2 fails on the installed version, do not run: either pin CAL-1 to the 0.89.0 source or rerun EXP-77b on the installed version first, and record which. The experiment loop commits this file as the pre-registration before the pilot.
- DRAFT. Nothing has been run: no audit rerun, no gate, no pilot, no script. The file is to be committed only with Will's go. On commit, the date line becomes the pre-registration date, and nothing above changes afterwards.
- 2026-11-13 14:50: pre-registration committed `b70748c`: this file, unchanged except the 2026-11-13 Status line (the working copy's CRLF line endings were normalized to LF; the diff is that one line).
- V1, before the pilot: `exp/EXP-77b_construction_audit.py`, unchanged: ADMITTED BY CONSTRUCTION (action shares .1997 to .2006, hit rate .1995; `exp/CAL-1-audit.out`). Inspect check: CAL-1's zero arms call EXP-62's `twin`, whose `labeller` is the audited entry point: PASS (`exp/CAL-1-v1.out`).
- V2, the version check (amendment b): on the installed 0.94.0 (`4cb9c29`), CAL-1's twin on EXP-77b student 0 (seed 9_000_000, EXP-62's labeller seeds) reproduced the actions and labels of null, untaught, random (by the zero path and by the teacher path), know-4, wrong-chain, echo and anti-echo in `exp/EXP-77b-full.jsonl`: IDENTICAL (11 s, `exp/CAL-1-gate-4cb9c29.out`). CAL-1 therefore ran on the installed version; no 0.89.0 pin and no EXP-77b rerun were needed.
- Pilot (one group of 24 x 4 students, seeds 10_900_000+, 108 twins, 149 s): know-4 W +.427; SD of the 24 mean W .206; one-way split v_b .0367, v_w .0228; projected reliability .906 at m = 6, .928 at m = 8. No stop; m = 6 by the rule (`exp/CAL-1-pilot.log`, `.json`). The pilot's JSON dump failed on a numpy bool after the rule had printed; the cast was fixed and the report rerun from the checkpoint, no twin rerun (first log kept as `exp/CAL-1-pilot.run1.log`).
- Full run: 2,160 twins (training 648, held-out 1,296, audition 216), m = 6, 15:00:02 to 15:49:27, 2,965 s at 4 workers (1.37 s per twin), one pass, exit 0, stderr empty; the clone was still `4cb9c29` afterwards. Probes for all 464 instances were written to `exp/CAL-1-full-probes.json` before any twin ran; the probes logged in the rows equal that file (0 mismatches). Analysis at 15:52 (`exp/CAL-1-full-analysis.out`, `.json`).

## Summary
- Question: before a teacher teaches anyone, can a v(S) learned from earlier teachers' realized student gain forecast a new teacher's worth from its 192 probe labels better than consistency (S1) and peer agreement (S2), on held-out teachers and fresh students, without overpricing any fake class, including one absent from training?
- Setup: EXP-77b's student side through EXP-62's code (delayed-credit brain, founder lateral, weather chamber, corrective schedule, lesson 80, 20 attempts alone, 16 unseen states); composite zero Z = per-student mean of null, untaught and random. Teachers with a fixed identity: graded (per-stage reliability uniform on [0, 1]), know-1 to 4, random, wrong-chain, echo, anti-echo, and wrong-map (held-out only). 192 training teachers on 24 students (8 groups x 3), 192 held-out teachers on 48 students (8 x 6), 8 audition students, fully crossed within groups. L = ridge on 21 probe features, penalty by leave-one-group-out CV (100 chosen), isotonic map on its out-of-fold scores. Rivals S1 and S2; references K (answer key) and A (audition); N0 = L refitted on permuted training W, 1,000 times. Paired bootstrap, 2,000 resamples over held-out teachers stratified by group.
- Prediction (written before data): rho L .75 to .85, S2 and K .6 to .75, S1 between -.2 and +.3, A .5 to .65, N0's 99th percentile about .2, reliability about .8; trained fakes forecast within a few hundredths; wrong-map forecast near wrong-chain and echo; verdict CONFIRM about 60%, BOUNDARY on criterion 2 or 3 against S2 about 30%, anything else about 10%.
- Result (192 held-out teachers, composite Z):
  - Reliability of W .908 (split-half r .831, students 0-2 against 3-5); noise ceiling .953. know-4 W +.401. No VOID.
  - rho: L .928, S2 .907, K .907, A .763, S1 -.158. S2 equals K to floating-point precision for every teacher: in this pool the plurality label is the right action at every context.
  - MSE: L .00535, S2 .00687, A .02174, S1 .03167, climatology .03297. Skill of L .838 [.803, .871].
  - L minus S2: rho +.021 [+.001, +.045], MSE -.00152 [-.00268, -.00048]. L minus S1: rho +1.087 [+.890, +1.259], MSE -.0263 [-.0319, -.0211].
  - N0 (1,000 refits): rho 99th percentile .850 against L's .928; MSE 1st percentile .0235 against L's .00535.
  - Overpricing, mean(L forecast minus W) with the upper bound (+1.645 SE) against 1/16 = .0625: random +.012 (+.032), wrong-chain -.030 (-.019), echo -.039 (-.023), anti-echo -.011 (+.009), wrong-map +.098 (+.132). wrong-map: W -.183, forecast -.085.
  - No kill: the highest fake forecast (random, +.007) sits far below know-2's (+.233); neither S1 nor S2 beats L on either metric.
  - Criteria 1 to 5 pass. Criterion 6 passes for the four trained fakes and fails for wrong-map.
- Verdict: **BOUNDARY**, failing criterion 6 on wrong-map only. The pre-registered reading: the learned v(S) prices the fakes it was trained on and misprices a new one. Prediction vs outcome: not the expected CONFIRM; the outcome is in the "anything else, about 10%" bucket. Most planning numbers were beaten (rho for L, S2 and A all higher), S1 was in range, and N0's rank percentile was far above plan (.850 against about .2).
- Reported, not decisive (composite Z):
  - A and K: L beats A on MSE (.00535 against .02174; difference [-.0216, -.0115]), so it forecasts better than one audition student per teacher, at no student cost. L beats K on rank (+.021 [+.001, +.045]), so it knows something the answer key does not: its weight on naming the right action falls with the stage (.075, .057, .052, .024 per unit share at stages 0 to 3), the order of EXP-77b's per-stage worth.
  - Within classes: graded rho L .787 against S2 .689; know-k .912 against .769. L orders know-1 < know-2 < know-3 < know-4 (+.118, +.233, +.290, +.433).
  - S2 coordinated (64 free wrong-chain clones added to the pool): rho -.810, MSE .0907, wrong-chain on top (S2 1.000) and know-4 at 0. L does not read the pool.
  - Probe-gamer: forecast +.433 against W -.005, overpriced +.438 (SE .012), about know-4's worth, as constructed.
  - L-archive (L's procedure on EXP-77b's 1,728 lesson streams, 0.89.0, applied to the held-out probes): rho .930, MSE .00707, skill .786; wrong-map forecast -.118.
  - L on 1, 3, 6 or 12 probe labels per context: rho .894, .916, .932, .928; MSE .00831, .00643, .00528, .00535.
  - Hindsight ratio L 1.36, S2 1.25, S1 1.04. Brier for [W >= 1/32]: L .0565, S2 .0605, S1 .1509, A .1823, climatology .2389.
  - Student-level bootstrap: rho L [.846, .914]; L minus S2 rho [+.009, +.029], MSE [-.0024, -.0007].
- Exploratory per-zero report (amendment a; the verdict uses Z):
  - null: rho L .917, S2 .897; L minus S2 rho +.020 [+.002, +.043], MSE -.0014 [-.0027, -.0002]; criteria 1 to 5 pass; 6 fails on wrong-map (+.102, upper +.137). Reading: BOUNDARY, as under Z.
  - untaught: rho L .901, S2 .873; L minus S2 rho +.028 [+.009, +.051], MSE -.0019 [-.0031, -.0008]; 1 to 5 pass; 6 fails on wrong-map (+.106) and on random (+.035, upper +.065, just over .0625). Reading: BOUNDARY.
  - random: rho L .906, S2 .898; L minus S2 rho +.008 [-.018, +.035], MSE -.0006 [-.0025, +.0013], so criteria 2 and 3 against S2 fail; 6 fails on wrong-map (+.111). Reading: BOUNDARY.
  - know-4 W .391 / .393 / .421 and reliability .895 / .852 / .890 under null / untaught / random; no VOID and no kill under any zero.

## Reflection
- What it means: on this instrument a learned v(S) prices teachers before they teach. Trained on 192 earlier teachers' realized gain, it forecast 192 new teachers on 48 fresh students at rho .93 and 84% skill over climatology, near the noise ceiling (.95). It beat the outcome-free signals out of sample on both rank and proper score, beat its form-matched null, and paid none of the four trained fake classes more than they deliver. Its edge over consensus is real but small (MSE 22% below S2's, rho +.02), and it comes from where the draft said it would: stage weights. L learned that naming the right action at stage 0 is worth about three times as much as at stage 3, which S2 and K cannot see because they weight stages equally (within know-k, rho .91 against .77). The calibration rung is not met as registered, because of the one novel fake. wrong-map turned out more harmful than every trained class (W -.183 against wrong-chain -.082 and echo -.083). L forecast it near those classes (-.085), as the draft predicted, and so overpriced it by +.098, about 1.6 states. The forecast was still negative and in the bottom sixth of the 192 (mean rank 30.6), so a router would not have sent students to it. What failed is the price, not the rank.
- Why wrong-map failed (post hoc, not registered): (a) its extra harm tracks WAIT labels. Maps with no WAIT averaged W -.113 (n 3, about wrong-chain's level), one WAIT -.174 (n 11), two WAITs -.332 (n 2), and no trained class labels WAIT consistently. (b) The isotonic map, fitted on training and clipped at its ends as registered, cannot forecast below -.1215 (echo's training mean). 11 of the 16 wrong-map instances realized less than that, and a forecast pinned at that floor for all 16 would still overprice the class by +.061, with an upper bound above 1/16. In short: the forecaster cannot go below the worst worth it saw in training. wrong-map was worse than that, so this procedure could not pass criterion 6 for it. The registration did not foresee a new class worse than every trained fake. The pre-registered rules fix this run's verdict, so only a new registration can test the fix (CAL-1b under Next). The L-archive, trained on per-student rows with a wider range of W, forecast wrong-map at -.118 (overpriced +.065), which fits the range explanation.
- The N0 surprise (post hoc): N0's rank 99th percentile was .850, not the planned .2. The probe features' main axis already tracks worth (the first principal axis carries 25% of the variance and has |rho| .58 with W), so a ridge direction fitted to permuted W often ranks teachers well (median |rho| .45; 19% of refits above +.5). L still cleared it (.928), but rank is cheap in this market. The proper score is where L separates from its null (MSE .00535 against a 1st percentile of .0235). Calibration, not rank, is the discriminating grade here, which is the measure Noesis adopted.
- The S2 edge depends on the zero (exploratory): L beats S2 under Z, null and untaught, but not under the random zero alone (rho +.008 [-.018, +.035]). One zero arm is a single noisy twin per student, and by construction its noise enters every W measured on that student. Under the random zero, the held-out teachers also came out higher than training predicted (graded teachers forecast .054 below their realized W). That noise and shift are larger than L's small stage-weight edge. The composite zero averages three twins, and the verdict's comparison with S2 rests on it.
- What it does not show: strategic teachers (the probe-gamer is overpriced +.438 by construction; the forecast is not a price, and realized transfer stays the price); drift over time; another brain, chamber, lesson length or task; a peer-prediction mechanism (S2 is plurality agreement, equal to the answer key in this honest pool, and it collapses to rho -.81 under 64 free clones); M2 or M3.
- Process: V1, V2, pilot and full run went as registered: one pass, no restart, m fixed by the pilot rule, nothing changed after the pilot. It ran on 0.94.0 (`4cb9c29`), not 0.89.0, with V2 IDENTICAL on the eight arm paths, as amendment (b) requires. The analysis script was written before the full run and tested on synthetic rows (since deleted). It was committed `8f600ae` 84 s after the run started and before any full-run row was read; the two edits made at commit time changed print formats only. The pilot JSON bug was fixed with no rerun (Status). The draft left some details open. They were settled in code before any data, and are listed here:
  - Order within a group: graded first, then know-1 to 4, then the fakes in pairs.
  - Probe-only identities: t 0 to 15 are the probe-gamer's know-4s; t 16 to 79 are the wrong-chain clones.
  - S2's plurality counts every label of every other teacher at that context.
  - Ridge has an intercept; the penalty is the one with the lowest out-of-fold MSE.
  - Spearman uses tie-averaged ranks; class SEs use the sample SD (ddof 1).
  - The coordinated S2 is mapped with the map fitted on the honest training pool.
  - L-archive: a stage with no labels in a lesson gets shares of .2; folds are 8 blocks of 27 students; skill is against CAL-1's climatology.
  - A's Brier score uses its own indicator [A >= 1/32].
- Process, continued: the post hoc checks above (WAIT counts, the isotonic floor, N0's spread, S2 equal to K) were run in a scratch directory after the verdict and are not part of it.
- Lesson: a calibration map fitted on a training block cannot forecast outside that block's range. When a held-out class could be worse (or better) than every trained class, register either a map that extrapolates or a criterion that measures the class against the training floor, and check novel fakes for harms no trained class has (here, WAIT labels). Second: with a permutation null, check how cheap rank is in the feature space before planning on it, and grade on the proper score.
- Next: CAL-2 keeps waiting; it waits on a CAL-1 CONFIRM. Candidate CAL-1b (Will-gated, not run): CAL-1's design with one trained fake that labels WAIT consistently, a novel fake inside the trained range, and a pre-registered treatment of forecasts below the training floor. Whether a calibration rung belongs on the ladder stays Will's call. This result says the learned v(S) interpolates well and does not extrapolate harm.
