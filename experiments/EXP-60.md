# EXP-60: does keeping misses out of the temporal context also help on the normal Stone Age chain, where the inventory is visible?

- Date: 2026-10-14 | Cadence version: 0.83.0 (`23dba71`, `~/_cadence_study`) | Program iter: none (memory track; scope check on EXP-57 before it is reported to the group)
- Script: `exp/EXP-60_hold_on_visible_chain.py` (EXP-56's brain, trace rule and readings; EXP-45's observation) | Evidence: `exp/EXP-60-full.json/.jsonl/.out`

## Summary
- Question: EXP-57 found that keeping decisions which left the observation unchanged out of the temporal context takes clean greedy passes of Huncho's hidden-inventory chain from 4/96 to 38/96. That chain shows the same observation at stages 1 and 3 and at 2 and 4, so memory has to carry the stage. The normal chain shows the inventory (has wood, has stone, has fire), so each stage has its own observation and place records alone can key it (EXP-46: per-state .94 with memory). Is the rule's gain specific to the hidden-inventory case?
- Setup: EXP-56/57 exactly (0.83 `Brain.compose(7, 5, modules=(48, 24), arousal=True, memory_choice=True)`, V5 chamber rules, 120 attempts, natural and corrective signals, readings in sequence on a saved copy) except the observation is EXP-45's visible-inventory vector at each stage. Arms: `ctx5` and `hold5`, 48 fresh seeds per signal (60_000 + i); `place` (context 0) on the first 24 seeds per signal as a reference.
- RUN GATE: (1) prediction below, written before any run. (2) Window: EXP-46 ran this chamber with this brain and memory on (corrective greedy solves 11 of 12), so ctx5 may sit near ceiling under corrections; the natural signal has room. No pilot; a ceiling is reported as such. (3) Variance: arms share each seed; paired exact McNemar for clean passes, paired SEM for rates. (4) Metric: clean greedy pass (four stages in four greedy decisions). (5) Chain: visible inventory -> place records key each stage -> less for the context to carry -> less for the hold rule to fix.
- Prediction (written before any run):
  - (P1) The rule's gain is much smaller here: (hold-only minus ctx5-only clean-pass pairs), pooled over 96 pairs, is at most 17, half of EXP-57's 34.
  - (P2) Place memory works on this chain: place's clean greedy passes are at least half of ctx5's on the same 48 seed pairs.
  - (P3) The rule does no harm here: ctx5-only pairs do not exceed hold-only pairs.
- Decision rule (written before any run): P1 and P2 hold -> the rule matters when the observation does not show progress, which is the case Bernhard's "which memories matter" is about; the group message says the gain is specific to the hidden-inventory chain. P1 fails (a large gain here too) -> the rule is general to this chain family, and the message says so. P3 fails -> the rule has a cost when the inventory is visible, and the message says that.
- Result (fresh seeds 60_000+, 120 attempts; `exp/EXP-60-full.*`):

  | visible-inventory chain | pairs | clean greedy passes | hold5- or place-only pairs / ctx5-only (exact McNemar p) | first try (SEM) | sampled success |
  |---|---|---|---|---|---|
  | hold5 vs ctx5, natural | 48 | 31 vs 33 | 8 / 10 (p .81) | +.016 (.037) | .862 vs .847 |
  | hold5 vs ctx5, corrective | 48 | 44 vs 42 | 6 / 4 (p .75) | -.004 (.018) | .987 vs .983 |
  | **hold5 vs ctx5, pooled** | 96 | **75 vs 75** | **14 / 14 (p 1.0)** | +.006 (.021) | .925 vs .915 |
  | place vs ctx5, pooled | 48 | 39 vs 40 | 6 / 7 (p 1.0) | +.012 (.032) | .946 vs .934 |

  P1 HELD (hold-only minus ctx5-only is 0, under 17). P2 HELD (place 39 vs ctx5 40 clean passes). P3 HELD (14 vs 14, no harm).
- Verdict: SUPPORTIVE, 3 of 3. When the inventory is visible, place memory alone keys each stage and the hold rule changes nothing (75 vs 75 clean passes of 96), against 38 vs 4 on the hidden-inventory chain (EXP-57). Decision rule: the rule matters when the observation does not show progress; the group message says the gain is specific to that case.

## Reflection
- What it means: the 4% to 40% jump in EXP-57 is a property of chains where what the brain sees does not show how far it has got, which is exactly the case Bernhard's "learn which memories matter" is about. On the ordinary chain the brain already does well (78% clean greedy passes with or without the rule) and the rule is neutral, so turning it on costs nothing where it is not needed. Whether it costs something where an action is correct but invisible is EXP-59.
- Process: pre-registered before any run, fresh seeds, no pilot (same machinery as EXP-56/57, prior data on this chamber from EXP-46); ran while the atlas UI was being fixed. Limits: our rebuild of the chamber, one composed brain, 120 attempts only.
- Lesson: before reporting a mechanism's gain, run it where the problem it fixes is absent; a gain that vanishes there is evidence it fixes that problem and not something incidental.
- Next: EXP-59 (the rule's boundary: a correct action that changes nothing visible).
