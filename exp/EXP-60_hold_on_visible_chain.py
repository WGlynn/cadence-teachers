"""
EXP-60: does keeping misses out of the temporal context (EXP-56/57's hold5) also help on the normal Stone Age chain, where
the inventory is visible (EXP-45's observation), or only on Huncho's hidden-inventory chain?
EXP-56's brain, trace rule, signals and readings; only the observation changes. ctx5 vs hold5 on 48 fresh seeds per
signal, place on the first 24 per signal as a reference. 120 attempts.
PREDICTION: experiments/EXP-60.md (written before any run).

    WORKERS=4 TAG=full python -u EXP-60_hold_on_visible_chain.py
"""
import importlib.util, json, os, tempfile, time
from math import comb
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("e56", os.path.join(HERE, "EXP-56_ambiguous_chain_trace.py"))
E56 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E56)
np = E56.np

STAGES = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1)]       # (has wood, has stone, has fire) at each stage, EXP-45


def visible_x(self):
    w, s, f = STAGES[self.k]
    return np.array([[0.35, float(w), float(s), float(f), w / 2.0, s / 2.0, 1.0]])   # EXP-45's obs()


E56.Chamber.x = visible_x            # the only change from EXP-56/57: the inventory is visible

WORKERS = int(os.environ.get("WORKERS", 4))
TAG = os.environ.get("TAG", "full")
SIGNALS, SEED_BASE, N_PAIR, N_PLACE, EPISODES = ("natural", "corrective"), 60_000, 48, 24, 120


def run(job):
    arm, signal, i = job
    import cadence as cd
    t0 = time.time()
    E56.EPISODES = EPISODES
    b = E56.compose(arm, SEED_BASE + i)
    stats = E56.train(b, E56.Trace(b, arm == "hold5"), signal)
    with tempfile.TemporaryDirectory() as d:
        rd = E56.read(b.save(os.path.join(d, "b.npz")), arm == "hold5")
    row = dict(arm=arm, signal=signal, seed=i, **stats, **rd, secs=round(time.time() - t0, 1), cadence=cd.__version__)
    print(f"  {arm:5s} {signal:10s} s{i:2d}: exact {int(rd['greedy_exact'])} sampled {rd['sampled']:.2f} ({row['secs']}s)", flush=True)
    return row


def mcnemar(b, c):
    n = b + c
    return min(1.0, 2 * sum(comb(n, k) for k in range(min(b, c) + 1)) / 2 ** n) if n else 1.0


def main():
    t0 = time.time()
    ckpt = os.path.join(HERE, f"EXP-60-{TAG}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["arm"], r["signal"], r["seed"]) for r in rows}
    jobs = [(a, s, i) for i in range(N_PAIR) for s in SIGNALS for a in ("ctx5", "hold5") + (("place",) if i < N_PLACE else ())
            if (a, s, i) not in done]
    print(f"EXP-60: {len(jobs)} lives to go ({len(done)} done)", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as fh:
                    fh.write(json.dumps(r) + "\n")
    by = {(r["arm"], r["signal"], r["seed"]): r for r in rows}
    sem = lambda x: float(np.std(x, ddof=1) / np.sqrt(len(x))) if len(x) > 1 else 0.0
    print(f"\nEXP-60 summary ({time.time() - t0:.0f}s), visible-inventory chain, 120 attempts")
    summary = {}
    for scope in list(SIGNALS) + ["pooled"]:
        sigs = SIGNALS if scope == "pooled" else (scope,)
        o = {}
        for x, y, n in (("hold5", "ctx5", N_PAIR), ("place", "ctx5", N_PLACE)):
            pairs = [(by[(x, s, i)], by[(y, s, i)]) for s in sigs for i in range(n) if (x, s, i) in by and (y, s, i) in by]
            xb = sum(u["greedy_exact"] and not v["greedy_exact"] for u, v in pairs)
            yb = sum(v["greedy_exact"] and not u["greedy_exact"] for u, v in pairs)
            r0 = [u["p_right"]["r0"] - v["p_right"]["r0"] for u, v in pairs
                  if u["p_right"]["r0"] is not None and v["p_right"]["r0"] is not None]
            sd = [u["sampled"] - v["sampled"] for u, v in pairs]
            o[f"{x}-{y}"] = dict(n=len(pairs), x_exact=sum(u["greedy_exact"] for u, _ in pairs),
                                 y_exact=sum(v["greedy_exact"] for _, v in pairs), x_only=xb, y_only=yb, p=mcnemar(xb, yb),
                                 r0=float(np.mean(r0)), r0_sem=sem(r0), sampled=float(np.mean(sd)), sampled_sem=sem(sd),
                                 x_sampled=float(np.mean([u["sampled"] for u, _ in pairs])),
                                 y_sampled=float(np.mean([v["sampled"] for _, v in pairs])))
            q = o[f"{x}-{y}"]
            print(f"  [{scope:10s}] {x} vs {y} n={q['n']:3d}: clean greedy {q['x_exact']} vs {q['y_exact']} ({x}-only {xb}, "
                  f"{y}-only {yb}, McNemar p {q['p']:.4f}) | first try {q['r0']:+.3f} (SEM {q['r0_sem']:.3f}) | sampled "
                  f"{q['x_sampled']:.3f} vs {q['y_sampled']:.3f} ({q['sampled']:+.3f}, SEM {q['sampled_sem']:.3f})")
        summary[scope] = o
    json.dump(dict(rows=rows, summary=summary), open(os.path.join(HERE, f"EXP-60-{TAG}.json"), "w"))


if __name__ == "__main__":
    main()
