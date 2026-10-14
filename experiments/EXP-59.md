# EXP-59: where the hold rule breaks: a correct action that leaves the observation unchanged

- Date: 2026-10-14 | Cadence version: 0.83.0 (`23dba71`, `~/_cadence_study`) | Program iter: none (memory track; the boundary EXP-57's reflection named before the rule is proposed upstream)
- Script: `exp/EXP-59_hold_boundary.py` (EXP-56's brain, trace rule and readings; a new observation map) | Evidence: `exp/EXP-59-full.json/.jsonl/.out`

## Summary
- Question: EXP-57's rule (a decision whose next observation is unchanged never enters the temporal context) assumes "the observation did not change" means "the decision did nothing". Here that assumption is false by construction: gathering wood is correct but invisible. Stages 1 and 2 both show observation A (right action WOOD, then STONE); STONE turns it into B (FIRE), then C (WARM). The only thing that tells stage 2 from stage 1 is the brain's own successful WOOD, which the hold rule erases.
- Setup: EXP-56 exactly (0.83 `Brain.compose(7, 5, modules=(48, 24), arousal=True, memory_choice=True)`, V5 chamber rules, 10 decisions per attempt, 120 attempts, natural and corrective signals, readings in sequence on a saved copy) with observations A, A, B, C at the four stages. Arms `place`, `ctx5`, `hold5`, 48 fresh seeds per signal (59_000 + i).
- RUN GATE: (1) prediction below, written before any run. (2) Window: no pilot; same machinery as EXP-56/57, and the stage-2 first-try reading is the one that matters; a floor is reported as such. (3) Variance: paired by seed; exact McNemar on clean passes, paired SEM on rates. (4) Metric: first-try accuracy at stage 2 (STONE at A, after the invisible WOOD). (5) Chain: hold erases the correct WOOD -> stage 2's key equals stage 1's -> the vote at stage 2 repeats stage 1's answer (WOOD) -> wrong.
- Prediction (written before any run):
  - (P1, headline) The rule breaks at the invisible step: first-try accuracy at stage 2 is lower under hold5 than under ctx5 by at least .15, pooled, more than 2 SEM.
  - (P2) Clean greedy passes: ctx5 has more ctx5-only pairs than hold5-only pairs, pooled.
  - (P3) At the stages where the observation does change (3 and 4), hold5 is not worse than ctx5 on first-try accuracy (difference > -.05 pooled).
- Decision rule (written before any run): P1 holds -> the rule as stated is wrong in general; the gate has to be "the decision changed nothing", which the observation alone cannot tell when actions can have invisible effects; any upstream proposal names that limit and the signal it would need (outcome, reward, or the brain's own forecast). P1 fails -> the rule survives even an invisible correct step at this horizon, which needs explaining before anyone relies on it.
- Result (48 fresh seeds per signal, 120 attempts; `exp/EXP-59-full.*`). First-try accuracy by stage, pooled (stage 2 is STONE at A, after the invisible WOOD):

  | arm | stage 1 | stage 2 | stage 3 | stage 4 | clean greedy passes (of 96) | sampled success |
  |---|---|---|---|---|---|---|
  | place | .21 | .42 | .68 | .95 | 2 | .275 |
  | ctx5 | .22 | .54 | .71 | .93 | 9 | .481 |
  | hold5 | .19 | .39 | .70 | .95 | 2 | .302 |

  hold5 - ctx5 first try: stage 1 -.030 (.028), stage 2 -.157 (.042), stage 3 -.021 (.038), stage 4 +.024 (.020). Clean passes: ctx5-only 7, hold-only 0 (exact McNemar p = .016). By signal, sampled success ctx5 vs hold5: natural .158 vs .125, corrective .805 vs .478.
  P1 HELD (stage 2 -.157, 3.7 SEM). P2 HELD (7 vs 0). P3 HELD (stages 3 and 4 within -.05).
- Verdict: SUPPORTIVE, 3 of 3 (the predicted break). When a correct action changes nothing visible, the hold rule erases it, the invisible step falls back to place-memory level (.39 vs place .42), and with corrections sampled success drops from .81 to .48. Decision rule: P1 held, so the rule as stated is wrong in general; the gate has to be "the decision changed nothing", which the observation alone cannot tell.

## Reflection
- What it means: EXP-57, 59 and 60 together pin the rule down. It helps a lot when progress is hidden and misses are the only unchanged-observation decisions (EXP-57), does nothing when progress is visible (EXP-60), and hurts when a correct action is invisible (EXP-59). The memory that matters is "the decision that changed something", and the observation is only a proxy for that. A working gate needs a signal that tells a miss from an invisible success: an outcome, a reward, or the brain's own forecast error. Cadence's replay path makes the same observation-equality judgment (`_extend_paths`), so it may share this blind spot; untested here.
- Process: pre-registered before any run, fresh seeds, no pilot (same machinery); ran beside EXP-58 and EXP-61 on shared cores, which changed timing only. Limits: our rebuild, one composed brain, 120 attempts, one kind of invisible step.
- Lesson: name the boundary of a fix and test it before proposing the fix; here the boundary is the fix's main limitation and belongs in the same message as the gain.
- Next: a gate keyed on outcome rather than observation (hold only decisions the world answered as failures), on all three chambers.
