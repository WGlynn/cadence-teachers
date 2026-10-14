"""
EXP-57: confirm on fresh seeds that keeping misses out of the temporal context (EXP-56's hold5) makes the greedy ambiguous
chain clean more often than the plain .5 context (ctx5). Reuses EXP-56's chamber, brain, trace rule and readings.
Primary: greedy exact pass at 120 attempts, 48 seeds per signal, paired exact McNemar. Secondary: 240 attempts, 24 seeds.
PREDICTION: experiments/EXP-57.md (written before any run).

    WORKERS=4 TAG=full python -u EXP-57_confirm_hold_greedy.py
"""
import importlib.util, json, os, tempfile, time
from math import comb
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("e56", os.path.join(HERE, "EXP-56_ambiguous_chain_trace.py"))
E56 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E56)
np = E56.np

WORKERS = int(os.environ.get("WORKERS", 4))
TAG = os.environ.get("TAG", "full")
PLAN = [(120, 48), (240, 24)]                 # (attempts, seeds per signal)
ARMS, SIGNALS, SEED_BASE = ("ctx5", "hold5"), ("natural", "corrective"), 57_000


def run(job):
    arm, signal, episodes, i = job
    import cadence as cd
    t0 = time.time()
    E56.EPISODES = episodes
    b = E56.compose(arm, SEED_BASE + i)
    stats = E56.train(b, E56.Trace(b, arm == "hold5"), signal)
    with tempfile.TemporaryDirectory() as d:
        rd = E56.read(b.save(os.path.join(d, "b.npz")), arm == "hold5")
    row = dict(arm=arm, signal=signal, episodes=episodes, seed=i, **stats, **rd, secs=round(time.time() - t0, 1),
               cadence=cd.__version__)
    print(f"  {arm} {signal:10s} ep{episodes} s{i:2d}: exact {int(rd['greedy_exact'])} sampled {rd['sampled']:.2f} "
          f"r0 {rd['p_right']['r0'] if rd['p_right']['r0'] is not None else float('nan'):.2f} ({row['secs']}s)", flush=True)
    return row


def mcnemar(b, c):
    n = b + c
    return min(1.0, 2 * sum(comb(n, k) for k in range(min(b, c) + 1)) / 2 ** n) if n else 1.0


def main():
    t0 = time.time()
    ckpt = os.path.join(HERE, f"EXP-57-{TAG}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["arm"], r["signal"], r["episodes"], r["seed"]) for r in rows}
    jobs = [(a, s, ep, i) for ep, n in PLAN for i in range(n) for s in SIGNALS for a in ARMS if (a, s, ep, i) not in done]
    print(f"EXP-57: {len(jobs)} lives to go ({len(done)} done); plan {PLAN}; seeds from {SEED_BASE}", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as fh:
                    fh.write(json.dumps(r) + "\n")
    by = {(r["arm"], r["signal"], r["episodes"], r["seed"]): r for r in rows}
    sem = lambda x: float(np.std(x, ddof=1) / np.sqrt(len(x))) if len(x) > 1 else 0.0
    print(f"\nEXP-57 summary ({time.time() - t0:.0f}s)")
    summary = {}
    for ep, n in PLAN:
        for scope in list(SIGNALS) + ["pooled"]:
            sigs = SIGNALS if scope == "pooled" else (scope,)
            pairs = [(by[("hold5", s, ep, i)], by[("ctx5", s, ep, i)]) for s in sigs for i in range(n)
                     if ("hold5", s, ep, i) in by and ("ctx5", s, ep, i) in by]
            if not pairs:
                continue
            hb = sum(h["greedy_exact"] and not c["greedy_exact"] for h, c in pairs)
            cb = sum(c["greedy_exact"] and not h["greedy_exact"] for h, c in pairs)
            r0 = [h["p_right"]["r0"] - c["p_right"]["r0"] for h, c in pairs
                  if h["p_right"]["r0"] is not None and c["p_right"]["r0"] is not None]
            sd = [h["sampled"] - c["sampled"] for h, c in pairs]
            o = dict(n=len(pairs), hold_exact=sum(h["greedy_exact"] for h, _ in pairs),
                     ctx_exact=sum(c["greedy_exact"] for _, c in pairs), hold_only=hb, ctx_only=cb, p=mcnemar(hb, cb),
                     r0_diff=float(np.mean(r0)), r0_sem=sem(r0), sampled_diff=float(np.mean(sd)), sampled_sem=sem(sd),
                     hold_sampled=float(np.mean([h["sampled"] for h, _ in pairs])),
                     ctx_sampled=float(np.mean([c["sampled"] for _, c in pairs])))
            summary[f"{ep}-{scope}"] = o
            print(f"  ep{ep} [{scope:10s}] n={o['n']:3d}  greedy exact hold5 {o['hold_exact']} vs ctx5 {o['ctx_exact']} "
                  f"(hold-only {hb}, ctx-only {cb}, McNemar p {o['p']:.4f}) | first try {o['r0_diff']:+.3f} (SEM "
                  f"{o['r0_sem']:.3f}) | sampled hold5 {o['hold_sampled']:.3f} ctx5 {o['ctx_sampled']:.3f} diff "
                  f"{o['sampled_diff']:+.3f} (SEM {o['sampled_sem']:.3f})")
    json.dump(dict(rows=rows, summary=summary), open(os.path.join(HERE, f"EXP-57-{TAG}.json"), "w"))


if __name__ == "__main__":
    main()
