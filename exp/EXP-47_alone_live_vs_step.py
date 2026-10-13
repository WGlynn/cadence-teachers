"""
EXP-47: after the caregiver leaves, does a memory brain's taught Stone Age chain drift through `step`, through `live`,
or both, and when?

Upstream's 0.83 caveat (docs/episodic.md): "after 80 episodes alone through `step`, the frozen greedy policy of the
corrected chain can stall at one stage while the sampled policy still succeeds (through `live` it does not)". EXP-46
saw stage answers drift through `live` (all four right 9 -> 5 of 12) while full-chain success held. This runs both paths
from the same taught brains and reads them over time.

Brain: Brain.compose(7, 5, modules=(48, 24), arousal=True, memory_choice=True) (EXP-46's memory brain). Teaching: 120
attempts (EXP-46 / V5), signals corrective and natural. Then 80 attempts alone with world reward only, through `live` or
through `step`, from a copy of the same taught brain. Readings on frozen copies after teaching and after 10, 20, 40, 80
attempts alone: per-state greedy accuracy and answers, greedy full-chain, sampled full-chain (100 attempts).
PREDICTION: experiments/EXP-47.md (written before the pilot).

    SEEDS=12 WORKERS=2 TAG=full python -u EXP-47_alone_live_vs_step.py
"""
import importlib.util, json, os, tempfile, time
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("EPISODES", "120")
_spec = importlib.util.spec_from_file_location("e46", os.path.join(HERE, "EXP-46_episodic_memory_stone_age.py"))
E46 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E46)
Chamber, train, read = E46.Chamber, E46.train, E46.read

SEEDS = int(os.environ.get("SEEDS", 12))
WORKERS = int(os.environ.get("WORKERS", 2))
TAG = os.environ.get("TAG", "full")
CHECKS = [10, 20, 40, 80]
SIGNALS = os.environ.get("SIGNALS", "corrective,natural").split(",")
PATHS = os.environ.get("PATHS", "live,step").split(",")


def alone_until(brain, path, start, stop, state):
    """Continue the alone stream from attempt `start` to `stop` through `live` or `step`, world reward only.
    `state` carries the chamber and the pending action across calls so the stream is one continuing life."""
    call = brain.live if path == "live" else brain.step
    if state.get("c") is None:
        state["c"] = Chamber()
        state["a"] = int(np.asarray(call(state["c"].x())).reshape(-1)[0])
    c, a = state["c"], state["a"]
    for _ in range(stop - start):
        while True:
            _, r = c.execute(a)
            if c.done:
                c = Chamber()
                a = int(np.asarray(call(c.x(), reward=np.array([r]), done=np.array([True]))).reshape(-1)[0])
                break
            a = int(np.asarray(call(c.x(), reward=np.array([r]), done=np.array([False]))).reshape(-1)[0])
    state["c"], state["a"] = c, a


def run(job):
    signal, seed = job
    import cadence as cd
    t0 = time.time()
    brain = cd.Brain.compose(7, 5, modules=(48, 24), seed=seed, arousal=True, memory_choice=True)
    train(brain, signal)
    out = dict(signal=signal, seed=seed, cadence=cd.__version__)
    with tempfile.TemporaryDirectory() as d:
        taught_path = brain.save(os.path.join(d, "taught.npz"))
        out["taught"] = read(taught_path)
        for path in PATHS:
            b = cd.Brain.load(taught_path)
            state, prev, series = {}, 0, {}
            for k in CHECKS:
                alone_until(b, path, prev, k, state)
                prev = k
                # read a frozen copy; the stream itself continues untouched
                series[str(k)] = read(b.save(os.path.join(d, f"{path}-{k}.npz")))
            out[path] = series
    out["secs"] = round(time.time() - t0, 1)
    line = f"  {signal:10s} s{seed}: taught acc {out['taught']['acc']:.2f} {out['taught']['answers']}"
    for path in PATHS:
        line += f" | {path} " + " ".join(f"{k}:{out[path][str(k)]['acc']:.2f}/{int(out[path][str(k)]['greedy'])}" for k in CHECKS)
    print(line + f" ({out['secs']}s)", flush=True)
    return out


def main():
    t0 = time.time()
    ckpt = os.path.join(HERE, f"EXP-47-{TAG}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["signal"], r["seed"]) for r in rows}
    jobs = [(sg, 42 + s) for s in range(SEEDS) for sg in SIGNALS if (sg, 42 + s) not in done]
    print(f"EXP-47: {len(jobs)} runs to go ({len(done)} done); signals {SIGNALS}; paths {PATHS}; checks {CHECKS}", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as f:
                    f.write(json.dumps(r) + "\n")
    print(f"\nEXP-47 summary, {SEEDS} seeds ({time.time() - t0:.0f}s). Per check: per-state acc mean / all-4-right count / "
          f"greedy full-chain solves / sampled mean")
    summary = {}
    for sg in SIGNALS:
        rs = [r for r in rows if r["signal"] == sg and r["seed"] < 42 + SEEDS]
        if not rs:
            continue
        t = [r["taught"] for r in rs]
        print(f"  {sg:10s} taught      acc {np.mean([x['acc'] for x in t]):.2f}  all-4 {sum(x['acc'] == 1 for x in t):2d}  "
              f"greedy {sum(x['greedy'] for x in t):2d}  sampled {np.mean([x['sampled'] for x in t]):.3f}")
        summary[sg] = {"taught": dict(acc=float(np.mean([x['acc'] for x in t])), all4=sum(x['acc'] == 1 for x in t),
                                      greedy=sum(x['greedy'] for x in t), sampled=float(np.mean([x['sampled'] for x in t])))}
        for path in PATHS:
            for k in CHECKS:
                xs = [r[path][str(k)] for r in rs]
                m = dict(acc=float(np.mean([x['acc'] for x in xs])), all4=sum(x['acc'] == 1 for x in xs),
                         greedy=sum(x['greedy'] for x in xs), sampled=float(np.mean([x['sampled'] for x in xs])))
                summary[sg][f"{path}-{k}"] = m
                print(f"  {sg:10s} {path:4s} {k:3d}    acc {m['acc']:.2f}  all-4 {m['all4']:2d}  greedy {m['greedy']:2d}  "
                      f"sampled {m['sampled']:.3f}")
    json.dump(dict(rows=rows, summary=summary), open(os.path.join(HERE, f"EXP-47-{TAG}.json"), "w"))


if __name__ == "__main__":
    main()
