"""EXP-75: is V0.5B's late collapse caused by nudged phases that take zero steps?

EXP-74 found that from about lesson 1300 a growing share of lessons run a nudged phase of 0 steps: its starting
residual (~.0025) is already within learning_tolerance (.003), so `_equilibrate_local` never relaxes it toward the
label, and in the collapsed founders the weight step then decays to ~1e-30. This reruns Bernhard's runner and calm rule
exactly (EXP-71/74) with one change, learning_tolerance=0.0003, logging every lesson (EXP-74) and the EXP-71 readings
at checkpoints. Pre-registration: experiments/EXP-75.md.

    python -u EXP-75_v05b_tolerance.py --seed 59101 --out EXP-75-59101.jsonl
"""
import argparse, json, pathlib, sys, time
from copy import deepcopy
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).with_name("v05b")))
import run_v05b as v  # noqa: E402  (Bernhard's runner, unchanged)
import cadence as cd  # noqa: E402

TOL = 0.0003
CHECKPOINTS = (256, 512, 1024, 2048, 4096)


def compose(seed, heads):  # his compose() with learning_tolerance=TOL instead of 0.003; nothing else differs
    return cd.Brain.compose(
        v.INPUTS, v.ACTIONS, modules=(64,), learned_code=16, attention=True, recall_heads=heads,
        recall_address=0.01, recall_temperature=0.25, episodic=False, teaching="normalized",
        learning_qualified=True, learning_damping=3, learning_free_steps=1024,
        learning_nudged_steps=1024, learning_tolerance=TOL, seed=seed,
    )


def reading(brain, bank, patterns):
    out = v.accuracy(brain, bank, patterns)
    choice = v.answer(deepcopy(brain), bank, patterns)
    counts = np.bincount(choice, minlength=v.ACTIONS)
    out.update(choice_counts=counts.tolist(), modal_share=float(counts.max() / counts.sum()))
    return out


def main():
    p = argparse.ArgumentParser(); p.add_argument("--seed", type=int, required=True); p.add_argument("--out", required=True)
    a = p.parse_args(); t0 = time.time()
    brain = compose(a.seed, 2); v.warm(brain); bank = v.banks(brain)
    panels = np.random.default_rng(99); taught, held = v.sample(panels, 192, v.TAUGHT), v.sample(panels, 192, v.HELD)
    rng = np.random.default_rng(1000 + a.seed); level = 1.0
    with open(a.out, "w") as f:
        f.write(json.dumps({"cadence": cd.__version__, "seed": a.seed, "heads": 2, "teach": "calm", "learning_tolerance": TOL}) + "\n")
        for lesson in range(CHECKPOINTS[-1]):
            patterns = v.sample(rng, 16, v.TAUGHT); row = {"lesson": lesson}
            try:
                wrong = v.answer(brain, bank, patterns) != v.labels(patterns)
                level = 0.95 * level + 0.05 * float(wrong.mean())
                calm = level < 0.02
                if calm != brain.learner.config.surprise:
                    brain.retune(learning_surprise=calm)
                n = len(patterns); v.install(brain, bank, patterns); brain.act(v.event(v.NEUTRAL, n), greedy=True)
                rep = brain.lesson(v.event(v.ASK, n), v.labels(patterns))
                row.update(wrong=int(wrong.sum()), level=round(level, 5), surprise=bool(brain.learner.config.surprise),
                           report={k: rep[k] for k in ("accepted_presentations", "nudged_steps", "nudged_residual",
                                                        "free_steps", "free_residual", "scale_step", "bias_step") if k in rep})
            except RuntimeError as error:
                row.update(refused=str(error)[:80])
            if lesson + 1 in CHECKPOINTS:
                row.update(taught=reading(brain, bank, taught), held=reading(brain, bank, held), seconds=round(time.time() - t0, 1))
                print(a.seed, lesson + 1, row["taught"]["accuracy"], row["held"]["accuracy"], row["taught"]["modal_share"], row["seconds"], flush=True)
            f.write(json.dumps(row, default=float) + "\n")


if __name__ == "__main__":
    main()
