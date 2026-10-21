# EXP-69b: does EXP-69's salience-mark result hold at lateral 0.0 (0.85's proposed default)?

- Date: pre-registered 2026-10-21 (Will's go 2026-10-21, "1. go"), before any EXP-69b data | Cadence version: to run on the 0.85 release (record the SHA and `__version__` at run time); the code gate compares against `be372b8` | Program iter: at run time
- Script: `exp/EXP-69b_salience_mark_lateral0.py` (imports EXP-69's script unchanged and overrides only `lateral`, seeds and file names) | Evidence: `exp/EXP-69b-check.out`, `exp/EXP-69b-full.*`

## Pre-registration (written 2026-10-21, before any EXP-69b data)

**In one line: EXP-69 found that marking a miss with `salience=` rescues about three quarters of a small cost's harm on the reward-only hidden chain, with a residual of about .12. Does that still hold when the motor `lateral` is 0.0, the value upstream #220 proposes as the new default?**

**Why.** EXP-67, EXP-68 and EXP-69 all ran with `lateral=-0.5`: EXP-67/68 through the unset default, EXP-69 pinned explicitly. On 2026-10-21 Bernhard's #220 reading recommended resolving an unset `lateral` to 0.0 throughout, with -0.5 kept as an explicit option. In his chain chamber at -0.5, 4.0% of acts fell to the damped fallback, and none of the readings he reported moved at 0.0 (his chambers and seeds; he didn't measure a reward-only learner under a per-miss cost). Our comments on #202 and #210, and the scope note on the docs line in `docs/episodic.md:166-173`, report numbers measured at -0.5. Once 0.85 ships, a reader of those docs runs at 0.0. So the result has to be re-measured where readers will actually be.

**What could differ, and what can't (read before designing).** `lateral` shapes the motor settle. None of the functions that carry EXP-69's mechanism reads it: `_replay` (3189), `_record_outcome` (3135), `_received` (3126), `_remember` (3415) and `_extend_paths` (3098) never mention `lateral`, and neither does `memory.py` (checked by AST source segments at `be372b8`, 2026-10-21). The replay rule credits success backwards only through steps whose own reward is exactly 0.0 (3223). A marked miss becomes a known outcome written at value 0 (3153-3160). So the replay half of EXP-69's mechanism should carry over by construction, and the check tests it again. What can differ is everything the settle feeds: how often the chain is solved, how many misses each life makes, and so how many zero-valued writes the residual harm comes from. The design therefore re-measures all three readings rather than assuming any of them.

**Setup (pinned).** Everything is EXP-69's setup (see `EXP-69.md`) except three things.
- `lateral=0.0`, set explicitly, so the result doesn't depend on what the release's default turns out to be. The check reports whether explicit 0.0 equals unset on the release; True means the release resolves unset to 0.0 for this chamber.
- Fresh seeds 69_500 + i, and check seed 69_995. No script in `exp/` used 69_500-69_599 or 69_995 (checked 2026-10-21 with `grep -rnE "\b69_?(5[0-9]{2}|99[5-9])\b" --include=*.py`, no hits).
- It runs on the 0.85 release, whatever commit is tagged.

The arms are EXP-69's, paired by seed: `ctx5` (no cost, no mark; 96 lives), `pen@.005` (every non-terminal miss pays -.005; 48), `sal@.005` (every non-terminal miss pays 0 and carries `salience=.005`; 96), and `sal@1` (the same mark at salience 1; 48). Hidden chain, natural signal, 120 training attempts, readings on a saved copy as in EXP-69. In total, 288 lives.

**Primary reading.** Sampled success, delta vs ctx5 paired by seed, with the paired SEM and the 95% interval. The rescue contrast is sal@.005 minus pen@.005, on seeds 0..47. Also reported, as in EXP-69: sal@1, clean greedy passes, training success, first-try accuracy by stage, misses / marks / marked writes per life, and replay stops at successes.

**Check (`MODE=check`, seed 69_995, on the release, before the full run; a failure stops it).**
- (gate) The functions EXP-69's pre-registration read (`step`, `learn`, `_received`, `_extend_paths`, `_record_outcome`, `_remember` and `_replay` in `generic.py`, plus the whole of `memory.py`) are AST-identical to `be372b8` with docstrings stripped. If not, the run stops: the code reading is redone and EXP-69b is re-registered before any data.
- (info) Whether explicit `lateral=0.0` equals unset on the release, for ctx5 and pen@.005.
- (b) `sal@0` is identical to ctx5, and nothing is written for its misses.
- (c) At sal@.005 and sal@1, every non-terminal miss is marked and written, no nonzero miss reward reaches the memory, and replay never stops at a miss.
- (d) At pen@.005, the memory sees the cost, and replay stops at a charged miss at least once.
- (time) Seconds per life. If the full run projects past 30 min at 4 workers, only seeds 0..47 of every arm run, as a pilot under the same rules.

**Predictions (written before any data).**
- The check passes: about 85%. The main risk is the gate: 0.85 may touch `step` or the memory for reasons unrelated to this question, which would force a re-registration, not a result.
- (P0) pen@.005 is below ctx5 by at least 2 SEM at 0.0: about 85%. The harm runs through the replay rule, which `lateral` doesn't touch.
- Rescue: sal@.005 is above pen@.005 by at least 2 SEM: about 85%. EXP-69 had 6.0 SEM.
- The residual repeats: sal@.005 is below ctx5 by 2 SEM or more: about 55%. EXP-69 had 2.65 SEM at the same size, so even if the true gap is the same, a replication reaches 2 SEM only about three times in four, and the settle change may move the miss count.
- Verdict odds: HOLDS about 45%, SAFE SWAP about 25%, NO RESCUE about 5%, NO COST HARM AT 0.0 about 10%, VOID about 15%.
- sal@1 vs sal@.005: no prediction (EXP-69 +.006).

**Decision rules (written before any data).**
- VOID: the check fails, including the code gate. No data is run, and the experiment is re-registered on the release.
- NO COST HARM AT 0.0: P0 fails (pen@.005 is not below ctx5 by 2 SEM). That is a finding, not a void: the cost harm we reported on #210 and #202 would then need scoping to `lateral=-0.5`, and upstream should hear that.
- HOLDS (EXP-69's PARTIAL carries over): P0 holds, the rescue holds, and sal@.005 is below ctx5 by at least 2 SEM.
- SAFE SWAP AT 0.0: P0 and the rescue hold, and sal@.005 is not below ctx5 by 2 SEM. The residual isn't detected at 0.0, bounded by its 95% interval. That is not proof it's gone, since EXP-69 itself sat at only 2.65 SEM.
- NO RESCUE: P0 holds and the rescue fails.
- Reported with every verdict: each arm's delta and 95% interval next to EXP-69's (different seeds, so compared as two independent estimates, not paired).
Loop verdict: HOLDS -> CONFIRMED (replication); SAFE SWAP AT 0.0 -> INCONCLUSIVE; NO RESCUE -> REFUTED; NO COST HARM AT 0.0 -> BOUNDARY; VOID -> VOID.

**Power.** The same sizes as EXP-69 (paired SEMs .046 to .068 there). The rescue (+.28 in EXP-69) is well powered. A residual of about .12 sits near 2.6 SEM at 96 lives, so it is detected about three times in four. That is why a SAFE SWAP at 0.0 reads as "not detected", bounded by its interval.

**Cost and trigger.** 288 lives, about 17 min at 4 workers (EXP-69 took 1,030 s). Trigger: the day 0.85 is tagged. The monitor loop fast-forwards `~/_cadence_study`, reruns EXP-08 with `lateral=-0.5` explicit (the queued re-baseline), and then this check and run follow. It is not run before the release, because 0.85 may bundle other changes (#220 says the lateral change is "read with the other 0.85 candidates").

## Result
PENDING (runs on the 0.85 release).

## Summary
PENDING.

## Reflection
PENDING.
