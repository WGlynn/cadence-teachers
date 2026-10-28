# EXP-78: do surprise lessons rescue the recall arms in Sean McClane's Breakout?

- Date: 2026-10-28 (pre-registered before any surprise-lesson data) | Cadence version: 0.89.0 (`81345d8`, the version the demo ran; pinned copy `~/_cadence_0890` installed in `~/_ext/venv-arcade`) | Program iter: none (off the V(S) ladder; an outside demo, OPH/Pragma group 2026-10-28)
- Harness: `sean-mcclane832/cadence-arcade` at `c8a5e4c`, `classic/run.py` unchanged, cloned to `~/_ext/sean-arcade`; the only change is `--cadence '{"learning_surprise": true}'`. Evidence: `exp/EXP-78-*`.

## Pre-registration (written 2026-10-28, before any EXP-78 surprise data)

**Question.** In Sean McClane's single-frame Breakout demo, the recall arms lose to the no-recall arm on most seeds (his `classic/runs/main.log`, seeds 10-21: mean bricks per test episode over the last 10 blocks pos32 6.04, pos0 5.80, norecall 7.08; pos32 beats pos0 on 6 of 12 seeds, his "6/12"). Every arm is taught with `teaching="normalized"` on every training moment, and the students already agree with the coach about .82 to .97 of the time. EXP-72 tested the same kind of teaching on a different task (V0.5B, a recall-heads brain). There (EXP-71), three of five founders collapsed onto one action late in training under Bernhard's calm rule, which on those runs never switched off every-row lessons (his reproduction, Cadence group 2026-10-25). With `learning_surprise` from the first lesson, none collapsed, and mean held accuracy at 4,096 lessons rose from .53 to .85. Cadence's docs now recommend surprise lessons once the answers are mostly right (`docs/teach.md:110`, crediting EXP-72). Does the same switch raise the recall arms here, and does it change the recall against no-recall comparison?

**Arms.** pos32, pos0 and norecall exactly as in the demo, each run with `learning_surprise=True` (teach only the moments whose greedy answer differs from the coach's label). Baselines: the demo's own every-row arms. If our identity check (seed 10, norecall and pos32, on this machine) reproduces Sean's logged numbers, his logged baselines are used; if it does not, the three baseline arms are rerun here on seeds 10-21 and only our own runs are compared.

**Seeds and life.** Seeds 10-21, 30 blocks of 1,000 training moments, 3 greedy test episodes per block, everything else as the demo (see `classic/run.py` docstring). Metric: the demo's primary (bricks per test episode over the last 10 blocks); secondary: final test agreement with the coach.

**Predictions.**
- P1: surprise raises pos32: pos32-surprise > pos32-every-row in at least 8 of 12 paired seeds, median paired difference above 0. Same test for pos0 (P1b).
- P2: fewer recall seeds end with low agreement. A seed counts as low if its last test block agrees with the coach less than .75 of the time. Under every-row lessons, 4 of the 24 recall lives are low (pos32 seeds 15 and 16; pos0 seeds 13 and 15). Under surprise, at most 1 of 24 is.
- P3 (no direction predicted, reported): pos32-surprise against norecall-surprise, paired, seeds won and median difference.
- Expectation: P1 and P2 hold if every-row teaching is what costs the recall arms here. If P1 fails, the EXP-72 mechanism does not explain this demo's recall deficit, and that is the result.

**Decision rules.** Paired comparisons use Wilcoxon signed-rank on the 12 seed differences (the demo's test), reported beside the win count. SUPPORTIVE if P1 and P2 hold; PARTIAL if one holds; NOT SUPPORTED if neither. VOID if a run crashes or the identity check shows the harness does not run as published.

**Cost.** Unknown until the identity check returns (Sean's machine: about 140 s per Cadence life with Numba; this machine has no Numba). With surprise lessons, a moment the brain already answers right gets no lesson at all (`docs/teach.md:82-86`). So the surprise arms should run faster. Each moment still costs one settle to act.
