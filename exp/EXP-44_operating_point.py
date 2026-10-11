"""
EXP-44: on graded text, is the limit the readout's operating point or the brain's size?

EXP-43: graded by a judging teacher, a Cadence brain reading the last 3 characters reached .254 on held-out Alice
(always learning, 6 passes) while a lookup table on the same grades reached .346. Which lever closes that gap?
(a) the readout's operating point: Cadence 0.81's readout intrinsic plasticity (a learner gene that moves each output's
bias toward a target activation so the readout neither saturates nor falls silent; upstream measured it lowering
readings under reward at its development point), or a smaller actor step (the composed actor rate 1.0 is named in
Cadence's own troubleshooting as contributing to failure); (b) capacity: a brain twice as wide.

Arms, all EXP-43's judged-w3-always (last 3 characters in, 4-gram teacher's judged grade, Brain.step, no arousal,
EXP-43's seeds):
  control     : modules (32, 16), founder genes (= EXP-43 judged-w3-always; pass 1 must reproduce it exactly)
  homeo-0.3   : learning_homeostasis_rate 0.1, target 0.3 (upstream's development point)
  homeo-width : learning_homeostasis_rate 0.1, target 1/28 (the share one of 28 outputs holds under a uniform policy)
  actor-small : actor_eta 0.2 (a fifth of the composed 1.0)
  wide        : modules (64, 32), founder genes
Protocol: PASSES passes over Alice ch.1; after every pass, greedy held-out accuracy on ch.2 from a saved copy (no
learning, reset per probe, as EXP-43); after the last pass also the SAMPLED policy's held-out accuracy (same copy, not
greedy) and the share of the most frequent greedy answer (1.0 = one answer everywhere). Chain printed per pass:
grade -> mean reward -> agree with the teacher's best -> accuracy, plus the top-action share of the pass.
PREDICTION: experiments/EXP-44.md (written before the run).

    SEEDS=3 PASSES=2 WORKERS=8 TAG=full python -u EXP-44_operating_point.py
"""
import importlib.util, json, os, tempfile, time
from collections import Counter
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("exp43", os.path.join(HERE, "EXP-43_judged_grades.py"))
E43 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E43)
ALPHA, V, IDX, window, corpus, Teacher, grade = E43.ALPHA, E43.V, E43.IDX, E43.window, E43.corpus, E43.Teacher, E43.grade

SEEDS = int(os.environ.get("SEEDS", 3))
PASSES = int(os.environ.get("PASSES", 2))
TAG = os.environ.get("TAG", "full")
WORKERS = int(os.environ.get("WORKERS", 8))
N = 3  # characters of context; the teacher is order N + 1
ARMS = {
    "control": ((32, 16), {}),
    "homeo-0.3": ((32, 16), dict(learning_homeostasis_rate=0.1, learning_homeostasis_target=0.3)),
    "homeo-width": ((32, 16), dict(learning_homeostasis_rate=0.1, learning_homeostasis_target=round(1 / 28, 4))),
    "actor-small": ((32, 16), dict(actor_eta=0.2)),
    "wide": ((64, 32), {}),
}
ARM_ORDER = os.environ.get("ARMS", ",".join(ARMS)).split(",")


