# Cadence Teachers

Can small learning brains teach each other, and can a market pay them fairly for it, with teaching ability passed
down generations? This repo is an open lab notebook of experiments on that question, built on
[Cadence](https://github.com/muellerberndt/cadence) by Bernhard Mueller.

**Start here: [the Atlas](https://cadence-atlas.vercel.app)** (mirror: [GitHub Pages](https://wglynn.github.io/cadence-teachers/experiments/ATLAS.html)): every experiment on one
page, with charts, verdicts, and the mistakes we made along the way (also at `experiments/ATLAS.html`).

## Honest floor first

Small Cadence brains, small tasks (bandits, a key-door world), one PC. <!-- counts:start -->86 experiments so far: 6 crossed, 34 supportive, 18 boundary, 16 null, 5 void, 1 retracted, 6 superseded.<!-- counts:end --> Every bug we caught in our own scripts is kept on the atlas, with the rerun.
Nothing here has been shown at scale, and nulls and retractions are kept, not hidden.

## What we have measured (see the write-ups for numbers and caveats)

- A twin-brain test separates genuine teaching from fakes; Shapley splits teamwork credit fairly where leave-one-out overpays.
- Teaching beats learning alone on key-door; skill passes down 5 generations by grading (labels fail).
- Over-teaching hurts; knowing your limits is a teaching skill.
- A teacher network's plateau was stale teaching; provenance notes plus a drift check lift it (.79 to .99).
- Weight change alone does not tell genuine from fake teaching.

Each experiment has a write-up with a Summary and a Reflection in `experiments/EXP-XX.md`.

## Repo map

- `experiments/`: one write-up per experiment, `TEMPLATE.md`, the atlas and its generator (`build_atlas.py`), `check.py`
- `exp/`: experiment scripts and their raw outputs (`.out`, `.json`, `.jsonl`). Brain checkpoints are not committed; scripts regenerate them.
- `VS-TRANSFER-PROGRAM.md`: the program log (append-only, newest first), including the RUN GATE every experiment must pass.
- `EXPERIMENT-RESULTS.md`, `EXPERIMENT-QUEUE.md`, `M5-EXOGENOUS-ANCHOR.md`: results ledger, queue, and the open "who writes the tests" boundary.
- `ui/`: a small market simulator page.

## Reproduce

```bash
./setup.sh                      # clones Cadence at the pinned commit into vendor/, installs it, runs the smoke test
python exp/EXP-33_forgetting_fix.py
```

Cadence is not on PyPI at the pinned version, so `setup.sh` installs it from GitHub. Each write-up names the Cadence
version it ran on; most scripts read their settings from environment variables listed at the top of the file. Brain
checkpoints are not committed; scripts regenerate them.

## Help wanted

Open problems: XOR-style synergy, defenses against sandbagging and fake need, who writes the tests, whether a pedigree
share drives discovery, and teaching multi-step prerequisite chains. To contribute an experiment: write the prediction
before running, pilot the effect window under the exact run conditions, ship `experiments/EXP-XX.md` from the template,
and make `python experiments/check.py` pass. Nulls and replications are welcome. Full guide: [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Code GPL-3.0 (`LICENSE`); write-ups and docs CC BY 4.0 (`LICENSE-docs.md`).
