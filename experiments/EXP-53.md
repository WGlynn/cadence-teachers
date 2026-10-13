# EXP-53: does the content of a teacher's labels matter, and at what lesson length?

- Date: 2026-10-13 | Cadence version: 0.83.0 (`23dba71`) | Program iter: none (teaching track; the gate EXP-52 set for any further Noesis-lite market work)
- Script: `exp/EXP-53_does_content_matter.py` | Evidence: `exp/EXP-53-pilot.*`, `exp/EXP-53-full.json/.jsonl/.out` (PENDING)

## Summary
- Question: at 40-attempt lessons a teacher that knows the whole chain was worth no more than one labelling at random (EXP-52). Is that a property of short lessons, or does the label's content never reach the student through this teaching channel?
- Setup: EXP-48's weather chamber; the default memory brain; paired twins from each student's seed and world draws: taught by know-4 (the right action as the label on every executed mistake in a guided window), taught by random labels at the same kind of moments, and untaught; lesson lengths 40, 120 and 240 attempts; then 20 attempts alone through `live`; per-state greedy accuracy on unseen weather. Content = know-4 minus random, paired per student. 24 students per length.
- RUN GATE: (1) prediction below, written before the pilot. (2) Window: a pilot of 3 students per length at exact run conditions; EXP-52 sets the 40-attempt expectation (know-4 .661, random .648, untaught .46). (3) Variance: the three twins share the seed and world draws. (4) Metric: content, paired per student, at each length. (5) Chain: lesson length -> know-4 / random / untaught accuracy -> content.
- Prediction (written before the pilot):
  - (P1) At 40 attempts content is near zero (within 2 SEM of zero), reproducing EXP-52.
  - (P2) Content matters at long lessons: at 240 attempts know-4 beats random by >= .1 (paired mean).
  - (P3) Content grows with lesson length: mean content at 40 < 120 < 240.
  - (P4) Both taught arms beat untaught at every length.
- Decision rule (written before the pilot): P2 holds -> the teaching channel carries content given enough lessons, and Noesis-lite needs lessons at least as long as the length where content appears; P2 fails -> in this protocol the student learns from being corrected and not from the label's content even at 240 attempts, which is a finding about Cadence's teaching path worth telling upstream, and market work waits for a channel that carries content.
- Pilot (3 students per length, exact run conditions, `exp/EXP-53-pilot.out`), read before the full run: content (know-4 minus random) -.29 at 40, -.25 at 120, +.13 at 240, with random labels above know-4 at the two short lengths (.94 vs .65 at 40); SEMs .10-.27 at n=3, so direction only. No floor or ceiling; no design change. The full run reuses the pilot rows and adds 21 students per length.
- Result: PENDING. Verdict: PENDING.

## Reflection
- PENDING (after the run).
