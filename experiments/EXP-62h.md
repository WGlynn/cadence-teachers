# EXP-62h: is the scaled exchange rate between early and late knowledge the same across brains?

- Date: pre-registered 2026-10-20 (Will's go 2026-10-20 06:57), before any EXP-62h data | Cadence version: 0.84.3 (`8dc92d8`), record at run time | Program iter: iter42
- Script: `exp/EXP-62h_scaled_rate.py` (EXP-62g's harness at budget 6; instruments A, C, D1) | Evidence: `exp/EXP-62h-pilot.*`, `exp/EXP-62h-full.*`

## Pre-registration (written 2026-10-20, before any EXP-62h data)

**In one line: once each brain's numbers are scaled by how much it absorbs, do brains agree on how much late knowledge is worth against early knowledge?**

**Why.** EXP-62b and EXP-62g found the same order of worth across three brains, but different raw gaps between early and late knowledge. We then re-read both in exploratory form. Each brain's gap was divided by its own know-4 worth, which is a measure of how much that brain absorbs. Scaled that way, the cross-family pair in EXP-62g agreed (A .71, D1 .76). The near-relative pair in EXP-62b did not (A .46, C .66). Those two readings came from different tasks (budget 10 and budget 6), were not registered, and had wide intervals (about plus or minus .35). This test measures the scaled rate for both kinds of pair, on one task, as the primary quantity, with a sample size set to separate about .10.

**Setup.** EXP-62g's harness, teachers and readings, at budget 6 (6 decisions per attempt) and lesson 80. Teachers: know-early-2, know-late-2, know-4, null (random labels, the zero), untaught. Instruments, fixed now:
- A: EXP-58's delayed-credit brain (the reference).
- C: EXP-62b's C, the near relative (A with 64 units and critic rate 2.0).
- D1: EXP-62g's D1, the cross-family brain (the memory-choice architecture with A's learning rule).
D2 is dropped: it equalled D1 in every arm of all 51 students measured (3 in the EXP-62f pilot, 48 in EXP-62g), so it adds nothing. Every instrument sees the same student seeds and the same label seeds, so the comparisons are paired. Fresh seeds: pilot 7_490_000 + student, full 7_400_000 + student. No script in `exp/` uses 7_400_000 or 7_490_000 (checked by grep).

**Primary quantity.** For instrument I: s_I = mean(D_I) / mean(K_I), where D_I = acc(know-early-2) - acc(know-late-2) and K_I = acc(know-4) - acc(null), both per student. Pairs: near relatives A-C, cross-family A-D1. For each pair, the difference s_J - s_A and its 95% interval from a paired bootstrap over students (10,000 draws, seed 62).

**Pilot, which sets N (before the full run).** 24 students, all three instruments. Stop rules, checked first: if any instrument's mean untaught accuracy is .90 or more (ceiling), or any instrument's know-4 worth is below .10 or below 2 SEM (it does not take in content), the full run does not start. Otherwise N = 24 x (SE / .05)^2, rounded up to a multiple of 24 and held between 96 and 720. SE is the larger of the two pairs' bootstrap SEs of s_J - s_A in the pilot. The target is an SE of about .05, so that a difference of .10 is about 2 SE. At the cap of 720, the run takes about 4 to 5 hours at 4 workers. The pilot's students are not reused in the full run, and the pilot's differences are not reported as a result.

**Predictions (written before any data).**
- The near relatives differ (A-C interval excludes 0): about 60%. EXP-62b's exploratory reading was +.195.
- The cross-family pair agrees within plus or minus .10 (A-D1 interval inside [-.10, +.10]): about 35%. EXP-62g's reading was close to 0, but its interval was wide.
- The pilot sets N at the 720 cap: about 50%.

**Decision rules (written before any data).**
- RATE DEPENDS ON THE BRAIN: the 95% interval of s_J - s_A excludes 0 for at least one pair.
- RATE AGREES: both pairs' 95% intervals lie inside [-.10, +.10].
- Otherwise: INCONCLUSIVE (neither different nor shown equal within .10).
- Reported with every verdict: each pair's difference and its interval. Also, as secondary readings: the late/early worth ratio for each instrument, the raw D difference, and the late-label counts.
Loop verdict: DEPENDS -> CONFIRMED (the instrument sets the exchange rate even after scaling); AGREES -> REFUTED; INCONCLUSIVE -> INCONCLUSIVE.

## Pilot
- 2026-10-20 07:15-07:33, 1,071 s at 2 workers (sharing the machine with EXP-68), 24 students (7_490_000+), Cadence 0.84.3 (`exp/EXP-62h-pilot.*`). Validity only: untaught A .352, C .372, D1 .786 (no ceiling); know-4 worth A +.255 (.039), C +.180 (.044), D1 +.385 (.059) (all take in content). Largest pair SE .294 -> N = 24 x (.294 / .05)^2 = 840 -> **capped at 720**. The cap leaves the target SE at about .055, so a difference of .10 is about 1.8 SE, not 2. Nothing else in the design changed. The pilot's differences are not reported, as registered.

## Summary
- Question: once each brain's numbers are scaled by how much it absorbs, do brains agree on how much late knowledge is worth against early knowledge?
- Setup: as registered. Cadence 0.84.3 (`8dc92d8`), budget 6, lesson 80, N 720 from the pilot (0ae8bf9), seeds 7_400_000+, 2,160 student-instruments, 14,501 s at 4 workers (a detached process).
- Prediction: see the pre-registration (near relatives differ about 60%; cross-family agree within .10 about 35%; N at the cap about 50%).
- Result. s = mean(early - late) / mean(know-4 worth), per instrument:
  - A (delayed-credit): s .874. know-4 worth +.243 (.007), D +.213 (.008), late/early worth ratio .044, untaught .341.
  - C (near relative): s .937. know-4 +.264 (.007), D +.247 (.007), late/early .009, untaught .340.
  - D1 (cross-family): s .610. know-4 +.462 (.011), D +.282 (.012), late/early .326, untaught .643.
  - **A-C: +.064 (SE .046, 95% interval -.025 to +.153).** No difference detected, and not shown equal within .10.
  - **A-D1: -.263 (SE .043, 95% interval -.349 to -.180).** The interval excludes 0.
  - Late-label events per student, know-late-2 arm: A 5.7, C 5.6, D1 7.8; know-early-2 arm: 15.0, 16.5, 31.1.
- Verdict: **RATE DEPENDS ON THE BRAIN** (loop: CONFIRMED).

## Reflection
- What it means: after scaling by how much each brain absorbs, the cross-family brain still prices late knowledge differently. To the two delayed-credit brains, a teacher who knows only the late stages is worth almost nothing next to one who knows only the early stages (late/early .04 and .01). To the memory-choice brain it is worth about a third (.33). All three brains still rank the teachers the same way: know-4, then early, then late. What differs is how much late knowledge is worth next to early knowledge. That rate depends on which brain judges, and scaling by how much each brain absorbs does not remove the difference. The near relatives do not differ detectably. At this sample size that means any rate difference between them is under about .15.
- For Noesis (measure-only): a payout rule that prices kinds of contribution through one learned judge inherits that judge's exchange rate. The order is robust across these brains; the rate is not. Any rule that pays by rate needs either more than one judge from different families, or a declared judge whose rate is part of the rule, stated up front. More judges do not settle the rate by themselves. Judges from different families give a range, not one number. Here late knowledge was worth .04 of early knowledge to one judge and .33 to another. So the rule still has to say which point of that range it pays, for example the lowest. And a declared judge invites contributors to fit that judge, which is the same capture problem the frozen-judge rule already addresses.
- Prediction check: "near relatives differ" (60%) did not hold; "cross-family agrees within .10" (35%) did not hold, it differed by .26; "N at the cap" (50%) held (840 asked, 720 run).
- Both exploratory readings that motivated this test were wrong, and in opposite directions. EXP-62g (n 48) suggested the cross-family pair agreed once scaled (.71 vs .76). The EXP-62b re-read (n 48) suggested the near relatives differed (.46 vs .66). At n 720 on one task, the cross-family pair differs and the near relatives don't. Even A's own late/early ratio moved from .16 (EXP-62g, n 48) to .04 here. Both earlier write-ups now carry an addendum pointing here.
- Lesson: an exploratory ratio of two noisy means at n 48 can point either way. At intervals as wide as these (about plus or minus .35), treat it as a reason to run a powered test, not as a reading. The pre-registered internal pilot sized this run correctly. Its SE estimate (.294 at n 24) predicted the run's actual SE (.043 to .046 at n 720) almost exactly.
- Mechanism hint (not tested). A late-only teacher can only help a student that gets far enough to hear it. D1 gets further on its own: untaught accuracy .643, against .34 for A and C. So a late-only teacher gets more chances to teach it (7.8 late labels per student, against 5.6). And D1 already knows enough of the early chain to put those late labels to use.
- Next: test that hint directly. Equalize how far students get (a scaffold that starts some attempts at stage 3) and check whether the delayed-credit brains' late/early ratio rises toward D1's. If it does, the "exchange rate" is mostly exposure, not valuation.

## Addendum (2026-10-20, from EXP-62i)
- EXP-62i tested the mechanism hint above and found more than exposure. Its exploratory section re-read this run's stored arms. The random-label null hurts D1 and not the delayed-credit brains: null minus untaught is D1 -.129 (SEM .015), A -.012 (.006), C -.006 (.006). A late-only teacher differs from the null only by giving right labels instead of random ones at the late stages. So D1's late worth of +.136 is mostly the harm that random late labels do. Measured against the untaught twin, D1's late-only teacher is worth +.008 (.015), and the A-D1 late/early gap is +.037 (95% -.078 to +.147), not detected. The numbers above stand. The reading "a brain built differently still prices late knowledge differently" holds only for worth measured against a random-label decoy. EXP-62i's off condition, an independent sample of 720, shows the same pattern.
