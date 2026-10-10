# EXP-35: pedigree share as a control dial (fixed share vs PI controller, with DISCOVERY) at K=48

- Date: 2026-10-09 | Cadence version: unrecorded in outputs (iter25 notes the clone was still v0.78.0 / `750c8ef` that day) | Program iter: iter23
- Script: `exp/EXP-35_pedigree_controller.py` | Evidence: `exp/EXP-35.out`, `exp/EXP-35.json`

## Summary
- Question: does the pedigree share (the cut of teaching pay that goes to an item's origin) change how much brains
  discover, and can a PI controller set it as well as the best fixed value?
- Setup: K=48 bandit contexts, N=8 brains each knowing 4 (32 known to the network, 16 known to nobody). EXP-33 fix world
  (notes, drift-check, rehearse). Each round each brain TEACHes (oracle neediest peer; pay = student's measured gain,
  origin gets share ALPHA) or DISCOVERs (D=40 graded trials on an unknown context; becomes its origin). Move chosen by a
  running pay estimate per move, epsilon 0.15. Arms: ALPHA 0 / 0.3 / 0.6 / 0.9 and PI. 20 rounds, 6 seeds.
- Prediction: "low ALPHA under-discovers (network stalls near 32/48 = 0.83 + chance on the rest); high ALPHA
  over-discovers and spreads slowly; PI matches or beats the best fixed ALPHA."
- Result (final acc with SEM over 6 seeds / mean-over-time / network-knows / share of moves discovering):
  0.0: 0.948 (0.008) / 0.803 / 1.00 / 0.29; 0.3: 0.955 (0.005) / 0.808 / 1.00 / 0.32; 0.6: 0.947 (0.005) / 0.795 / 1.00 / 0.34;
  0.9: 0.967 (0.006) / 0.809 / 1.00 / 0.37; PI: 0.952 (0.007) / 0.802 / 1.00 / 0.33, alpha path 0.42 0.36 0.14 0.00 0.00.
- Verdict: NULL (logged iter23), and the null is uninformative: the world hit a ceiling and, by code reading, the
  move-credit accounting has the same flaw that made EXP-35b VOID in iter25. SUPERSEDED by EXP-35b (K=96, teachers choose
  own vs relayed items), which was itself VOID (iter25) and then NULL with a starved share channel (iter27).

## Reflection
- What it means: we learned nothing about whether the share drives discovery. Discovery effort rose only 0.29 to 0.37
  across shares and every arm ended with the network knowing 100% of contexts, so the low-share stall the prediction
  needed never happened. The PI controller drove the share to 0.
- Process: logged in iter23 as partly a process error: only a 2-round smoke ran, not a window pilot (RUN GATE line 2
  skipped). Named flaws: (1) ceiling, the world is fully discovered within 20 rounds; (2) discovery pays even at share 0,
  because a discoverer teaches its own find and keeps all the pay; (3) relaying was not a choice (items picked at random),
  so half of what the share controls was absent. Additional flaw found in this write-up by reading the script (not
  logged in the program): each round's earnings, royalty included, are credited to whatever move the brain made that
  round, and a DISCOVER move earns nothing when made, so royalty reaches the Discover estimate only in rounds where the
  origin happens to discover again; mostly it inflates the Teach estimate. This is the same credit bug that voided
  EXP-35b iter25. The PI integral term is also unbounded (alpha is clipped to 0-0.95 but the integral is not, so no
  anti-windup), and both move estimates start at 0.05. Version not stamped.
- Lesson: before testing a knob, trace the chain knob to signal to estimate to choice to outcome and confirm every link
  moves (this became RUN GATE item 5, CHAIN, after iter27); and pilot the effect window under run conditions.
- Next: EXP-35b at K=96 (two-thirds unknown), teachers choosing own vs relayed items, window pilot first.
