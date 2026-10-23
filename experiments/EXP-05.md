# EXP-05: is a mid-stream snapshot of a learning brain a byte-identical continuation?

- Date: pre-registered 2026-10-23, before any EXP-05 data | Cadence version: 0.85.1 + 41 commits, main `4ac887c` (`git describe` v0.85.1-41-g4ac887c, `__version__` 0.85.1), editable clone `~/_cadence_study`, re-read at run time | Program iter: iter46 (off the V(S) ladder; library & tooling)
- Script: `exp/EXP-05_snapshot_restore.py` | Evidence: `exp/EXP-05-check.out`, `exp/EXP-05-check.json`, `exp/EXP-05-check-diagnosis.out` (no full run: VOID by the check; the registered `exp/EXP-05-full.*` files do not exist). Checkpoints and per-process traces stay in the git-ignored `exp/EXP-05_brains/`.

## Pre-registration (written 2026-10-23, before any EXP-05 data)

**In one line: save a learning brain in the middle of its life and load it in a new Python process. Does it then act and learn exactly, bit for bit, as the brain that was never stopped? And does a copy made with `copy.deepcopy` do the same?**

**What a yes allows.** A saved brain is a safe hand-off point: a live brain can be stopped, moved and resumed with nothing lost, even while an action is still waiting for its outcome. And our experiments can fork twins with `deepcopy` instead of writing and reading a file each time.

**Why.** Queue item EXP-05 (the portable-mind property, the one property of [[portable-swappable-jarvis-mind]] we call demonstrated). Three upstream changes make it worth testing now. 0.85.1: "A pending-action checkpoint must carry its decision-time observation, action and learned code where applicable. Missing records now raise on load rather than silently losing the action's associative-memory write." 0.85.0: "A checkpoint saved immediately after `reset(keep="slots")` loads its retained recall rows even though the reset cleared the current neural state" (so this boundary lost state before 0.85.0), and "`copy.deepcopy(brain)` works". Our own harnesses fork twins through save/load, and the 2026-10-22 integration note recommends `deepcopy` for new fork-heavy experiments only after a byte-identity check against save/load. This is that check.

**What the docs promise (read at `4ac887c`).** `docs/start.md` (Imagine privately and resume): "`save` and `load` keep the brain's full continuation, pending feedback included." `docs/api.md`: `save` / `Brain.load` "The whole continuation, written atomically"; `copy.deepcopy(brain)` "An independent copy: every array, store, state and random generator copied, the immutable connectomes shared." `docs/contracts.md`: "save every one needed for an exact continuation". Upstream's own tests compare checkpoints member by member (`assert_same_checkpoint`) and in one place byte for byte (`tests/test_learned_code.py:904,917`). So an exact continuation is promised, and a mismatch would be an upstream bug.

