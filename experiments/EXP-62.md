# EXP-62: does transfer price skill on a brain that takes in content, against a committed null?

- Date: 2026-10-17 | Cadence version: 0.83.0 + Unreleased, main `6499e56` (`~/_cadence_study`) | Program iter: iter36
- Script: `exp/EXP-62_content_market_committed_null.py` | Evidence: `exp/EXP-62-pilot.*`, `exp/EXP-62-full.*` (outputs, json, jsonl)

## Pre-registration (written 2026-10-17 before the pilot; nothing below this section existed when it was written)

**Question.** On the one brain known to take in teacher content (EXP-58's delayed-credit operating point), priced against a fixed, committed counterfactual, does measured transfer order genuine teachers by skill and price every task-blind fake at or below zero?

**Why.** This is the one untested combination. EXP-49 used the default brain against an untaught twin and was fooled (a random fake earned +.179). EXP-52 used the default brain against a form-matched null and was blind (know-4 +.013, Spearman .06). EXP-58 and EXP-61 showed content reaches only the delayed-credit brain (+.469 at 120 attempts vs +.016).

**Setup.**
- Instrument I: EXP-58's `compose` (10 inputs, 5 actions, modules (32,), EXP-45 actor/critic settings, working memory as in EXP-58). The alone phase is 20 attempts through `step` with no labels, as in EXP-58.
- Chamber and schedule: EXP-48's weather chamber, lessons under SEEN weather. Labels are given only after an executed mistake in V5's guided window (EXP-49 `live_world`). Worth is read as per-state greedy accuracy under UNSEEN weather after the alone phase.
- Shared students (change a): every arm for a student uses the same student seed and the same world draws. The null and untaught twins are built once per student, not once per teacher. Labeller seeds: teachers use student_seed+1, the null uses student_seed+2 (EXP-52 convention), so the random teacher and the null are different draws.
- Arms (10 twins per student): null (random-label teacher, the form-matched null), untaught (= abstain), know-1, know-2, know-3, know-4 (EXP-52 labeller: right action at k known stages, uniform random elsewhere), random, wrong-chain, echo, anti-echo (uniform among the 4 actions other than the executed mistake).
- Counterfactual (change b): pooled over all students, whichever of {null, untaught} has the higher mean accuracy is the committed counterfactual CF. Worth = taught - CF on the same student. This is a fixed rule chosen once from pooled means, not a per-student max. Both counterfactuals are reported.
- Pay (change d): per teacher, students in fixed batches of 6 (by student index). A batch finalizes iff its mean worth > 0 and mean / SEM > 2. Pay for a finalized batch = its mean worth; otherwise 0. Fake pay share = pay to {random, wrong-chain, echo, anti-echo, abstain} / total pay.
- Logging (change e): every twin's 16 per-state greedy actions on UNSEEN weather, and every teacher's label stream (right action, executed action, label) are saved.
- Full run: 72 students (n = 288 know-k twins), 4 workers, fresh seeds 6_200_000 + student. Pilot seeds are disjoint (6_290_000 + 1000*L + student).

**Window (change c), pilot under the exact run conditions:** 3 students, lesson lengths 40 / 80 / 120, arms null, untaught, know-1..4, random. Choice rule fixed now: pick the length with the largest pooled (know-4 - know-1) among lengths where know-4 mean <= .90; ties go to the shorter length. If no length qualifies, pick 80. The pilot also prints each chain link per arm: label-correctness rate, taught accuracy, counterfactual accuracy, worth.

**Prediction.** From EXP-58: random labels sit slightly below untaught on this brain (-.016 at 40, -.078 at 120), so CF will be the untaught twin. Know-4 minus untaught was .177 at 40 and .391 at 120 (near ceiling at .93), so the pilot should pick 80. At the chosen length:
- know-1 < know-2 < know-3 < know-4, Spearman(worth, k) about .4 to .5;
- know-4 worth about +.25 to +.35;
- random about -.02 to -.06; wrong-chain and echo clearly negative; abstain exactly 0 (CF = untaught);
- anti-echo about -.02 against CF (not > 0 by 2 SEM), about +.03 against the null;
- fake pay share well under .10.
Predicted verdict: CONFIRM. Biggest risk: adjacent know-k means (know-1 vs know-2) out of order through noise at n = 72.

**Decision rules (from VS-TRANSFER-PROGRAM.md NEXT ITERATIONS item 1, unchanged):**
- CONFIRM if all hold: means ordered know-1 < know-2 < know-3 < know-4 and pooled Spearman(worth, k) >= .3 (n >= 288); know-4 >= .2 against CF; every task-blind fake (abstain included) has mean <= 0; fakes take <= .10 of pay. Then transfer prices skill on an instrument that takes in content, with I and N named.
- KILL (angle refuted under its best conditions): any task-blind fake's mean worth >= know-2's mean worth (point estimates, n = 72 each).
- DECISIVE FOR NOESIS WITHOUT KILLING: content large but Spearman < .1 means transfer is a pass/fail filter, not a price. Anti-echo > 0 against CF by 2 SEM means the zero point must be the best fake in a declared committed class, because the corrective schedule leaks one elimination bit per mistake.
- Anything else: BOUNDARY, with the failing criterion named.

## Pilot and window decision (2026-10-17, before the full run)

Pilot (`exp/EXP-62-pilot.*`, 3 students per length, 132 s). Chain links per arm, pooled over lengths: label-correctness
rises with k as designed (know-1 .30-.34, know-2 .45-.63, know-3 .76-.84, know-4 1.00, random .18-.19). The committed
CF is the untaught twin at every length (untaught .479 / .583 / .542 vs null .438 / .438 / .458 at 40 / 80 / 120), as
predicted. Know-4 mean accuracy .667 / .917 / .708; know-4 minus know-1 .125 / (.917 - .458) / .062.

Window rule as registered: 80 is excluded (know-4 .917 > .90), so the rule picks **40** (largest know-4 - know-1 among
qualifying lengths). This departs from the prediction (which expected 80); the rule governs.

**Amendment A1 (written before the full run):** the primary run is lesson 40, and only lesson 40 decides the verdict.
Because the ceiling guard was judged on 3 students and the prediction expected 80, lesson 80 is also run on the same 72
students as an EXPLORATORY secondary. Its result is reported but cannot change the verdict. Known risk at 40: EXP-58 had
know-4 - untaught = .177 there, under the .2 bar, so BOUNDARY on the know-4 criterion is a live outcome.

## Summary
- Question: on the one brain known to take in teacher content (EXP-58's delayed-credit operating point), priced against a committed counterfactual, does measured transfer order genuine teachers by skill and price every task-blind fake at or below zero?
- Setup: EXP-48's weather chamber, corrective schedule (labels only after executed mistakes), 20 attempts alone through `step`, per-state greedy accuracy on unseen weather. 72 shared students, 10 twins each (null, untaught = abstain, know-1..4, random, wrong-chain, echo, anti-echo). Lesson 40 is primary (picked by the registered window rule); lesson 80 exploratory (amendment A1). Full run 1,997 s, 144 student jobs.
- Prediction: CONFIRM, with the untaught twin as CF and the pilot picking 80. Both side predictions missed: the rule picked 40, and the null (random labels) beat untaught on pooled accuracy, so CF = null at both lengths (40: null .409 vs untaught .393; 80: .455 vs .425).
- Result (lesson 40, decides): worth vs CF know-1 +.054, know-2 +.068, know-3 +.138, know-4 +.236 (SEMs .018-.021), ordered; Spearman(worth, k) .400 (n = 288); random -.028, wrong-chain -.054, echo -.075, abstain -.016, anti-echo +.023 (SEM .019, 1.2 SEM); fakes take .041 of pay, all of it anti-echo. Criteria: ordered yes, Spearman yes, know-4 >= .2 yes, every task-blind fake <= 0 NO (anti-echo), fake pay <= .10 yes; no kill (no fake near know-2); anti-echo > 0 by 2 SEM no.
- Exploratory (lesson 80, same students): know-1..4 +.059 / +.121 / +.234 / +.391, Spearman .530, random -.050, wrong-chain -.091, echo -.132, abstain -.030, anti-echo +.031 (1.6 SEM), fake pay .042. Same criterion fails.
- Exploratory re-read (saved data, no new runs): across the 8 labelling arms, mean worth tracks the fraction of labels that are right almost perfectly (r = .991 at 40, .994 at 80; 8 arm means, descriptive). Anti-echo's labels are right .25 of the time vs random's .19-.20, because the schedule tells the labeller which action was just wrong; its worth sits where that much information predicts. Priced against anti-echo as the zero, the ladder still holds: know-1 +.030 (SEM .018) to know-4 +.213 (40); +.028 to +.359 (80).
- Verdict: BOUNDARY (4 of 5 CONFIRM criteria; the failing one is the zero point: a task-blind labeller that uses the schedule's elimination bit prices slightly above the random-label null, not significantly at 2 SEM).

## Reflection
- What it means: for the first time in this program, transfer prices skill on a brain that takes in content, against a committed null: the know-k ladder is ordered, Spearman is .40 (.53 at 80), know-4 clears .2, and wrong-chain, echo, random and abstain all price below zero, with fakes taking 4% of pay. The one failure is informative rather than a fooling: worth follows label information almost one-for-one across every arm, and the corrective schedule hands any labeller one elimination bit per mistake. So the measure is pricing information correctly, including information the protocol leaks. The zero point therefore has to be the best fake in a declared class (here: a labeller that sees only the executed mistake, of which anti-echo is the best possible), not uniform noise. That is the pre-registered "decisive for Noesis" reading in substance, though its formal 2-SEM trigger did not fire.
- Process: the registered window rule overrode the prediction (its .90 ceiling guard excluded 80 on 3 pilot students, know-4 .917); 80 ran as a declared exploratory arm so the verdict did not depend on the choice. The counterfactual flipped vs prediction (null above untaught, unlike EXP-58 at the same length), which the fixed pooled rule handled without a per-student max. Cadence printed "finite teaching free phase used its entire free_steps budget" warnings on this brain (8 lines in the stderr log); EXP-58 ran the same composition; not investigated. The label-information correlation and the anti-echo re-pricing are post hoc and labelled exploratory.
- Lesson: a "task-blind" fake is only blind relative to what the protocol tells it. Before declaring the zero point, enumerate the information the schedule itself leaks to a labeller (here, which action just failed) and price against the best labeller that uses only that.
- Next: EXP-62c, pre-registered on fresh seeds with the committed zero = the best fake in the declared class (anti-echo), same CONFIRM criteria; then EXP-62b (instrument dependence) on this harness.
