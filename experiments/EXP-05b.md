# EXP-05b: is a mid-stream snapshot of a learning brain a byte-identical continuation? (EXP-05 redone on a task that keeps the brain choosing)

- Date: pre-registered 2026-10-29, before any EXP-05b data | Cadence version: 0.91.1, main `c9c8080` (tag v0.91.1), editable clone `~/_cadence_study`, re-read and printed at run time | Program iter: none. This is a library and tooling test, off the V(S) ladder. The V(S) program is waiting on three decisions only Will can make (CAL-1, CAL-2, the registered zero test), so the loop took the best ready queue item.
- Script: `exp/EXP-05b_snapshot_restore.py` | Evidence (to be written): `exp/EXP-05b-pilot.out`, `exp/EXP-05b-pilot.json` (pilot, already run), `exp/EXP-05b-check.out`, `exp/EXP-05b-check.json`, `exp/EXP-05b-full.out`, `exp/EXP-05b-full.json`. Checkpoints and per-process traces stay in the git-ignored `exp/EXP-05b_brains/`.

## Pre-registration (written 2026-10-29, before any EXP-05b check or data life)

**In one line: save a learning brain in the middle of its life and load it in a new Python process. Does it then act and learn exactly, bit for bit, as the brain that was never stopped? And does a `copy.deepcopy` fork do the same? Asked on a task where the brain keeps choosing different actions after every cut and wakes at the reversal.**

**What a yes allows.** Same as EXP-05: a saved brain is a safe hand-off point (stop, move and resume a live brain with nothing lost, even while an action waits for its outcome), and our harnesses can fork twins with `deepcopy` instead of a file round trip.

**Why redo it, and why now.**
- EXP-05 (2026-10-23, Cadence 0.85.1 + 41 commits) stopped at its own check k4, before any data. After youth its brains answered every cue with one fixed action. A continuation that repeats one action matches the reference almost by default, so after 6 of its 14 cuts a match would have proved little. Its brains also never woke at the reversal, so the two reversal cuts (A5, A6) never happened. Its one check life was consistent with exact continuation, but a check life is not a reading.
- Eight releases have shipped since then (0.86.0 to 0.91.1). Several of them changed what a saved brain carries or how it is rebuilt:
  - 0.91.1 (today) added a recall cache: "Reuse raw recall content products while applying the current temperature on every read. Check a bitwise key snapshot before reuse, so runtime retuning, in-place expert edits and checkpoint continuation agree. Bound the cache to one bank and four addresses per head." If that cache is not saved, a loaded brain starts with it empty while the uninterrupted brain has it warm. A byte-identity test is the direct way to see whether that ever changes a result. (Whether this configuration reaches the cache is checked before the run, below.)
  - 0.91.1 also validates apical checkpoints on load: "Validate original apical checkpoint types and both topology arrays before construction ... Valid checkpoints retain exact continuation."
  - 0.91.1, for the learned code: "Restore the previous code step and phase when an enclosing action, prediction, wait, lesson or feedback operation refuses. Validate feedback before preparing the next code."
  - 0.90.0 added the apical compartment and its checkpoint format `cadence-checkpoint/5`.
  - 0.89.0 turned the recall position term on by default. Read on the three composed brains before registration (pilot seed 0): `recall.position` 32, 33 buckets, one position map each. So all three brains have this state. Whether `save` writes all of it is part of what this test checks.
- What the docs promise (read at `c9c8080`): `docs/start.md` "`save` and `load` keep the brain's full continuation, pending feedback included"; `docs/api.md` `last_arousal` "`None` after construction, reset or load"; 0.91.1 CHANGELOG "Valid checkpoints retain exact continuation". A mismatch anywhere else is an upstream bug.

**Changes from EXP-05 (as queued 2026-10-23, plus one brain).**
1. `last_arousal` is recorded and compared only at `live` events (L and E). At `wait` and `reset` events the field is written as the constant "not compared". Reason: the docs clear it on load and `wait` does not set it; EXP-05's diagnosis isolated exactly that field at a `wait` after a load.
2. The task is chosen by a behaviour pilot (below), so that every cut type occurs and every cut is followed by at least two distinct actions.
3. Fresh seeds: brain `9_055_000 + i`, environment `9_055_200 + i`, data lives i = 0, 1, 2, check life i = 99. Pilot seeds `9_056_000 + i` / `9_056_200 + i`, i = 0..3, are never data. No script in `exp/` used 9_055_xxx or 9_056_xxx before this one (checked 2026-10-29 with `grep -rnE "\b9_?05[5-6]_?[0-9]{3}\b" --include=*.py`: no hits).
4. A third brain is added: two regions with the apical compartment (`modules=(16, 8), apical=0.25`), the composition 0.90.0 introduced and 0.91.1 now validates on load. The plain and learned-code brains are EXP-05's.
5. Check gate k1 requires all 9 cut types on the check life (EXP-05 allowed 7 of 9); k5 allows 15 minutes of projected full run (three brains instead of two).

