# EXP-48: does 0.83's episodic memory generalize the Stone Age chain, or record the taught situations?

- Date: 2026-10-13 | Cadence version: 0.83.0 (`23dba71`) | Program iter: none (teaching track; the EXP-46 limit, raised by the Noesis cross-read: transfer is not teaching when the test overlaps the lesson)
- Script: `exp/EXP-48_generalize_or_record.py` | Evidence: `exp/EXP-48-pilot.*`, `exp/EXP-48-full.json/.jsonl/.out` (PENDING)

## Summary
- Question: EXP-46 taught and tested on the same four chain states, so it shows acquisition, not generalization; a brain that records the caregiver's answers would score the same. If every situation also carries features irrelevant to the chain, and the test uses combinations of them never seen in teaching, does the memory brain still get the chain right?
- Setup: EXP-45's V5 chamber replica; the observation is V5's 7 inputs plus 3 weather bits, irrelevant to the chain, fixed for an attempt. Teaching weathers: the 4 even-parity combinations (000, 011, 101, 110); test weathers: the 4 odd-parity ones (001, 010, 100, 111), never seen in teaching; every single bit value appears in teaching. Brain: `Brain.compose(10, 5, modules=(48, 24), arousal=True)` with and without `memory_choice=True`; signals corrective (V5's caregiver) and natural (world reward only); 120 teaching attempts. Readings on frozen copies: per-state greedy accuracy over the 16 seen situations (4 states x 4 weathers) and the 16 unseen ones, and sampled full-chain success under unseen weather (100 attempts). Seeds 42-53.
- RUN GATE: (1) prediction below, written before the pilot. (2) Window: a 3-seed pilot at exact run conditions; EXP-46 (no weather) sets the seen-side expectation (memory corrective .94, natural .75). (3) Variance: seeds vary; arms differ only in memory and signal; weather draws are seeded per run. (4) Metric: the generalization gap = seen minus unseen per-state accuracy, per seed; unseen accuracy against the no-memory arm. (5) Chain: train success -> seen accuracy -> unseen accuracy -> sampled unseen.
- Prediction (written before the pilot):
  - (P1) memory + corrective reaches seen accuracy >= .85 (EXP-46's acquisition survives three irrelevant inputs).
  - (P2) The memory partly records: memory + corrective's unseen accuracy is at least .1 below its seen accuracy (mean gap >= .1), but stays >= .6.
  - (P3) The memory's gain is not only recording: memory + corrective's unseen accuracy beats no-memory + corrective's unseen accuracy by >= .2.
  - (P4) Without memory the readout generalizes as well as it learns: no-memory arms' mean gap is within .1 of zero.
- Decision rule (written before the pilot): P2 and P3 hold -> the memory both records and generalizes, and its EXP-46 numbers overstate what transfers to new situations by the gap; a gap near zero with P3 holding -> the memory generalizes over irrelevant features, and EXP-46's limit is answered for this kind of novelty; unseen accuracy at the no-memory level -> the memory's gain was recording.
- Result: PENDING. Verdict: PENDING.

## Reflection
- PENDING (after the run).