**What the code says (read before designing; `src/cadence/generic.py` unless named).**
- `pending_feedback` (1887) is true for a sampled pending action (`basal_ganglia._pending`) and for a calm `live` action (`_lived` with `sampled` false, whose `lived[4]` must be the very object `basal_ganglia.state`). `live` (3277-3279) treats a calm action as pending only under that identity, so a calm pending action survives a save only if `load` re-links it (4493-4503 does: `lived[4] = agent._free`). That is the code path I trust least.
- `save` (4052) writes `lived/` (the issued action, its observation and, with a learned code, its decision-time code), `awaiting/` (what `wait` sensed), `pending/` (a sampled action's phases), every memory, both random generators and the arousal. The learned code's running step (`halvings`) is saved as `stepping` (`code.py:667`).
- Raw checkpoint bytes are a fair digest: `np.savez_compressed` opens every member with `ZipInfo(name)`, whose date is fixed at 1980-01-01 (Python 3.12 `zipfile.ZipFile.open`), so two saves of the same state are the same bytes. A second digest over the members (name, dtype, shape, data bytes, sorted by name) is kept to tell an encoding difference from a state difference.

**Before registration (disclosed).** One API and timing probe ran (`exp/EXP-05_brains/probe.py`, seed 1, not in the registered range): no save, no load, no comparison. It measured 7.5 ms per moment for the plain brain and 19 ms with the learned code, and showed `pending_feedback` true after every `live` (calm and aroused) and false after `reset(keep=("slots",))`. No other run preceded this file.

**Setup (pinned).**
- Cadence main `4ac887c` (`__version__` 0.85.1), imported from the editable install. Python 3.12.10, NumPy 2.4.2 (re-read and printed at run time).
- Two brains, each `Brain.compose(6, 3, modules=(16,), seed=s, lateral=0.0, arousal=True, memory_choice=True, recall=True)`; the second adds `learned_code=16`. Every other gene is the library default; the check prints `describe()["genes"]` and `describe()["layout"]["composition"]` in full so each value is on record. `lateral=0.0` is passed although it is the 0.85 founder, so a later default change cannot move this run.
- Seeds: brain `9_005_000 + i`, environment `9_005_200 + i`, data lives i = 0, 1, 2, check life i = 99. No script in `exp/` uses 9_005_000 to 9_005_999 (checked 2026-10-23 by `grep -rnE "\b9_?005_?[0-9]{3}\b" --include=*.py` over the repo: no hits; the largest seed base in `exp/` is 7_590_000).
- Task (one stream, through `live`): 6 inputs (cues 0..3 one-hot, a wait frame at index 4, an end frame at index 5), 3 actions. 300 moments m = 0..299; the cue at each moment is drawn once from the environment seed. The paying action for cue c is `c % 3` before moment 200 and `(c + 1) % 3` from moment 200 (a reversal). The outcome of the action issued at moment m is reported at the next `live`: reward 1.0 if it paid, else 0.0 with `salience=[0.5]` (0.85.1's `live` mark), always with `decision_id` set to the id read when the action was issued. After the `live` of moment m, 0, 1 or 2 wait frames (probabilities .7 / .2 / .1, drawn from the environment seed) are sensed with `wait`. Episodes end at moments 100, 175 and 250: the pending outcome is reported on the end frame with `done=[True]`, the action that call issues is dropped, the brain is reset, and moment m starts with `live(cue)` and no reward. The resets are `reset(keep=("slots",))` at 100 and 250 and the default `reset()` (keeps the arousal) at 175. The life ends right after the `live` of moment 299, with an action pending.
- Trace: every event (live, wait, end, reset) records, exactly, the returned action, `decision_id`, `pending_feedback`, `last_arousal` (every field) and `last_settlement` (every field), floats as `float.hex`. Final digest: SHA-256 of the bytes of the checkpoint saved after the last event, plus the member digest.
- Cuts, chosen by rule from the reference trace before any restore:
  - A1, youth, right after an aroused `live` (sampled action pending): the `live` of moment 40.
  - A2, youth, mid-wait: the first `wait` at moment 60..99.
  - A3, adult, right after a calm `live` (a routine action pending): the first `live` at 130..174 whose mode is routine.
  - A4, adult, mid-wait under a calm action: the first `wait` at 130..174 whose action was routine.
  - A5, after the reversal, right after an aroused `live`: the first `live` at 200..249 whose mode is aroused.
  - A6, after the reversal, mid-wait under an aroused action: the first `wait` at 200..249 whose action was aroused.
  - B1, right after `reset(keep=("slots",))` at 100; B2, right after the default `reset()` at 175; B3, right after `reset(keep=("slots",))` at 250.
  A cut type with no qualifying event in a life is recorded as unavailable for that life.
- Processes (each a fresh `python` subprocess with its own fixed `PYTHONHASHSEED`, so set orders differ between them; at most 4 at once):
  - R, the reference: the whole life, no save until the final one (hash seed 1). R2: the same life again (hash seed 2), the determinism control.
  - P1, snapshot: the whole life, saving a checkpoint plus the environment's state (next event, the pending action, its moment and `decision_id`) right after each cut event, and living on in the same process after every save (hash seed 3). Its full trace and final digest test that a save does not perturb the life (A0).
  - P2 per cut (arms A and B): a fresh process loads the cut checkpoint and the environment state, continues every remaining event with the same inputs, and saves at the end (hash seed 100 + cut). A second, separate load in the same process is saved at once, to read the round trip (load then save) against the cut file's bytes; the continuing brain is never saved before the end.
  - F per cut (arm C): a fresh process lives the brain from moment 0 to the cut, then forks D = `copy.deepcopy(O)`, S = `Brain.load(O.save(...))` and X = `copy.deepcopy(O)`, and runs O, D, S and X to the end, interleaved event by event (hash seed 200 + cut). O, D and S get the reference inputs. X is the diverging twin: it sees cue `(c + 1) % 4` at every `live` and is paid for its own actions, with the same waits, ends and resets. The checkpoints of O, D and S saved at the fork are compared to each other and to P1's cut file.

**Arms and readings.**
- (a) Arm A, pending action: at cuts A1..A6, P2's continuation versus R's events after the cut, and P2's final bytes versus R's. A0 (P1 equals R, trace and final bytes) belongs to this arm.
- (b) Arm B, reset boundary: the same at cuts B1..B3.
- (c) Arm C, forks: at every cut (A1..A6 and B1..B3), O, D and S each versus R's events after the cut and R's final bytes; the fork-time checkpoints of O, D, S and P1 equal; X differs from R (otherwise the independence reading is empty).
- Reported without a rule: the round trip (load then save at once equals the cut file's bytes); P1's cut files versus F's fork-time saves; accuracy by phase, aroused and routine moments, waits, and seconds per process.

**Check (`MODE=check`, life i = 99, both brains, before the data lives; a failure stops the run).**
- (k1) At least 7 of the 9 cut types are available on each brain, and each available cut saved the groups its type requires: A1 and A5 `pending/` arrays and `lived` with sampled true; A3 `lived` with sampled false and no `pending/`; A2, A4 and A6 an `awaiting` record as well; B1..B3 none of `lived`, `pending/` or `awaiting`.
- (k2) Determinism control: R and R2 agree exactly (trace and final bytes). If not, the uninterrupted life is not reproducible across processes and the snapshot question cannot be asked: stop and record it.
- (k3) Sensitivity: one extra restore at the first available of A3, A1 adds 1e-9 to the first reward it reports; the comparison must flag it (trace or final bytes differ). The member digest must change when one float in a copy of a cut checkpoint is moved by one ULP.
- (k4) The state moves: every cut's checkpoint bytes differ from the final bytes, and R's events after every cut contain at least two distinct actions.
- (k5) Printed for the record: the genes, accuracy by phase, aroused / routine moments, waits, seconds per process, and the projected full run at 4 workers. If that projects past 12 minutes, the data lives are cut to i = 0, 1 and the missing life is recorded as owed.
- The identity comparisons on the check life are printed with the check. Because the property is universal (every continuation, not an average), a mismatch on the check life is a counterexample like any other: it counts in the verdict, flagged as the check life. It does not stop the run; only (k1) to (k5) do.

**Predictions (written before any data).**
- The check passes: about 85% (a new harness; most likely failure is a cut type that never occurs, e.g. a brain that never wakes after the reversal).
- R equals R2 on every life: about 97%. A0 (saving does not perturb the life): about 97%.
- Arm A holds at every pending cut on both brains: about 82%. If anything breaks, my first suspect is the calm (routine) pending action (A3, A4) and its object-identity link; second, the learned-code brain.
- Arm B holds at every reset cut: about 85% (0.85.0 just repaired this boundary for `keep="slots"`).
- Arm C: the deepcopy fork matches the reference at every cut about 88%; the save/load fork about 85%; X differs from R about 99%.
- All three arms hold: about 65%.
- The round trip (load then save at once gives the cut file's bytes): about 60% (load may not restore report-like fields such as `last_learning`, which `save` writes). No rule attaches to it.
- Accuracy: the brain learns the pre-reversal map above chance (1/3) by moments 100..199 on most lives: about 70%. No rule attaches to it; it is printed so a reader can see the brain is learning, while (k4) is what guarantees the state moves.

**Decision rules (written before any data).**
- VOID (whole experiment): the check fails (no data run), or R differs from R2 on any data life (the life is not reproducible across processes; recorded as a finding in itself).
- Arm A CONFIRMED: A0 holds on every life, and at every available A cut on every life (3 data lives and the check life, 2 brains), P2's continuation equals R event for event and its final checkpoint has R's bytes. REFUTED: any difference, or a load or a continuing call that raises. INCONCLUSIVE: no difference, but some A cut type was unavailable on every life of a brain (a coverage gap, named).
- Arm B: the same rules at B1..B3.
- Arm C CONFIRMED: at every cut on every life, O, D and S each equal R after the cut and end on R's bytes, the fork-time checkpoints of O, D and S have the same bytes, and X differs from R. REFUTED: any of O, D, S differs (naming which: deepcopy, save/load, or the original beside them). INCONCLUSIVE: no difference but X equal to R somewhere (the independence reading empty there).
- A mismatch that raises a byte-identity failure is followed to its first differing event and, at the end, to the checkpoint members that differ; the member digest says whether bytes differ with equal members (encoding) or the members differ (state).
- Overall: all three arms CONFIRMED -> SUPPORTIVE (loop CONFIRMED). Any arm REFUTED -> BOUNDARY if another arm is CONFIRMED (the property holds on a named part and fails at a named boundary), NULL if no arm is (loop REFUTED either way). No arm refuted but one INCONCLUSIVE -> SUPPORTIVE with the gap named (loop INCONCLUSIVE).
- A refutation where the docs promise an exact continuation gets a minimal reproduction for Will at `Desktop/Cadence/cadence-pr-draft-2026-10-23-snapshot-<slug>.md`; nothing is filed or posted.

**Cost.** Per life and brain about 30 life-lengths of events (R, R2, P1, 9 restores, 9 fork processes with 4 brains after the cut); a life is about 400 events, so about 90 s for the plain brain and about 4 min for the learned code, serially. 8 brain-lives (4 lives x 2 brains) at 4 workers: about 6 to 8 minutes in total, check included.

## Check
- 2026-10-23, after the pre-registration commit `6d710c3` and before any data life. Evidence: `exp/EXP-05-check.out` and `exp/EXP-05-check.json`. Run on Cadence 0.85.1 at `4ac887c` (clean tree), Python 3.12.10, NumPy 2.4.2, life 99, both brains, 76 s wall. Result: **FAIL on k4.**
  - k1 PASS. 7 of the 9 cut types occurred on each brain, and each saved the groups its type requires. A5 and A6 did not occur on either brain in this life. Each brain was aroused for its 100 youth moments and at none of its other 200 moments, so neither woke after the reversal.
  - k2 PASS. R and R2 (hash seeds 1 and 2) were identical on both brains, in every event and in the final bytes.
  - k3 PASS. The 1e-9 reward perturbation at A3 was flagged on both brains. The member digest moved under a one-ULP change.
  - k4 FAIL. The state moves: every cut's checkpoint bytes differ from the final bytes. But after 6 of the 14 cuts, the reference's remaining events contain only one distinct action. On the plain brain that was A3, A4, B1, B2 and B3; on the learned-code brain, B3. After youth both brains answered greedily with one fixed action. Plain accuracy was .26 / .23 / .49 over moments 0-99 / 100-199 / 200-299 (chance .33). Learned code scored .52 / .52 / .25, which is exactly what one fixed action scores on this map.
  - k5 PASS. The projected full run was 227 s.
  - By the registered rule, a failed check stops the run. No data life was run.
- **Seen in the check** (life 99 only). The registered outcome is VOID, so these are observations, not arm verdicts. 56 continuations were compared (14 cuts x restore, O, D, S), about 13,800 event records.
  - Fresh-process restores: at 14 of 14 cuts the final checkpoint had the reference's bytes. The event records were identical at 12 of 14.
  - The 2 differences: at A2 on both brains, one field of one event differs. A2 is a cut after the first of two waits under a sampled action. On the next `wait`, the reference still shows the previous `live`'s `last_arousal` snapshot, while the loaded brain shows `None`. The docs say `last_arousal` is "None after construction, reset or load" (`docs/api.md`, Attributes; `docs/start.md`), and `wait` does not set it. So this is a report that the docs exclude from the continuation, not a state difference. Every other field of the 339 events after that cut matches, and the final bytes are identical.
  - Round trip (load, then save at once) gave back the cut file's bytes at 14 of 14.
  - Forks. Deepcopy D matched the reference at 14 of 14, in trace and final bytes. So did the original O, run beside the forks. Save/load fork S matched at 12 of 14 (the same A2 `last_arousal` difference), and its final bytes matched at 14 of 14. The fork-time checkpoints of O, D and S were identical to each other and to P1's cut file at 14 of 14. The diverging twin X differed from the reference at 14 of 14.
  - `MODE=diagnose` was added after the check. It runs nothing: it reads the stored traces and prints every differing field (`exp/EXP-05-check-diagnosis.out`). Result: 52 continuations identical in every event; 4 differ in exactly that one field at one event.

## Summary
- Question: save a learning Cadence brain in the middle of its life, either while an action still waits for its outcome or right after a reset. Load it in a new Python process. Does it continue bit for bit as the brain that was never stopped? Does a `copy.deepcopy` fork do the same?
- Setup: as registered. Cadence 0.85.1 + 41 commits at `4ac887c`. Two composed brains with arousal, episodic choice and recall, one with a learned code. A 4-cue / 3-action map learned through `live`, with delayed outcomes, a reversal and three resets. Comparisons were exact: every event's record plus the SHA-256 of the final checkpoint's bytes, against an uninterrupted reference. The check ran on life 99; data lives 0..2 were never run.
- Prediction (quoted from the pre-registration): check passes about 85%; R equals R2 about 97%; A0 about 97%; arm A about 82%, arm B about 85%, deepcopy about 88%, save/load fork about 85%; all three arms about 65%; round trip about 60%; learning above chance about 70%.
- Result: the check failed on k4. After 6 of 14 cuts the reference continued with a single action, so "identical" was too cheap to count there. On this life both brains collapsed onto one greedy action after youth and did not wake at the reversal, so A5 and A6 did not occur. Seen in the check, not a reading:
  - on this life, every fresh-process restore and every fork ended on the reference's checkpoint bytes (14 of 14 each);
  - event records matched in 52 of 56 continuations;
  - the other 4 differ only in `last_arousal`, which the docs say a load clears;
  - load-then-save reproduced the cut bytes at 14 of 14.
- Verdict: **VOID** (by its own check, before any data life; loop: VOID). No arm verdict is declared. No upstream bug was found, so no draft was written.

## Reflection
- What it means: we still do not have the registered answer. The one check life is consistent with the docs' promise of an exact continuation. Every restore, every save/load fork and every deepcopy ended on the reference's checkpoint bytes, and their event records matched except where the docs say a report resets on load. That is a hint for EXP-05b, not a reading. It is 2 brains on 1 life, and the adult cuts that would have been most informative (A5 and A6, a woken brain after the reversal) never occurred. For our harnesses, it hints that deepcopy behaves like save/load, with one difference to know about: a save/load fork starts with `last_arousal` None, and deepcopy keeps it. That matters only to a harness that reads `last_arousal` before the twin's next `live`. Side observation, one life per brain: under 1 / 0 rewards with salience-marked misses, both brains settled on one fixed greedy action after youth. The learned-code brain did not wake when the reversal halved its income (.52 to .25).
- Process: two design errors, both mine, both caught before any data life.
  - First, the task did not keep the brain learning after youth. I piloted only timing and API behaviour, not the brain's behaviour under the exact run conditions. The RUN GATE's VARIANCE line applies to an identity test as well: if the compared trace stops varying, "identical" passes for free. k4 was written to catch this, and it did.
  - Second, the trace recorded `last_arousal` at `wait` events. The docs say a load clears that field, so the registered "every field" rule would have counted a documented reset as a failure. The diagnosis isolated it to that one field.
  - What went right: the determinism control (R equal to R2 across hash seeds) and the sensitivity control (a 1e-9 change flagged) both worked. The stop rule held, and no data life was run on a failed check.
- Prediction check:
  - "The check passes" (85%) was wrong.
  - R equal to R2 (97%) and A0 (97%) held on the check life.
  - The round trip (60%) held at 14 of 14. I expected load to drop report fields such as `last_learning`; it does not. The only report it drops is `last_arousal`, which `save` does not write.
  - "Learning above chance" (70%) failed for the plain brain (.23). The learned-code brain's .52 is the score of one fixed action, so it did not hold there either.
  - The arm predictions were not tested.
- Lesson: an identity test needs a behaviour pilot too. The compared trace must keep varying after every cut, and the compared fields must be the ones the library says survive a load. Read the attribute docs for "None after load" before choosing what to compare.
- Next: EXP-05b is queued as ready (EXPERIMENT-QUEUE.md). It keeps the same three arms, compares `last_arousal` only at `live` events, uses a task piloted under the exact run conditions to keep the policy moving after youth and to wake the brain at the reversal, and gets fresh seeds and a new pre-registration. It needs a new pre-registration before any data, as this lab requires.