**Before registration (disclosed; none of it compares a restore or a fork).**
- API probe (seed 1, outside every registered range): all three brains compose with `lateral=0.0, arousal=True, memory_choice=True, recall=True`, live 51 moments, save and load on 0.91.1. About 10 / 24 / 16 ms per moment (plain / learned code / apical).
- Behaviour pilot (`MODE=pilot`, `exp/EXP-05b-pilot.out` and `.json`): the reference life only, in one process, no save, no comparison, pilot seeds, 4 lives x 3 brains x 4 candidate tasks, 69 s. The candidates, all on EXP-05's schedule (300 moments, waits, resets at 100 / 175 / 250, reversal at 200, salience 0.5 on unpaid outcomes):
  - T0, EXP-05's task (paid 1, unpaid 0, founder genes). It fails the same way on 0.91.1. The reversal cuts A5 and A6 never happen, on 12 of 12 lives. After youth the brains are almost never aroused (1 to 3 moments, on 3 of the 12 lives). Only 5 of 12 lives have at least 2 distinct actions after every cut.
  - T1, paid +1, unpaid -1, founder genes; T2, the same plus the docs' `live` example operating point (`consolidation=0.25, actor_eta=0.1, actor_eta_bias=0.01`, docs/start.md "Routine and repair"). Both learn the map: accuracy over moments 100-199 is 1.00 on 12 of 12 T2 lives and .70 to 1.00 on T1. But no brain wakes at the reversal: 0 aroused moments after youth on 24 of 24 lives. Accuracy over moments 200-299 is 0.00 on 12 of 12 T2 lives and 0.00 to .26 on T1. A5 and A6 never happen.
  - T3, T2 plus `arousal_need=0.5`. All 9 cut types on 12 of 12 lives; every cut followed by at least 2 distinct actions on 12 of 12; 39 or 40 aroused moments in 200-249 on every life; accuracy 100-199 1.00 and 200-299 .56 to .78. The only cut never followed by an aroused moment is B3 (the `reset(keep=("slots",))` at 250): on every pilot life the brain stays calm for its last 50 moments.
  - **T3 is chosen** by the rule written in the queue before the pilot (every cut type occurs, every cut followed by at least 2 distinct actions, A5 and A6 occur). It was the only candidate that met it.
- Side observation (pilot T2, plain brain, life 0, one life, read from `last_arousal` after the pilot): at the reversal the brain's error rises to about 1.9 and surprise fires briefly (.38 at moment 202, .23 at 203), but the level peaks at .07 against the 0.2 threshold, and want stays exactly 0 for all 100 punished moments. Consistent with the documented law: the `reset(keep=("slots",))` at moment 100 cleared the reward scale, a calm brain learns no outcome so the scale stays empty, and the income want has a zero denominator. The docs warn that "a world that stops paying may leave it calm on a lapsed habit"; here the world punishes (-1) and the brain still stays calm. Not part of this experiment's question; queued as a separate candidate (EXP-05c), no claim.

