# EXP-07h: does the episodic memory's lift hold as the number of situations grows, and does it carry anything to a situation it never saw?

- Date: pre-registered 2026-11-17 before any data | Cadence version: 0.101.0 (clone `~/_cadence_study` at `3961509` = origin/main, v0.101.0 plus #350 docs; CPU NumPy loop, numba not installed; BLAS threads pinned to 1 to keep the machine's load moderate) | Program iter: iter60 (generic queue; off the V(S) ladder, which waits on Will-gated CAL-1c)
- Script: `exp/EXP-07h_scale.py` | Evidence: `exp/EXP-07h-3961509.out`, `.json`, `.err`, `.time`; pilot `exp/EXP-07h-pilot-3961509.out`; version check `exp/EXP-07g-3961509-v0.out`, `.json`

## Summary
- Question: EXP-07f and EXP-07g found that `memory_choice=True` lets the brain learn a rule that needs a feature
  and its context combined, on 8 situations, with or without the temporal context in the memory's key, and that
  the actor settings alone do not. A per-situation lookup would explain it. Two things decide whether this is a
  recipe for our learned policies or only for small closed sets: does the lift hold as the number of distinct
  situations grows, at a fixed number of moments per situation; and does it give anything on a situation the brain
  never trained on?
- Setup: F features and C contexts; a situation (f, c) is a 2-hot input over F + C inputs. Every seed's rule is
  t(f, c) = g(f) XOR h(c), with g balanced over the features and h balanced over the contexts, drawn per seed
  (at (4, 2) this is EXP-07b's combination family). Sizes (4, 2), (8, 4), (16, 8): 8, 32, 128 situations, 6, 12,
  24 inputs.
  - Ceiling, exact by construction: pairing the g = 0 with the g = 1 features and the h = 0 with the h = 1 contexts
    tiles the table with quadruples of 4 situations, each an XOR pattern. No sum of input weights with a threshold
    gets all 4 cells of an XOR quadruple right (the two cells it must call 1 and the two it must call 0 have the
    same total weight), so on any union of whole quadruples it gets at most 3/4; "1 if the feature is in g-class 0
    or the context in h-class 0" gets exactly 3/4. The script asserts the tiling and the XOR pattern for every seed,
    and at size 8 the exhaustive integer search (EXP-07b's) also gives 6 of 8.
  - Held-out situations are whole quadruples drawn per seed: none at 8, 1 (4 situations) at 32, 4 (16 situations)
    at 128. So the trained set's ceiling is exactly 3/4, every held-out feature and context still appears in
    training, and held-out targets are half 1 and half 0: chance is .5, and one answer for every cue scores
    exactly .5. A sum of input weights at its 3/4 optimum would get 3 of 4 cells of each held-out quadruple, so
    .75 is the held-out level an additive fit could reach.
  - Training through `live` (EXP-07g's moment helper and refusal contract, unchanged): each moment draws a trained
    situation uniformly, the outcome is +1 right / -1 wrong, given with the next moment. Budget = PER_SIT moments
    per trained situation on average (8, 28, 112 trained situations). Greedy exam of every situation (trained and
    held out), each cue on a fresh deepcopy with `act(greedy=True)`, at 25%, 50% and 100% of the budget.
  - Seeds: 10 per size (brain seed, rule, tiling, held-out draw and cue stream all from 7_080_000 + 100 x size
    index + s), the same stream in every arm.
  - Arms, each `Brain.compose(inputs=F + C, actions=2, arousal=True, seed=...)` plus: FOUNDER nothing (control);
    MEM `memory_choice=True`; MEMCTX0 `memory_choice=True, memory_context=0.0`. Settings are read back after the
    runs (eta, bias, memory on, the memory's context share).
  - Version: 0.101.0 composes the 0.95.0 and 0.97.0 default changes (recall memory in every new brain, backend
    auto, history_decays (0.0,), memory_rate 0.2), so the founder and MEM here are not the 0.94.0 brains of
    EXP-07g. The API smoke run (30 moments of one seed per arm and size, no scores) passed on 0.101.0: all three
    arms compose, train and answer at all three sizes; `memory_context` still composes (read back 0.5 for MEM,
    0.0 for MEMCTX0, from the memory's `share`).
  - V0 version check (reported, not a gate): EXP-07g's script, unchanged, rerun on 0.101.0 (TAG 3961509-v0); per
    arm, are its answers identical to the 0.94.0 rerun (`exp/EXP-07g-4cb9c29-rerun.json`) at every exam, and do its
    verdicts hold? Its memory_context read-back prints None on 0.101.0 because the attribute moved; EXP-07h reads it.
  - Budget rule, fixed before the pilot: the pilot times one MEM life at size 128 for 2,000 moments in chunks of
    500 plus one exam of 128 cues, and prints timings only, no scores. Projected wall = sum over sizes and arms of
    10 x (moments x the slowest chunk's seconds per moment + 3 x cues x exam seconds per cue), MEM's rate applied to
    every arm. PER_SIT = 100 if the projection at 100 is at most 45 minutes, else 50.
- Prediction (written before any data):
  - FOUNDER FAILS at all three sizes (at most 2 of 10 seeds above 3/4), as A0 did on 0.93.1. Moderate confidence:
    the risk is the 0.95.0 recall memory now in every brain, which EXP-07f's founder did not have.
  - MEM and MEMCTX0 LEARN at 8 and at 32 (at least 7 of 10 above 3/4). At 128 I lean LEARNS for both, low
    confidence (about 55%): the risks are 0.97.0's memory_rate 0.2, a cap on kept records, and keys of 2-hot
    inputs that share a feature or a context with 22 other situations at 128.
  - Held out: no arm above chance by more than 2 SEM at 32 or 128 (a lookup, and a similarity-weighted recall whose
    neighbours under an XOR rule are half right and half wrong, both predict chance).
  - Pre-registered rules, per arm and size, at the full budget: LEARNS if at least 7 of 10 seeds score above 3/4 on
    the trained situations; PARTIAL if 3 to 6; FAILS if at most 2. Readings:
    - Scaling: an arm that LEARNS at all three sizes keeps the lift as situations grow to 128 at a fixed budget per
      situation; an arm that LEARNS at 8 and not at 128 does not, and the size where it breaks is reported.
    - Carry-over: per arm at 32 and 128, held-out mean over seeds with its SEM. Above .5 + 2 SEM means something
      carries to unseen situations; above .75 + 2 SEM means more than an additive fit could carry; within .5 +- 2
      SEM is consistent with a lookup (not a proof of one); below .5 - 2 SEM is reported as such.
    - Loop verdict on the prediction: CONFIRMED if FOUNDER FAILS at all three sizes, MEM and MEMCTX0 LEARN at all
      three, and no arm's held-out mean is above .5 + 2 SEM; REFUTED if any part reads otherwise (named).
    - VOID if any arm errors or refuses beyond the 5-try contract.
    - Reported with them: trained mean with SEM, seeds at all right, one-answer seeds, the curve at 25% and 50%
      (registered secondary), and the fewest and most visits any trained situation got.
- Result: PENDING
- Verdict: PENDING

## Reflection
- What it means: PENDING
- Process: PENDING
- Lesson: PENDING
- Next: PENDING