def run(job):
    arm, seed, a, b = job
    from cadence import Brain
    modules, genes = ARMS[arm]
    brain = Brain.compose(inputs=N * V, actions=V, modules=modules, seed=10_000 * (seed + 1) + 42, **genes)
    teacher, reward, t0 = Teacher(N + 1), None, time.time()

    def read(text):
        nonlocal reward
        hits = agree = 0
        rsum, said = 0.0, Counter()
        for i in range(len(text)):
            x = window(text, i, N)
            act = brain.step(x) if reward is None else brain.step(x, reward=reward, done=np.array([True]))
            act = int(np.asarray(act).reshape(-1)[0])
            said[act] += 1
            hits += act == IDX[text[i]]
            agree += act == teacher.best(text, i)
            r = grade("judged", teacher, text, i, act)
            rsum += r
            reward = np.array([r])
            teacher.tell(text, i)
        return dict(acc=hits / len(text), agree=agree / len(text), reward=rsum / len(text),
                    top_share=said.most_common(1)[0][1] / len(text))

    def probe(text, greedy=True):
        with tempfile.TemporaryDirectory() as d:
            cp = Brain.load(brain.save(os.path.join(d, "b.npz")))
            hits, said = 0, Counter()
            for i in range(len(text)):
                cp.reset()
                act = int(np.asarray(cp.act(window(text, i, N), greedy=greedy)).reshape(-1)[0])
                said[act] += 1
                hits += act == IDX[text[i]]
            return hits / len(text), said.most_common(1)[0][1] / len(text), ALPHA[said.most_common(1)[0][0]]

    by_pass, greedy = [], {}
    for p in range(1, PASSES + 1):
        by_pass.append(read(a))
        greedy[p] = probe(b)
        s = by_pass[-1]
        print(f"    {arm} s{seed} pass {p}: acc {s['acc']:.3f} agree {s['agree']:.3f} reward {s['reward']:+.3f} "
              f"top-share {s['top_share']:.2f}  greedy held-out {greedy[p][0]:.3f} (top '{greedy[p][2]}' {greedy[p][1]:.2f})",
              flush=True)
    sampled = probe(b, greedy=False)
    steps = PASSES * len(a)
    return dict(arm=arm, seed=seed, modules="x".join(map(str, modules)), genes=genes, passes=PASSES, by_pass=by_pass,
                greedy={str(k): v[0] for k, v in greedy.items()}, greedy_top_share={str(k): v[1] for k, v in greedy.items()},
                sampled=sampled[0], sampled_top_share=sampled[1],
                ms_per_step=round(1000 * (time.time() - t0) / (steps + len(b) * (PASSES + 1)), 2),
                cadence=__import__("cadence").__version__)


def main():
    t0 = time.time()
    a, b = corpus()
    ckpt = os.path.join(HERE, f"EXP-44-{TAG}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["arm"], r["seed"]) for r in rows}
    jobs = [(arm, s, a, b) for s in range(SEEDS) for arm in ARM_ORDER if (arm, s) not in done]
    print(f"EXP-44: {len(jobs)} runs to go ({len(done)} done); passes {PASSES}; arms {ARM_ORDER}", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as f:
                    f.write(json.dumps(r) + "\n")
                print(f"  {r['arm']:11s} seed {r['seed']}: greedy {r['greedy']} sampled {r['sampled']:.3f}  "
                      f"{r['ms_per_step']} ms/step", flush=True)
    sem = lambda x: float(np.std(x, ddof=1) / np.sqrt(len(x))) if len(x) > 1 else 0.0
    print(f"\ngreedy held-out accuracy (Alice ch.2) by pass, {SEEDS} seeds  ({time.time() - t0:.0f}s)")
    summary = {}
    for arm in ARM_ORDER:
        rs = [r for r in rows if r["arm"] == arm and r["seed"] < SEEDS and r["passes"] == PASSES]
        if not rs:
            continue
        last = [r["greedy"][str(PASSES)] for r in rs]
        summary[arm] = dict(mean=float(np.mean(last)), sem=sem(last), n=len(rs),
                            sampled=float(np.mean([r["sampled"] for r in rs])))
        print(f"  {arm:11s} " + " ".join(f"pass {p}: {np.mean([r['greedy'][str(p)] for r in rs]):.3f}" for p in range(1, PASSES + 1))
              + f" (SEM {sem(last):.3f})  sampled {summary[arm]['sampled']:.3f}"
              + f"  greedy top-share {np.mean([r['greedy_top_share'][str(PASSES)] for r in rs]):.2f}"
              + f"  per seed {[round(x, 3) for x in last]}")
    json.dump(dict(rows=rows, summary=summary, passes=PASSES), open(os.path.join(HERE, f"EXP-44-{TAG}.json"), "w"))


if __name__ == "__main__":
    main()
