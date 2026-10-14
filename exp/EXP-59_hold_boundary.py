"""
EXP-59: where EXP-57's hold rule breaks: gathering wood is correct but leaves the observation unchanged. Observations
A, A, B, C at the four stages (right actions WOOD, STONE, FIRE, WARM); the hold rule erases the successful WOOD, the only
thing that tells stage 2 from stage 1. place / ctx5 / hold5, 48 fresh seeds per signal, 120 attempts.
PREDICTION: experiments/EXP-59.md (written before any run).

    WORKERS=4 TAG=full python -u EXP-59_hold_boundary.py
"""
import importlib.util, json, os, tempfile, time
from math import comb
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("e56", os.path.join(HERE, "EXP-56_ambiguous_chain_trace.py"))
E56 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E56)
np = E56.np

OBS_C = np.array([[0.35, 1.0, 1.0, 0.0, 0.5, 0.5, 1.0]])
STAGE_OBS = [E56.OBS_A, E56.OBS_A, E56.OBS_B, OBS_C]          # the first (correct) WOOD changes nothing visible


def invisible_wood_x(self):
    return STAGE_OBS[self.k].copy()


E56.Chamber.x = invisible_wood_x

WORKERS = int(os.environ.get("WORKERS", 4))
TAG = os.environ.get("TAG", "full")
ARMS, SIGNALS, SEED_BASE, N, EPISODES = ("place", "ctx5", "hold5"), ("natural", "corrective"), 59_000, 48, 120


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
    ft = " ".join("  - " if v is None else f"{v:.2f}" for v in rd["first_try"])
    print(f"  {arm:5s} {signal:10s} s{i:2d}: exact {int(rd['greedy_exact'])} sampled {rd['sampled']:.2f} first-try {ft} ({row['secs']}s)",
          flush=True)
    return row


def mcnemar(b, c):
    n = b + c
    return min(1.0, 2 * sum(comb(n, k) for k in range(min(b, c) + 1)) / 2 ** n) if n else 1.0


def main():
    t0 = time.time()
    ckpt = os.path.join(HERE, f"EXP-59-{TAG}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["arm"], r["signal"], r["seed"]) for r in rows}
    jobs = [(a, s, i) for i in range(N) for s in SIGNALS for a in ARMS if (a, s, i) not in done]
    print(f"EXP-59: {len(jobs)} lives to go ({len(done)} done)", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as fh:
                    fh.write(json.dumps(r) + "\n")
    by = {(r["arm"], r["signal"], r["seed"]): r for r in rows}
    sem = lambda x: float(np.std(x, ddof=1) / np.sqrt(len(x))) if len(x) > 1 else 0.0
    print(f"\nEXP-59 summary ({time.time() - t0:.0f}s), invisible-wood chain (A, A, B, C), 120 attempts")
    summary = {}
    for scope in list(SIGNALS) + ["pooled"]:
        sigs = SIGNALS if scope == "pooled" else (scope,)
        o = {"mean_first_try": {}, "clean": {}}
        for a in ARMS:
            rs = [by[(a, s, i)] for s in sigs for i in range(N) if (a, s, i) in by]
            o["mean_first_try"][a] = [float(np.nanmean([np.nan if r["first_try"][k] is None else r["first_try"][k] for r in rs]))
                                      for k in range(4)]
            o["clean"][a] = sum(r["greedy_exact"] for r in rs)
        diffs = {}
        for k in range(4):
            d = [by[("hold5", s, i)]["first_try"][k] - by[("ctx5", s, i)]["first_try"][k] for s in sigs for i in range(N)
                 if ("hold5", s, i) in by and ("ctx5", s, i) in by
                 and by[("hold5", s, i)]["first_try"][k] is not None and by[("ctx5", s, i)]["first_try"][k] is not None]
            diffs[k + 1] = (float(np.mean(d)), sem(d), len(d)) if d else (None, None, 0)
        pairs = [(by[("hold5", s, i)], by[("ctx5", s, i)]) for s in sigs for i in range(N) if ("hold5", s, i) in by and ("ctx5", s, i) in by]
        hb = sum(h["greedy_exact"] and not c["greedy_exact"] for h, c in pairs)
        cb = sum(c["greedy_exact"] and not h["greedy_exact"] for h, c in pairs)
        o.update(hold_minus_ctx_first_try=diffs, hold_only=hb, ctx_only=cb, p=mcnemar(hb, cb),
                 sampled={a: float(np.mean([by[(a, s, i)]["sampled"] for s in sigs for i in range(N) if (a, s, i) in by])) for a in ARMS})
        summary[scope] = o
        print(f"  [{scope:10s}] clean greedy " + "  ".join(f"{a} {o['clean'][a]}" for a in ARMS)
              + f" (hold-only {hb}, ctx-only {cb}, p {o['p']:.4f}) | sampled " + "  ".join(f"{a} {o['sampled'][a]:.3f}" for a in ARMS))
        for a in ARMS:
            print(f"      first try by stage {a:5s}: " + " ".join(f"{v:.2f}" for v in o["mean_first_try"][a]))
        print("      hold5 - ctx5 first try: " + "  ".join(f"stage {k} {m:+.3f} (SEM {s:.3f})" for k, (m, s, n) in diffs.items() if m is not None))
    json.dump(dict(rows=rows, summary=summary), open(os.path.join(HERE, f"EXP-59-{TAG}.json"), "w"))


if __name__ == "__main__":
    main()
