# CAL-1: calibration-graded v(S) in the teacher market

> **DRAFT for Will's approval; not pre-registered until committed with his go.**

- Date: drafted 2026-10-27 (no CAL-1 data exists) | Cadence version: 0.89.0 (`81345d8`), the instrument EXP-77b grades | Program iter: none yet (candidate named in VS-TRANSFER-PROGRAM.md, NEXT ITERATIONS, 2026-10-27 update)
- Script: `exp/CAL-1_calibration_vs.py` (not written) | Evidence: `exp/CAL-1-*` (none yet)

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
- DRAFT. Nothing has been run: no audit rerun, no gate, no pilot, no script. The file is to be committed only with Will's go. On commit, the date line becomes the pre-registration date, and nothing above changes afterwards.

## Summary
- PENDING (to be written after the run)

## Reflection
- PENDING (to be written after the run)
