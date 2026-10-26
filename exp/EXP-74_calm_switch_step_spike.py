"""EXP-74: does switching to learning_surprise mid-training give normalized teaching an oversized step?

Mechanism probe for EXP-71's late collapse on V0.5B. Replays EXP-71's training exactly (Bernhard's runner, calm rule,
same lesson stream; EXP-71's readings were on copies, so the path is the same) and logs, for every lesson: the rows
the lesson taught, the wrong count on the lesson's 16 patterns, the running wrong level, whether surprise was on, and
the learner's report (`scale_step` = mean |weight step|, `bias_step`). Taught and held accuracy on EXP-71's panels at
2048 and 4096 cross-check the replay. Pre-registration: experiments/EXP-74.md.

    python -u EXP-74_calm_switch_step_spike.py --seed 59101 --out EXP-74-59101.jsonl
"""
import argparse
import json
import pathlib
import sys
import time
from copy import deepcopy

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).with_name("v05b")))
import run_v05b as v  # noqa: E402  (Bernhard's runner, unchanged)

import cadence as cd  # noqa: E402

LESSONS, CHECK = 4096, (2048, 4096)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    t0 = time.time()
    brain = v.compose(a.seed, 2)
    v.warm(brain)
    bank = v.banks(brain)
    panels = np.random.default_rng(99)
    taught, held = v.sample(panels, 192, v.TAUGHT), v.sample(panels, 192, v.HELD)
    rng = np.random.default_rng(1000 + a.seed)
    level = 1.0
    with open(a.out, "w") as f:
        f.write(json.dumps({"cadence": cd.__version__, "seed": a.seed, "heads": 2, "teach": "calm (Bernhard's rule)"}) + "\n")
        for lesson in range(LESSONS):
            patterns = v.sample(rng, 16, v.TAUGHT)
            row = {"lesson": lesson}
            try:
                wrong = v.answer(brain, bank, patterns) != v.labels(patterns)
                level = 0.95 * level + 0.05 * float(wrong.mean())
                calm = level < 0.02
                if calm != brain.learner.config.surprise:
                    brain.retune(learning_surprise=calm)
                n = len(patterns)
                v.install(brain, bank, patterns)
                brain.act(v.event(v.NEUTRAL, n), greedy=True)
                report = brain.lesson(v.event(v.ASK, n), v.labels(patterns))
                row.update(wrong=int(wrong.sum()), level=round(level, 5), surprise=bool(brain.learner.config.surprise),
                           report={k: (float(x) if isinstance(x, (int, float, np.floating, np.integer)) else str(x))
                                   for k, x in report.items()})
            except RuntimeError as error:
                row.update(refused=str(error)[:80])
            if lesson + 1 in CHECK:
                row["taught_acc"] = v.accuracy(brain, bank, taught)["accuracy"]
                row["held_acc"] = v.accuracy(brain, bank, held)["accuracy"]
                row["seconds"] = round(time.time() - t0, 1)
                print(a.seed, lesson + 1, row["taught_acc"], row["held_acc"], row["seconds"], flush=True)
            f.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    main()
