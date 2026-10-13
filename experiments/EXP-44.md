# EXP-44: on graded text, is the limit the readout's operating point or the brain's size?

- Date: 2026-10-11 | Cadence version: 0.81.0 (`736fee9`) | Program iter: iter34 (pending)
- Script: `exp/EXP-44_operating_point.py` | Evidence: `exp/EXP-44-full.json/.jsonl/.out` (PENDING) | Text: Alice ch.1 (train), ch.2 (held out), as EXP-42/43

## Summary
- Question: EXP-43 left a gap. Graded by a judging teacher, a Cadence brain reading 3 characters reached .254 held out, and a lookup table on the same grades reached .346. EXP-43's next levers were (a) the readout's operating point and (b) capacity. Which one moves it? Run by the cadence experiment loop as lever (a), Jarvis's stated pick, sharpened with a capacity arm so the run decides between (a) and (b).
- Setup: EXP-43's judged-w3-always arm (4-gram teacher's judged grade, Brain.step, no arousal, EXP-43's seeds), 2 passes over ch.1, greedy held-out accuracy on ch.2 from a saved copy after each pass; after pass 2 also the sampled policy's held-out accuracy and the share of the most common greedy answer. 3 seeds. Arms: control (modules (32, 16), founder genes); homeo-0.3 (Cadence 0.81's readout intrinsic plasticity at upstream's development point, rate .1, target .3); homeo-width (rate .1, target 1/28, the share one of 28 outputs holds under a uniform policy); actor-small (actor_eta .2, a fifth of the composed 1.0); wide (modules (64, 32), founder genes).
- RUN GATE: (1) prediction below. (2) Window: no separate pilot for the new arms. The control's window comes from EXP-43's measured curve for this exact arm (greedy .240 after pass 1, .254 after pass 3; floor always-space .202; table .346, teacher .506), so a lift or a drop shows between .20 and .35 at pass 2; a 600-character smoke run of the code was seen, too short to read. (3) Variance: arms differ only in genes or width; seeds vary. (4) Metric: greedy accuracy is passed by always-space at .202, so the top-answer share and the sampled policy are read beside it. (5) Chain per pass per arm: grade -> mean reward -> agree with the teacher's best -> accuracy, plus the pass's top-action share.
- Prediction (written before the run):
  - Check, not a prediction: control on Cadence 0.81 reproduces EXP-43's judged-w3-always pass-1 greedy numbers exactly (.242 / .263 / .217); the new gene is off by default.
  - (P1) homeo-0.3 ends below control after pass 2 (upstream's reward result transfers: the gene as declared is a teaching-time mechanism).
  - (P2) No operating-point arm (homeo-0.3, homeo-width, actor-small) beats control by more than 2 SEM after pass 2.
  - (P3) wide beats control by more than 2 SEM after pass 2 (capacity is a binding limit with about 2,000 three-character contexts).
  - (P4) Every arm stays below the table on the same grades (.346).
- Decision rule (written before the run): wide up and no operating-point arm up -> capacity next (lever b); an operating-point arm up -> lever (a) holds; neither -> the gap to the table is exploration (the table tries every character once per context it sees; Cadence samples), and the next lever is exploration, not size or operating point.
- Amendment (2026-10-13, after the crash, before the remaining runs' results): the 2026-10-11 full run stopped at 7 of 15 runs when one brain in a readout-gene arm raised "brain did not settle within 1024 steps" (residual .0065, tolerance .003), which killed the whole pool. A brain that cannot settle is a result, so the script now records such a run as unsettled (pass, phase, message), counts it per arm, and keeps it out of the arm's mean. Nothing else changed. Upstream removed the readout gene in Cadence 0.82.0 (it flattened a six-action policy under reward), so the remaining 8 runs finish on the pre-registered 0.81.0 from a pinned worktree, not on the current release. The crashed log is kept as `exp/EXP-44-full-crash-2026-10-11.out`.
- Result: PENDING. Verdict: PENDING.

## Reflection
- PENDING (after the run).
