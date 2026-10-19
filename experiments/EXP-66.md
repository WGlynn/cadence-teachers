# EXP-66: a per-miss penalty through the reward channel, with and without the gate keyed on it

- Date: pre-registered 2026-10-19 (not run) | Cadence version: 0.84.3 (`8dc92d8`, `~/_cadence_study`) | Program iter: none (memory track; upstream #202)
- Script: `exp/EXP-66_penalty_gate.py` (imports EXP-65, which imports EXP-63 and EXP-56: same chambers, brain, signals, trace rule and readings) | Evidence: `exp/EXP-66-check.out`, `exp/EXP-66-pilot.*`, `exp/EXP-66-full.*`

## Pre-registration (written 2026-10-19, before any EXP-66 data)

**Why.** Bernhard's #202 status review (2026-10-18, comment 6248152993) asks, before any implementation, to "specify precisely which available signal holds a decision out of the key. If a failed action receives a new negative reward, compare that reward change with and without the gate to separate altered information/learning from the key rule", and to keep the ambiguous-chain paired test, the fully observed preservation floor and the invisible-action boundary. EXP-63 showed the outcome gate's gain with the chamber's success flag read as an oracle; EXP-65 showed that neither the teacher's label nor the brain's own forecast error stands in for it. This experiment specifies the signal and runs his comparison.

**The signal, stated precisely.** The `reward` argument that `step()` already receives. The gate holds the previous decision out of the temporal context when the reward delivered with the current call is below 0, on non-boundary calls only (the library clears the context at done; no gate acts there). No other input is read.

**What this does and does not test.** A per-miss penalty changes the world: a chamber that charges a small cost for a wasted move. On the invisible chain it carries exactly the bit the oracle carried (a stage-1 miss pays -p, the invisible correct WOOD pays 0). So this is not a test of whether the brain can infer a hidden success flag on its own; it cannot (EXP-65, AUC .525). It tests whether a failure input delivered as a reward convention, through a channel Cadence already has, can key the gate, and how much of any gain is the penalty's own effect on learning rather than the key rule. Per #210, on 0.84.x a nonzero reward makes a decision eligible for an episodic write (`generic.py` 3138 at 0.84.2: `known = learned & ((reward != 0) | done | woken | marked)`), so the penalty alone can change memory through extinction. That is why the penalty-without-gate arm is required.

**Setup.** EXP-63 exactly (`Brain.compose(7, 5, modules=(48, 24), arousal=True, memory_choice=True, memory_context=.5)`, efference off, V5 rules, 10 decisions per attempt, 120 attempts, natural and corrective signals, readings on a saved copy with the plain context). Re-measured on 0.84.3, not reused from 0.83, because 0.84.1 changed memory_choice (#204). Fresh seeds 66_000 + i. Three chains:
- invisible (A, A, B, C; the correct WOOD changes nothing visible): 48 lives per signal;
- hidden, the ambiguous chain (A, B, A, B): 24 per signal;
- visible, fully observed (inventory): 24 per signal.

Four arms, a two-by-two of penalty and gate, every arm gating (if at all) during training only and reading plain:
- `ctx5`: no penalty, no gate (the founder key);
- `out5t`: no penalty, EXP-63's oracle gate during training (the ceiling, as in EXP-65);
- `pen`: a non-terminal miss pays -p instead of 0, no gate;
- `peng`: the same penalty, gate keyed on reward < 0.
The terminal reward is unchanged (+2 success, -1 failure; a miss that ends the attempt pays -1, not -1 - p). Arms are paired by seed (same brain initialisation). In `peng` the gate holds exactly the non-terminal misses, the same decisions out5t's oracle holds, but through the reward argument.

**Penalty size p, fixed by a pilot on a diagnostic that is not an outcome.** Grid {.02, .05, .10}; every value keeps a whole attempt of misses (at most 9 non-terminal) below one failure outcome (9 x .10 = .90 < 1), so none swamps the +2 / -1 episode outcome. Pilot: invisible chain, seeds 66_500 + i, 6 per signal, arm `pen` at each p (plus `peng` for the chain links). Rule: p = the smallest grid value at which the pen arm's mean per-life stage-1 AUC (the brain's own forecast error, miss vs the invisible WOOD, P(miss < WOOD)) pooled over 12 lives is at least .75, i.e. the smallest penalty the learner can see; if none reaches .75, p = .10 and that is reported. The pilot writes p to `EXP-66-pilot.json` and the full run reads it from there. The pilot cannot change arms, seeds, chains, metrics or predictions.

**Check (`MODE=check`, before the pilot; a failure stops the run).** (a) This script's ctx5 life equals EXP-63's harness ctx5 life on 0.84.3 (seed 66_990, all read fields), and out5t trains and passes greedily exactly as EXP-63's out5. (b) At p = 0, pen and peng are identical to ctx5. (c) At p = .05, peng holds only misses and holds every non-terminal miss (held = held-on-miss = logged misses; held-on-correct = 0). (d) The learner's dopamine is alive (nonzero, varying) in pen at p = .05.

**Readings.** Clean greedy pass (four stages in four greedy decisions), first-try accuracy by stage, sampled success over 100 attempts; exact McNemar on clean-pass discordant pairs; paired SEM on rates. Diagnostics per life: held decisions (on misses / on correct moves / on the invisible WOOD), stage-1 AUC of the forecast error.

**Predictions (written before any run).** Invisible chain pooled over signals (96 pairs) unless stated.
- (P0, precondition) The oracle gate's gain survives 0.84.3: out5t-only > ctx5-only clean passes, exact McNemar p < .05 (0.83: 19 vs 5).
- (P1, headline: the key rule) peng > pen: peng-only > pen-only clean passes, exact McNemar p < .05.
- (P2, the separation) The gate's contribution exceeds the penalty's: (peng-only minus pen-only) > (pen-only minus ctx5-only), in discordant clean-pass pairs.
- (P3, the invisible-action boundary) peng never holds a correct decision, and stage-2 first-try accuracy peng - ctx5 > -.05.
- (P4, the ambiguous-chain paired test; hidden chain, 48 pairs) peng > ctx5: peng-only > ctx5-only, exact McNemar p < .05 (0.83 oracle: 14 vs 1).
- (P5, the preservation floor; visible chain, 48 pairs) No reliable loss: not (ctx5-only > peng-only with exact McNemar p < .05).
- Reported, no verdict weight: pen vs ctx5 on every chain (the penalty's own learning effect, two-sided), peng vs out5t (reward gate plus penalty against the oracle gate without it), sampled success and first tries.

**Decision rules (written before any run).**
- P1, P3, P4 and P5 hold: SUPPORTIVE. For #202: the signal is "the reward this decision received was negative"; a world that charges a small cost per miss keys the outcome gate through `step()`'s existing argument, and the gate adds a measured gain over what the penalty teaches. P2 then says whether the key or the penalty carries more of it.
- P1 fails and pen > ctx5 (exact McNemar p < .05): BOUNDARY (the penalty does the work). The gain is the reward change's effect on learning (the #210 extinction path), not the key rule; for #202 the recommendation is the reward convention, with no gate.
- P1 fails and pen is not reliably above ctx5: NULL at this penalty size and 120 attempts.
- P3 or P5 fails: the reward gate breaks something it must not; a blocking caveat for #202, investigated before any claim.
- P0 fails: the oracle gate's gain itself did not survive 0.84.x; P1 is reported but read in that light, and the #202 note leads with the version change.
Loop verdict: CONFIRMED (SUPPORTIVE) / INCONCLUSIVE (BOUNDARY) / REFUTED (NULL).

**Not measured.** The failed action's episodic record value (the #210 readout). No public read of a single record was checked before this registration; the pen-vs-ctx5 contrast carries that pathway at the behaviour level.

**Check and pilot (2026-10-19, after the registration, before the full run; nothing in the design changed).**
- Check (`exp/EXP-66-check.out`): PASS. ctx5 through this script equals EXP-63's harness at 0.84.3; out5t trains and passes greedily as EXP-63's out5; pen and peng at p = 0 equal ctx5; at p = .05 peng held exactly the 264 non-terminal misses of the life and no correct move; dopamine alive. Library warning seen in corrective lives (finite teaching free phase used its free_steps budget; 0.84.x), recorded, not acted on.
- Pilot (`exp/EXP-66-pilot.*`, invisible chain, seeds 66_500+, 12 lives per p): pen-arm stage-1 AUC .626 at p .02, .774 at .05, .918 at .10. Rule: smallest p with AUC >= .75, so **p = .05**. peng held 6,687 / 7,023 / 7,357 decisions across the three sizes, all misses, none correct. About 15 s per life.

**Cost.** Pilot 72 lives, full 768 lives, 4 workers; timing recorded at the pilot.

## Summary
PENDING (after the run)

## Reflection
PENDING (after the run)
