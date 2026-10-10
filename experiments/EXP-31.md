# EXP-31: peer-to-peer bidirectional teaching vs a one-way ring

- Date: 2026-10-09 | Cadence version: unrecorded | Program iter: iter20
- Script: `exp/EXP-31_peer_exchange.py` | Evidence: `exp/EXP-31.out`, `exp/EXP-31-M16.json` (the program log cites `EXP-31.json`; the file on disk is `EXP-31-M16.json`)

## Summary
- Question: does random two-way peer teaching spread knowledge through a network faster than one-way teaching around a ring?
- Setup: N=8 plain Cadence brains (modules 16,8), K=32 two-action bandit. Each brain starts trained on its own slice of K/N contexts and keeps a KNOWN set that grows when it ends up agreeing with a peer on a taught context. Specialist rule (EXP-29): teachers only teach their KNOWN set. Session = M=16 graded steps (+1 if the student matches the teacher's greedy answer, -1 otherwise). Arms, N sessions per round each: RING (brain i teaches i+1) vs PEER (random pairs, both directions). 12 rounds, 6 seeds. Score = mean accuracy of all brains on the true rule.
- Prediction: "PEER reaches high accuracy in clearly fewer rounds than RING (two-way gossip spreads exponentially, a one-way ring linearly); copy errors may spread less in PEER." (script docstring, written before running)
- Result: mean accuracy by round, RING 0.57 0.71 0.76 0.77 0.76 0.76 0.77 0.76 0.76 0.77 0.77 0.77 0.78; PEER 0.57 0.63 0.69 0.73 0.76 0.78 0.79 0.79 0.80 0.78 0.79 0.79 0.79. Final round, mean (SEM, 6 seeds): RING 0.778 (0.025), PEER 0.789 (0.031). No run in either arm reached 0.90.
- Verdict: NULL. The prediction was wrong: RING was faster early, PEER only slightly higher late, and the finals are not distinguishable. Both arms plateau near 0.78. The plateau, left open here, was later explained by EXP-33 (iter21): brains kept teaching items they had since forgotten (stale teaching); provenance notes plus drift-check lifted the ceiling to about 0.99.

## Reflection
- What it means: in this world, who teaches whom was not the binding constraint; a shared ceiling near 0.78 was. The "exponential gossip" intuition did not show up because knowledge was being lost about as fast as it spread.
- Process: no pilot recorded. The run took 337 s, under the RUN GATE threshold (runs longer than about 10 min), so the gate lines were not required; the docstring has a PREDICTION but no WINDOW line. The plateau put both arms at a ceiling well before round 12, so the window for comparing spreading speed was mostly closed, and the "rounds to 0.90" metric was never reached by any run, so it carried no information. With 6 seeds the SEMs (about 0.03) are larger than the 0.011 final difference. Default WORKERS=6. The evidence file name differs from the one cited in the program log. Cadence version not stamped.
- Lesson: check for a common ceiling before comparing rates; if every arm plateaus at the same level, find the cause of the plateau before testing the mechanism you care about.
- Next: the plateau became the question of EXP-33 (stale teaching, fixed by the provenance ledger), and partner choice was revisited on the fixed network in EXP-34. Same day, this world was reused for the $SPAWN market sim (EXP-32).
