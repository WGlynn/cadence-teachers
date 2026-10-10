# Contributing to Cadence Teachers

Anyone can run an experiment here. Nulls, replications and "we found a bug in your script" are as welcome as wins:
about a third of this lab's own runs were nulls or voids, and every one is kept.

## 1. Set up (5 minutes)

```bash
git clone https://github.com/WGlynn/cadence-teachers && cd cadence-teachers
./setup.sh          # clones Cadence at the pinned commit into vendor/, installs it, runs exp/smoke_test.py
```

Needs git and Python >= 3.11. On Windows use Git Bash. To use your own Cadence checkout instead, set
`CADENCE_SRC=/path/to/cadence` and `pip install -e` it. The smoke test should end with `SMOKE TEST PASSED`.

## 2. Pick something

- **Replicate** an existing experiment: run `python exp/EXP-XX_<name>.py` (settings are env vars at the top of each
  script) and open a *Replication report* issue. Easiest way in, and genuinely useful.
- **Take an open problem** from the README, or **propose your own** with the *Experiment proposal* issue template.
  Claim the next free EXP number in the issue title (next free: check `experiments/` and open issues; EXP-38 at the
  time of writing).

## 3. The RUN GATE (before any run longer than ~10 minutes)

These come from mistakes this lab actually made (see the "Hall of nulls and mistakes" in the Atlas):

1. **Prediction**: write the expected result down before running (script docstring or the proposal issue).
2. **Window**: pilot the key knob (budget, population, seeds, difficulty) at 2-3 values *under the exact run
   conditions*. The effect must be visible, not stuck at 0% or 100%. Under-powered runs were our most common failure.
3. **Variance**: the thing being compared must actually vary.
4. **Metric**: a degenerate policy must not be able to pass the score.
5. **Chain**: name the mechanism (knob -> signal -> estimate -> choice -> outcome) and print each link in the pilot.
   A smoke test (does it run) is not a pilot. A link that never moves is a design bug: fix it, do not run.

If any line fails, redesign instead of running.

## 4. Ship it

- Script: `exp/EXP-XX_<short_name>.py`, settings via env vars, Cadence version stamped in the output.
- Raw outputs: `exp/EXP-XX*.out` / `.json` / `.jsonl`. Do not commit brain checkpoints (`*.npz`, `*_brains/`).
- Write-up: `experiments/EXP-XX.md` from `experiments/TEMPLATE.md`, with a **Summary** and a **Reflection**. The
  Reflection says what it means, what went wrong in how it was run, and the lesson. Required for every experiment.
- Program log: add an entry at the top of the ITERATION LOG in `VS-TRANSFER-PROGRAM.md`. It is append-only: correct an
  old result with a new entry that says what changed, never by editing the old one.
- `python experiments/check.py` must pass (CI runs it on every PR).
- Optional: add your experiment to `experiments/atlas.json` and run `python experiments/build_atlas.py`.

## Ground rules

- Report numbers with seed counts and SEM. Do not round a null into a result.
- Credit ideas to the people they came from.
- Code is GPL-3.0 (matching Cadence); write-ups CC BY 4.0. By contributing you agree to license your work the same way.
