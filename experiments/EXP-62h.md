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
- PENDING.

## Reflection
- PENDING.
