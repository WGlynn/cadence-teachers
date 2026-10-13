# EXP-47: after the caregiver leaves, does the taught chain drift through `step`, through `live`, or both?

- Date: 2026-10-13 | Cadence version: 0.83.0 (`23dba71`) | Program iter: none (teaching track; follow-up to EXP-46)
- Script: `exp/EXP-47_alone_live_vs_step.py` | Evidence: `exp/EXP-47-pilot.*`, `exp/EXP-47-full.json/.jsonl/.out` (PENDING)

## Summary
- Question: upstream's 0.83 caveat says that after 80 episodes alone through `step` the frozen greedy policy of the corrected chain can stall at one stage while the sampled policy still succeeds, and that through `live` it does not. EXP-46 saw the per-state answers drift through `live` too (all four right 9 -> 5 of 12) while full-chain success held. From the same taught brains, which path drifts, in which reading, and when?
- Setup: EXP-46's memory brain (`Brain.compose(7, 5, modules=(48, 24), arousal=True, memory_choice=True)`) on EXP-45's V5 chamber replica; 120 teaching attempts, signals corrective and natural; then 80 attempts alone (world reward only) through `live` and, from a copy of the same taught brain, through `step`. Readings on frozen copies after teaching and after 10, 20, 40, 80 attempts alone: per-state greedy accuracy and answers, greedy full-chain, sampled full-chain (100 attempts). Seeds 42-53 (the taught brains for 42-53 are EXP-46's memory arms).
- RUN GATE: (1) prediction below, written before the pilot. (2) Window: a 3-seed pilot at exact run conditions; EXP-46 already measured the end point of the `live` path (corrective: all four right 9 -> 5 of 12, greedy full-chain 11 -> 12, sampled .955), which sets the window for the drift reading. (3) Variance: the two paths start from the same taught brain per seed, so the comparison is paired. (4) Metric: per-state greedy accuracy (all four right) and greedy full-chain solves are read side by side, because the caveat is about the greedy full-chain reading and EXP-46's drift is in the per-state one. (5) Chain: taught -> 10 -> 20 -> 40 -> 80 per path.
- Prediction (written before the pilot):
  - Check, not a prediction: the taught readings equal EXP-46's memory arms on the same seeds (same code, same seeds).
  - (P1) Upstream's caveat holds for the greedy full-chain reading: after 80 alone, corrective greedy full-chain solves through `step` are fewer than through `live` (EXP-46: 12/12 through `live`).
  - (P2) The per-state drift is not specific to `step`: corrective all-four-right falls under both paths by 80 (`live` reproduces EXP-46's 5/12), and by at least 2 seeds under each.
  - (P3) Sampled full-chain stays at or above .9 after 80 alone for corrective under both paths.
  - (P4) The drift is early: most of the per-state loss by 80 is already there by 20 attempts alone.
- Decision rule (written before the pilot): P1 and P2 hold -> the caveat is right about greedy full-chain success and incomplete about the mapping: `live` keeps the chain completing while stage answers drift underneath, so per-state accuracy should be read beside full-chain success after the caregiver leaves. P1 fails (step as good as live) -> the caveat does not reproduce on this chamber at this budget.
- Pilot (3 seeds, 42-44, exact run conditions, `exp/EXP-47-pilot.out`), read before the full run: the check held (taught readings equal EXP-46's memory arms on the same seeds), and the `live` path at 80 reproduces EXP-46's after-alone readings exactly (.75 / .75 / 1.00 corrective), so saving a copy mid-stream does not perturb it. Drift is non-monotonic on both paths (stages lost and regained between checks), not at a floor or ceiling; no design change. The full run reuses the pilot's three seeds as rows and adds seeds 45-53.
- Result: PENDING. Verdict: PENDING.

## Reflection
- PENDING (after the run).
