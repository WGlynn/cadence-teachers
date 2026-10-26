"""EXP-71: on Attention V0.5B, is held accuracy limited by fitting the taught pairs or by generalizing,
and do the misses pile onto one action?

Bernhard's V0.5B pilot (cadence-stone-age PR #1, 4 founders, 1024 lessons) reads H2 held .65-.86 against
taught .66-.92: held nearly tracks taught. This runs his runner unchanged (vendored in exp/v05b/, commit
5f038a3) and reads taught, held and the predicted-action histogram at lesson checkpoints. Every reading is
taken on a deepcopy, so the training path is his exactly; at 1024 lessons founder 59101 must reproduce his
JSON (the reproduction gate). Pre-registration: experiments/EXP-71.md.

    python -u EXP-71_v05b_fit_vs_generalize.py --seed 59201 --heads 2 --out EXP-71-59201-H2.jsonl
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

CHECKPOINTS = (256, 512, 1024, 2048, 4096)
CONTROLS_AT = (1024, 4096)


def reading(brain, bank, patterns):
    """His accuracy() plus the choice histogram, on a copy."""
    out = v.accuracy(brain, bank, patterns)
    trial = deepcopy(brain)
    choice = v.answer(trial, bank, patterns)
    truth = v.labels(patterns)
    counts = np.bincount(choice, minlength=v.ACTIONS)
    out["choice_counts"] = counts.tolist()
    out["label_counts"] = np.bincount(truth, minlength=v.ACTIONS).tolist()
    out["modal_share"] = float(counts.max() / counts.sum())
    out["per_class"] = [float(np.mean(choice[truth == a] == a)) if np.any(truth == a) else None
                        for a in range(v.ACTIONS)]
    return out


def controls(brain, bank, held, heads):
    c = {"role0_erased": v.accuracy(brain, bank, held, v.RECORD[0]),
         "role1_erased": v.accuracy(brain, bank, held, v.RECORD[1]),
         "distractors_erased": v.accuracy(brain, bank, held, v.RECORD[2] + v.RECORD[3]),
         "memory_off": v.accuracy(brain, bank, held, sum(v.RECORD.values(), []))}
    if heads == 2:
        c["clone_head"] = v.accuracy(brain, bank, held, clone=True)
    return c


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--heads", type=int, choices=(1, 2), required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    t0 = time.time()
    split = v.report("V0.5B", *v.split_v05b(), 9)
    assert split["tests_conjunctive_generalization"], split  # his admission gate
    brain = v.compose(a.seed, a.heads)
    v.warm(brain)
    bank = v.banks(brain)
    panels = np.random.default_rng(99)  # his evaluation panels, drawn once, same order
    taught, held = v.sample(panels, 192, v.TAUGHT), v.sample(panels, 192, v.HELD)
    # his train(), unrolled so it can pause at checkpoints; same rng, same calm rule, same order
    rng = np.random.default_rng(1000 + a.seed)
    level, refused, calm_from = 1.0, 0, None
    with open(a.out, "w") as f:
        f.write(json.dumps({"cadence": cd.__version__, "seed": a.seed, "heads": a.heads,
                            "runner": "cadence-stone-age 5f038a3", "split": split}) + "\n")
        for lesson in range(CHECKPOINTS[-1]):
            patterns = v.sample(rng, 16, v.TAUGHT)
            try:
                wrong = v.answer(brain, bank, patterns) != v.labels(patterns)
                level = 0.95 * level + 0.05 * float(wrong.mean())
                calm = level < 0.02
                if calm != brain.learner.config.surprise:
                    brain.retune(learning_surprise=calm)
                    calm_from = lesson if calm and calm_from is None else calm_from
                n = len(patterns)
                v.install(brain, bank, patterns)
                brain.act(v.event(v.NEUTRAL, n), greedy=True)
                brain.lesson(v.event(v.ASK, n), v.labels(patterns))
            except RuntimeError:
                refused += 1
            done = lesson + 1
            if done in CHECKPOINTS:
                row = {"lessons": done, "refused": refused, "calm_from": calm_from,
                       "level": round(level, 4), "seconds": round(time.time() - t0, 1),
                       "taught": reading(brain, bank, taught), "held": reading(brain, bank, held)}
                if done in CONTROLS_AT:
                    row["held_controls"] = controls(brain, bank, held, a.heads)
                f.write(json.dumps(row) + "\n")
                f.flush()
                print(a.seed, f"H{a.heads}", done, row["taught"]["accuracy"], row["held"]["accuracy"],
                      row["taught"]["modal_share"], row["seconds"], flush=True)


if __name__ == "__main__":
    main()
