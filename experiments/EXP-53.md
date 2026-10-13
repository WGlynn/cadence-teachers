# EXP-53: does the content of a teacher's labels matter, and at what lesson length?

- Date: 2026-10-13 | Cadence version: 0.83.0 (`23dba71`) | Program iter: none (teaching track; the gate EXP-52 set for any further Noesis-lite market work)
- Script: `exp/EXP-53_does_content_matter.py` | Evidence: `exp/EXP-53-pilot.*`, `exp/EXP-53-full.json/.jsonl/.out`

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
- Result (24 students per length, paired twins; per-state accuracy on unseen weather after 20 attempts alone):

  | lesson | know-4 | random labels | untaught | content = know-4 - random (SEM) | know-4 - untaught | random - untaught |
  |---|---|---|---|---|---|---|
  | 40 | .714 | .701 | .453 | +.013 (.061) | +.260 | +.247 |
  | 120 | .742 | .635 | .695 | +.107 (.064) | +.047 | -.060 |
  | 240 | .820 | .753 | .659 | +.068 (.058) | +.161 | +.094 |

  P1 HELD (content at 40 is +.013, within 2 SEM of zero: EXP-52 reproduces). P2 FAILED (content at 240 is +.068, under .1 and 1.2 SEM). P3 FAILED (not monotone: 120 is the largest, and every step is within noise). P4 FAILED at 120 (random labels sit below untaught, -.060; know-4 only +.047).
- Verdict: NULL. 1 of 4 held. The content of the labels could not be seen at any lesson length: the largest per-length effect is +.107 (1.7 SEM), and pooled over 120 and 240 it is about +.09 (about 2 SEM), so a small effect may exist but this run cannot show it. What dominates is the correction event at short lessons (+.25 over untaught for either teacher at 40) and the untaught brain catching up from world reward at longer ones. Decision rule: P2 failed, so in this protocol the student learns from being corrected rather than from what it is told, even at 240 attempts; market work waits for a teaching channel that carries content.

## Reflection
- What it means: the Noesis-lite market had nothing to price, and this is why. Through `step(teacher=...)` on executed mistakes in guided windows, the default memory brain takes in the fact of being corrected far more than the answer it is given; a perfect teacher and a random one are within noise at every length tried. EXP-46's caregiver result (.94 at 120) is consistent with this: it never had a random-label control, so part of what looked like teaching was correction. For Cadence this is a question worth putting to upstream (is the teaching path meant to carry the label's content into the policy in a continuing life, or is it designed around settled lessons?); for Noesis it is the cleanest case yet of a channel that moves outcomes without carrying information.
- Process: pre-registered, pilot read before the full run, no design change; the pilot's striking "random beats know-4" at short lessons (n=3) shrank to noise at n=24, which is why the pilot only sets the window. Ran at Idle CPU priority while Will played, which changes timing, not results (every run is seeded). Limits: one chamber, one teaching protocol (labels only on executed mistakes, a third of decisions), the default memory brain, 24 students per length; EXP-45's delayed-credit brain was not tested here and may take content in differently.
- Lesson: when a market prices teaching, first test that the teaching channel carries content (perfect teacher vs random teacher on the same protocol), at the lesson lengths the market will use.
- Next: ask upstream how `teacher=` labels are meant to act in a continuing life (Will-gated note); test content transfer through a different channel: demonstrations at every decision (not only on mistakes), settled `fit()`-style lessons, or EXP-45's delayed-credit brain; market work (Noesis-lite v2) waits for a channel with measurable content.
