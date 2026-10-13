# EXP-48: does 0.83's episodic memory generalize the Stone Age chain, or record the taught situations?

- Date: 2026-10-13 | Cadence version: 0.83.0 (`23dba71`) | Program iter: none (teaching track; the EXP-46 limit, raised by the Noesis cross-read: transfer is not teaching when the test overlaps the lesson)
- Script: `exp/EXP-48_generalize_or_record.py` | Evidence: `exp/EXP-48-pilot.*`, `exp/EXP-48-full.json/.jsonl/.out`

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
- Pilot (3 seeds, 42-44, exact run conditions, `exp/EXP-48-pilot.out`), read before the full run: gaps are small (memory corrective +.04, memory natural +.06, no-memory +.02 / .00), seen accuracy is below EXP-46's (memory corrective .83 vs .94: three irrelevant inputs slow acquisition at 120 attempts), and nothing sits at a floor or ceiling. No design change; the full run reuses the pilot's seeds and adds 45-53.
- Result (12 seeds; per-state greedy accuracy over 16 seen and 16 unseen situations; gap = seen - unseen, per seed):

  | arm | seen | unseen | gap (SEM) | seeds with gap 0 | sampled full-chain, unseen weather |
  |---|---|---|---|---|---|
  | memory / corrective | .89 (.04) | .84 (.06) | +.05 (.02) | 9 of 12 | .920 |
  | memory / natural | .64 (.06) | .58 (.06) | +.06 (.02) | 8 of 12 | .387 |
  | without / corrective | .53 (.05) | .53 (.05) | .00 (.01) | 6 of 12 | .201 |
  | without / natural | .32 (.04) | .33 (.04) | -.02 (.02) | 5 of 12 | .098 |

  P1 HELD (memory corrective seen .89). P2 FAILED in the direction of generalization: memory corrective's gap is +.05, under the predicted .1; most seeds lose nothing to unseen weather, and two seeds (gaps .19 and .25) carry most of it. P3 HELD: on unseen weather memory corrective beats no-memory corrective by .31 (paired SEM .07). P4 HELD (no-memory gaps .00 and -.02).
- Verdict: SUPPORTIVE. 3 of 4 predictions held; the failed one failed toward generalization. Decision rule: a gap near zero with P3 holding, so for this kind of novelty (irrelevant features in unseen combinations) the memory generalizes and EXP-46's acquisition-only limit is answered: what the memory brain learned carries to situations it was never taught, at a cost of about .05 per state, concentrated in a few seeds.

## Reflection
- What it means: 0.83's episodic memory is not an answer key here. Its records are keyed by the whole situation, yet a chain taught under four weathers holds under four weathers it never saw (unseen .84 against seen .89), and its gain over the brain without memory survives the novelty almost intact (.31 of it on unseen situations). Where it does record, it is a minority of seeds, not the typical case. For the Noesis cross-read this is the condition that matters: transfer that survives a test the lesson never covered.
- Process: pre-registered and pushed before the pilot; pilot read before the full run; no design change. Limits that bound the claim: the novelty is irrelevant features only. The relevant input (inventory) takes the same four values at test as in teaching, so this is invariance to distractors, not generalization to a new recipe, a longer chain or a new inventory; 12 seeds; 120 attempts; three distractor bits.
- Lesson: an acquisition result becomes a learning result only when the test has situations the lesson never covered; build the held-out split into the chamber from the start.
- Next: EXP-49 (the Noesis-lite teacher market) pays teachers on held-out situations, which this result makes meaningful; a harder novelty test (a second recipe or a longer chain sharing steps) is the follow-up for compositional generalization.
