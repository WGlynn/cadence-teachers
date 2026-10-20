# EXP-62i: is the delayed-credit brain's low price for late knowledge a matter of exposure?

- Date: pre-registered 2026-10-20 (Will's go 2026-10-20 14:43), before any EXP-62i data | Cadence version: 0.84.3 source at upstream main `c7dc2f0` (`~/_cadence_study`, fast-forwarded after EXP-62h; record at run time) | Program iter: iter43
- Script: `exp/EXP-62i_exposure.py` (EXP-62h's harness at budget 6 and lesson 80; instruments A and D1; a stage-3 scaffold) | Evidence: `exp/EXP-62i-check.out`, `exp/EXP-62i-pilot.*`, `exp/EXP-62i-full.*`

## Pre-registration (written 2026-10-20, before any EXP-62i data)

**In one line: if the delayed-credit brain gets to the late stages as often as the cross-family brain does, does it value a late-only teacher the way that brain does?**

**Why.** EXP-62h found that a teacher who knows only the late stages is worth almost nothing to the delayed-credit brain A (late/early worth ratio .044) but about a third of an early-stage teacher to the cross-family brain D1 (.326). Its reflection offered a mechanism, untested. A late-only teacher can only label a student who reaches stage 3. D1 gets further on its own (untaught .643 against A's .341), so it hears more late labels (7.8 per student against 5.7). If that is the whole story, the "exchange rate" is mostly exposure, not valuation. This test equalizes how far the students get and asks whether A's ratio rises toward D1's.

**The scaffold.** The lesson has 80 attempts of up to 6 decisions. Under the scaffold, every other attempt (attempts 1, 3, 5 ... 79, counting from 0) starts at stage 3. Wood and stone are already done there, so the next right actions are fire, then warm. Nothing else changes. The weather draws, the guided/autonomous schedule, the labellers and the budget are as in EXP-62h. The 20 attempts alone after the lesson are never scaffolded. Accuracy is read as in EXP-62h: the greedy action at all four stages, under the four unseen weathers. The scaffold draws no random numbers, so both conditions see the same weather sequence and the comparison is paired.

**Setup.** EXP-62h's harness, teachers and readings: know-early-2, know-late-2, know-4, null (random labels, the zero), untaught. Two instruments: A (EXP-58's delayed-credit brain) and D1 (EXP-62g's cross-family brain). C is dropped: in EXP-62h it did not differ from A (A-C +.064, interval -.025 to +.153), and dropping it saves a third of the cost. Two conditions per instrument: off (EXP-62h exactly) and on (the scaffold). Every instrument and condition sees the same student seeds and label seeds. Fresh seeds: pilot 7_590_000 + student, full 7_500_000 + student; no script in `exp/` uses either range (checked by grep).

**Primary quantity.** R(I, c) = mean(late worth) / mean(early worth) for instrument I in condition c, with worth = accuracy minus the null arm's accuracy, per student (EXP-62h's late/early ratio). The share of the A-D1 gap that the scaffold closes for A:

phi_A = (R(A, on) - R(A, off)) / (R(D1, off) - R(A, off)),

with a 95% interval from a paired bootstrap over students (10,000 draws, seed 62).

**Check (TAG=check, before the pilot; a failure stops everything).** (a) Identity: with the scaffold off, the script's twin reproduces `E62.twin` exactly (accuracy and label stream) for one student per instrument, and it reproduces EXP-62h's stored accuracies for EXP-62h student 0 on every arm. If the stored 62h accuracies are not reproduced at `c7dc2f0` (the source moved since 62h), that is recorded; the off condition stays a valid within-experiment control, but no number from EXP-62h is compared to EXP-62i's. (b) The scaffold: with it on, exactly 40 of the 80 lesson attempts start at stage 3 (the first right action is fire), and none of the 20 attempts alone does. The check prints no accuracy under the scaffold.

**Pilot, which sets N.** 24 students, both instruments, both conditions. Stop rules, checked first: any instrument-condition with mean untaught accuracy .90 or more (ceiling), or with know-4 worth below .10 or below 2 SEM (it does not take in content), stops the run. Exposure check: under the know-late-2 teacher, A with the scaffold must hear at least as many late labels per student as D1 without it. If it does not, the scaffold rises to 3 of every 4 attempts (every attempt whose number is not a multiple of 4), and the pilot is rerun once on the same pilot seeds. If the check still fails, the run stops. Then N = 24 x (SE / .10)^2, rounded up to a multiple of 24 and held between 96 and 720, where SE is a robust estimate of phi_A's bootstrap spread in the pilot, half the width of its central 68% interval (a ratio of differences can have heavy tails at n 24, which would inflate a standard deviation). At the cap of 720 the run takes about 5 hours at 4 workers. Pilot students are not reused, and the pilot's phi is not reported.

**Decision rules (written before any data).**
- MOSTLY EXPOSURE: phi_A's 95% interval lies above .5 (equal exposure closes more than half of the gap).
- NOT MOSTLY EXPOSURE: phi_A's 95% interval lies below .5.
- Otherwise: INCONCLUSIVE.
- Reported with every verdict: phi_A and its interval; R for each instrument and condition with intervals; A's rise R(A, on) - R(A, off) with its interval (SOME EXPOSURE if it excludes 0); the parts of A's rise, late worth and early worth each by condition (the scaffold also halves early-stage practice, so a rising ratio can come from late worth rising or early worth falling, and the two mean different things); D1's own change under the scaffold; late and early label counts; untaught and know-4 per condition; EXP-62h's scaled rate s per instrument and condition.
- Loop verdict: MOSTLY EXPOSURE -> REFUTED for "the brain sets the rate" (EXP-62h's reading becomes "the exposure sets the rate"); NOT MOSTLY EXPOSURE -> CONFIRMED (the rate is the brain's valuation, not its exposure); INCONCLUSIVE -> INCONCLUSIVE.

**Predictions (written before any data).**
- A's ratio rises under the scaffold (A's rise excludes 0): about 70%.
- MOSTLY EXPOSURE about 40%, NOT MOSTLY EXPOSURE about 35%, INCONCLUSIVE about 25%.
- Most of A's rise comes from late worth rising rather than early worth falling: about 60%.
- D1's ratio also rises under the scaffold: about 60%.
- The pilot sets N at the 720 cap: about 70%.

**Known limits.** The scaffold changes more than exposure. Scaffolded attempts succeed more often, so every arm, including untaught and null, gets more late-stage practice of its own; and half the attempts skip the early stages, so early practice falls. The decomposition (late worth and early worth by condition) is reported so that the reading does not rest on the ratio alone. Two instruments only; one task (budget 6, lesson 80).

## Check
- 2026-10-20, `exp/EXP-62i-check.out` / `.json`, Cadence 0.84.3 source at `c7dc2f0`: **PASS.** (a) With the scaffold off, the script's twin equals `E62.twin` (accuracy, label stream and greedy actions) for A and D1, and it reproduces EXP-62h's stored accuracies for EXP-62h student 0 on all five arms for both instruments, so the source move since EXP-62h changed nothing here. (b) With the scaffold on, 40 of the 80 lesson attempts start at stage 3 (first right action fire) for both instruments, and none with it off. No scaffolded accuracy was printed or stored. Cadence prints a RuntimeWarning about a finite teaching free phase using its whole budget; it comes from the library's teaching step and was present before (not a design change).

## Pilot
- 2026-10-20 ~14:55-15:05, 608 s at 4 workers, 24 students (7_590_000+), share .5 (`exp/EXP-62i-pilot.*`). Validity only: untaught A off .349, A on .448, D1 off .708, D1 on .797 (no ceiling); know-4 worth A off +.294 (.046), A on +.146 (.031), D1 off +.411 (.057), D1 on +.232 (.047) (all take in content). Exposure check: under know-late-2, A with the scaffold hears 29.5 late labels per student against D1's 6.7 without it, so the fallback share is not needed. phi's robust SE .858 -> N = 24 x (.858 / .10)^2 = 1,776 -> **capped at 720**. At 720 the expected SE is about .16, so the 95% interval is about plus or minus .31, and a verdict other than INCONCLUSIVE needs phi below about .19 or above about .81. Nothing in the design changed. The pilot's phi is not reported, as registered. (A divide-by-zero warning in the pilot's bootstrap came from draws whose A-D1 gap was exactly 0 at n 24; recorded, not changed.)