**Setup (pinned).**
- Cadence main `c9c8080` (`__version__` 0.91.1), editable install. Python 3.12.10, NumPy 2.4.2, numba and torch not installed (re-read and printed at run time). `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS` set to 1 for every process (printed).
- Three brains, each `Brain.compose(6, 3, seed=s, lateral=0.0, arousal=True, memory_choice=True, recall=True, consolidation=0.25, actor_eta=0.1, actor_eta_bias=0.01, arousal_need=0.5, ...)` with: plain `modules=(16,)`; code `modules=(16,), learned_code=16`; apical `modules=(16, 8), apical=0.25`. Every other gene is the library default; the check prints `describe()["genes"]` and `describe()["layout"]["composition"]` for each.
- Task T3, otherwise EXP-05's schedule exactly: 6 inputs (cues 0..3 one-hot, a wait frame at index 4, an end frame at index 5), 3 actions, 300 moments; the cue at each moment drawn once from the environment seed. The paying action for cue c is `c % 3` before moment 200 and `(c + 1) % 3` from moment 200. The outcome of the action issued at moment m is reported at the next `live`: reward +1.0 if it paid, else -1.0 with `salience=[0.5]`, always with `decision_id` set to the id read when the action was issued. After the `live` of moment m, 0, 1 or 2 wait frames (probabilities .7 / .2 / .1, from the environment seed) are sensed with `wait`. Episodes end at moments 100, 175 and 250: the pending outcome is reported on the end frame with `done=[True]`, the action that call issues is dropped, the brain is reset (`reset(keep=("slots",))` at 100 and 250, the default `reset()` at 175, which keeps the arousal), and moment m starts with `live(cue)` and no reward. The life ends right after the `live` of moment 299, with an action pending.
- Trace, cuts, processes, arms and readings: exactly EXP-05's (experiments/EXP-05.md, Setup and Arms), with change 1 above. Cuts, chosen by rule from the reference trace before any restore: A1 the `live` of moment 40 (youth, sampled action pending); A2 the first `wait` at 60..99; A3 the first routine `live` at 130..174; A4 the first `wait` at 130..174 under a routine action; A5 the first aroused `live` at 200..249; A6 the first `wait` at 200..249 under an aroused action; B1 / B2 / B3 right after the resets at 100 / 175 / 250. Processes: R and R2 (the uninterrupted life twice, hash seeds 1 and 2); P1 (the life saving at every cut and living on, A0); P2 per cut (load in a fresh process, continue, save at the end; a separate load saved at once gives the round trip); F per cut (live to the cut, fork D = deepcopy, S = save/load, X = deepcopy fed shifted cues and paid for its own actions; O, D, S, X run interleaved to the end). At most 4 subprocesses at once.
- Added reading (no rule): aroused `live` moments in the reference after each cut, so a reader can see which continuations exercised the learning path after the restore (from the pilot, B3's will be 0).

**Check (`MODE=check TASK=T3`, life 99, all three brains, before the data lives; a failure stops the run).**
- (k1) All 9 cut types are available on each brain, and each cut saved the groups its type requires (EXP-05's table: A1 / A5 `pending/` and `lived` sampled; A3 `lived` not sampled, no `pending/`; A2 / A4 / A6 also `awaiting`; B1..B3 none of them).
- (k2) R and R2 agree exactly (trace and final bytes).
- (k3) A restore at the first available of A3, A1 that adds 1e-9 to the first reward it reports is flagged; the member digest moves when one float in a copy of a cut checkpoint moves by one ULP.
- (k4) Every cut's checkpoint bytes differ from the final bytes, and R's events after every cut contain at least two distinct actions.
- (k5) The projected full run at 4 workers is at most 15 minutes; otherwise the data lives are cut to i = 0, 1 and the missing life is recorded as owed.
- As in EXP-05, identity comparisons on the check life are printed with the check and count in the verdict, flagged as the check life; only k1 to k5 stop the run.

**Predictions (written before any check or data).**
- The check passes: about 85% (the pilot already shows the cut types and the action variety; the remaining risks are the harness on the third brain and the timing gate).
- R equals R2 on every life: about 97%. A0 (saving does not perturb the life): about 95%.
- Arm A holds at every pending cut on all three brains: about 75%. First suspect if it breaks: 0.91.1's recall content cache (a restored brain starts it cold); second, the apical brain's new checkpoint path; third, the learned code.
- Arm B holds at every reset cut: about 85%.
- Arm C: the deepcopy fork matches the reference at every cut about 85%; the save/load fork about 80% (if the cache matters, I expect S to differ while D, which copies the brain object whole, matches); X differs from R about 99%.
- All three arms hold: about 60%.
- The round trip (load then save at once gives the cut file's bytes): about 90% (14 of 14 in EXP-05's check).
- The brain learns the pre-reversal map (accuracy 100-199 at least .9) on every data life and brain: about 85%. No rule attaches to it.

**Decision rules (written before any check or data; EXP-05's, unchanged).**
- VOID (whole experiment): the check fails (no data run), or R differs from R2 on any data life.
- Arm A CONFIRMED: A0 holds on every life, and at every available A cut on every life (3 data lives and the check life, 3 brains), P2's continuation equals R event for event and its final checkpoint has R's bytes. REFUTED: any difference, or a load or a continuing call that raises. INCONCLUSIVE: no difference, but some A cut type unavailable on every life of a brain (named).
- Arm B: the same rules at B1..B3.
- Arm C CONFIRMED: at every cut on every life, O, D and S each equal R after the cut and end on R's bytes, the fork-time checkpoints of O, D and S have the same bytes, and X differs from R. REFUTED: any of O, D, S differs (naming which). INCONCLUSIVE: no difference but X equal to R somewhere.
- A mismatch is followed to its first differing event and, at the end, to the checkpoint members that differ; the member digest says whether bytes differ with equal members (encoding) or the members differ (state).
- Overall: all three arms CONFIRMED -> SUPPORTIVE (loop CONFIRMED). Any arm REFUTED -> BOUNDARY if another arm is CONFIRMED, NULL if none is (loop REFUTED either way). No arm refuted but one INCONCLUSIVE -> SUPPORTIVE with the gap named (loop INCONCLUSIVE).
- A refutation where the docs promise an exact continuation gets a minimal reproduction for Will at `Desktop/Cadence/cadence-pr-draft-2026-10-29-snapshot-<slug>.md`; nothing is filed or posted.

**Cost.** Pilot reference lives took about 3 / 8 / 6 s (plain / code / apical). Each brain-life is about 30 life-lengths of events, so about 4 to 5 minutes per life serially for the three brains together, about 1.5 to 2.5 minutes at 4 workers; the check plus three data lives about 6 to 10 minutes.

## Check
- PENDING

## Summary
- PENDING

## Reflection
- PENDING
