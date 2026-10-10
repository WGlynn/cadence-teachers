## What this PR adds
EXP-XX / fix / tooling:

## Checklist
- [ ] Prediction was written (docstring or proposal issue) BEFORE the full run
- [ ] Effect-window pilot ran under the exact run conditions, and every link of the mechanism chain moved with the knob
- [ ] `experiments/EXP-XX.md` written from `experiments/TEMPLATE.md` (Summary + Reflection), nulls included
- [ ] Raw outputs committed in `exp/` (`.out` / `.json` / `.jsonl`), Cadence version stamped
- [ ] `python experiments/check.py` passes
- [ ] Program log entry added to the top of the ITERATION LOG in `VS-TRANSFER-PROGRAM.md` (append-only; corrections go in a new entry)
