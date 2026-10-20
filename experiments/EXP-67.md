# EXP-67: can any failure cost help a learner with no teacher, or does it make the learner timid at every size?

- Date: pre-registered 2026-10-20 (Will un-gated 2026-10-20 05:01; off-program, memory track, upstream #202), before any EXP-67 data | Cadence version: 0.84.3 (`8dc92d8`), record at run time | Program iter: none
- Script: `exp/EXP-67_reward_only_penalty.py` (imports EXP-66, so the chambers, brain, gate, readings and the per-miss penalty are EXP-66's code) | Evidence: `exp/EXP-67-check.out`, `exp/EXP-67-full.*`

## Pre-registration (written 2026-10-20, before any EXP-67 data)

**In one line: does a cost for failing teach a learner with no teacher, at any size, or in a form that charges for repeating a mistake instead of for exploring?**

**Why.** EXP-66 found that a small cost per miss (p = .05), with the gate keyed on it, helps a learner that also has a corrective teacher. Without a teacher it hurt. Under reward alone, sampled success fell on every chain: hidden .365 to .076, invisible .141 to .080, visible .876 to .597. Clean greedy passes were 1 / 0 / 0 / 0 across the four arms. EXP-66 tested one size and one form of the cost, so it cannot say whether the harm is a property of failure costs in general or of that size and form. EXP-67 tests smaller sizes and a gentler form, under reward alone.

**Setup.** EXP-66 exactly, with three changes. First, **natural signal only**: world reward, no teacher. Second, fresh seeds 67_000 + i; no script in `exp/` uses 67_000-67_999 (checked by grep). Third, the life counts per arm: 36 on the invisible chain, 36 on the hidden chain, 24 on the visible chain. Brain, chambers (10 decisions per attempt, +2 / -1 terminal), 120 attempts, gate rule and readings on a saved copy with the plain context: all EXP-66's code. Arms are paired by seed (same brain initialisation).

Arms (13):
- `ctx5`: no cost, no gate (the base).
- `out5t`: no cost, EXP-63's oracle gate during training (completes EXP-66's two-by-two; reported only).
- `pen@p` for p in {.005, .01, .02, .05}: every non-terminal miss pays -p instead of 0, no gate. The .05 arm repeats EXP-66's size on fresh seeds (the precondition below).
- `peng@p` for p in {.005, .01, .02}: the same cost, with the gate keyed on reward < 0 (EXP-66's `peng`).
- `penr@p` for p in {.005, .01, .02, .05}: the gentler form. Within an attempt, the first miss at a stage is free and only a repeat miss at the same stage pays -p. No gate. It charges for repeating a mistake, not for exploring. Terminal rewards are unchanged in every arm.

**Primary reading: sampled success** (100 sampled attempts on the saved copy), because under reward alone clean greedy passes were near zero in EXP-66 and cannot separate arms. For each arm and chain: Delta = sampled(arm) - sampled(ctx5), paired by seed, with the paired SEM. Also reported: clean greedy passes with exact McNemar against ctx5, first-try accuracy by stage, the stage-1 AUC of the learner's forecast error, held counts for the gated arms, and penr@p - pen@p paired at each shared p.

**Check (`MODE=check`, before the full run; a failure stops it).** (a) At p = 0 every penalised arm (pen, peng, penr) gives a life identical to ctx5 (invisible chain, natural, seed 67_990). (b) At p = .02 on that seed, penr charges exactly the repeat misses: charged = misses minus first misses per (attempt, stage), and pen charges every non-terminal miss. (c) This script's `pen` life at p = .05 equals EXP-66's `life()` on the same seed.

**Predictions (written before any data).**
- (P0, precondition) The timidity replicates: pen@.05 on the hidden chain has Delta at or below -2 SEM. About 85%.
- Some arm helps (the HELPS rule below): about 20%.
- pen@.005 on the hidden chain is still harmful at 2 SEM: about 40%.
- penr is less harmful than pen at the same size (penr - pen > 0 on the hidden chain at .02 and at .05): about 65%.
- No prediction for out5t under reward alone.

**Decision rules (written before any data).** 11 penalised arms x 2 chains (invisible, hidden) give 22 chances to "help", so the bar for help is 3 SEM, not 2.
- HELPS (SUPPORTIVE): some penalised arm has Delta of at least +3 SEM on the invisible or the hidden chain, and that same arm's Delta on the visible chain is not below -2 SEM. For #202, a failure cost of that size and form helps even without a teacher.
- TIMID AT EVERY SIZE (BOUNDARY): no arm helps, and pen@.005 (the smallest per-miss cost) on the hidden chain has Delta at or below -2 SEM. The per-miss cost hurts a teacherless learner at every size tested.
- NULL: no arm helps, and pen@.005 on the hidden chain is within 2 SEM of zero. A cost small enough to be harmless is too small to help.
- Reported with each verdict: whether penr removes the harm at the sizes where pen has it.
- P0 fails: the verdict is reported, but read in the light that EXP-66's timidity did not replicate on fresh seeds.
Loop verdict: SUPPORTIVE -> CONFIRMED; BOUNDARY -> INCONCLUSIVE; NULL -> REFUTED.

**Cost.** 13 arms x 96 lives = 1,248 lives. EXP-66 measured about 15 s per life, so about 80 min at 4 workers.

## Check
- 2026-10-20 05:23, `exp/EXP-67-check.out`, Cadence 0.84.3, seed 67_990, invisible chain, natural: **PASS.** (a) pen, peng and penr at p = 0 are identical to ctx5. (b) At p = .02 penr charged exactly the repeat misses (773 of 939 non-terminal misses; 166 were the first miss at a stage in their attempt) and pen charged all 941. (c) pen at .05 through this script equals EXP-66's own `life()`.
- What (b) says about the design, before any outcome: because a wrong action changes nothing, a learner stuck at a stage repeats its miss, so most misses are repeats. On this life the repeat-only form waives about 18% of the charges, not most of them. penr is a gentler form, but only mildly gentler. Nothing in the design changed.

## Summary
- PENDING.

## Reflection
- PENDING.
