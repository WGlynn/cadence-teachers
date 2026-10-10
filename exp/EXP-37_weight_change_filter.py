"""
EXP-37 — Maarten's question: can we read a brain's gain from the INSIDE (how much its weights moved) instead of
running an outcome test?

EXP-08 harness (K=8 bandit, plain Cadence Brain). Same founder snapshot, three lessons: genuine (teaches the held-out
task T), fake_wrong (teaches the opposite rule), fake_random (reward unrelated to the action). For each twin record
  dW   : L2 norm of the change in all saved parameter arrays vs the founder
  v    : measured transfer on T (acc after - acc of the untouched founder)
PREDICTION (before running): dW is similar for genuine and fake_wrong (both learn a rule) while v differs hugely, so dW
is worth-blind; at best dW separates "learned something" (genuine, wrong) from noise (random): a pre-filter, not a price.
"""
import os, sys, json, tempfile, importlib.util
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("e08", os.path.join(HERE, "EXP-08_vs_transfer_separation.py"))
e08 = importlib.util.module_from_spec(spec); spec.loader.exec_module(e08)
from cadence import Brain, ArousalConfig

SEEDS = range(int(os.environ.get("SEEDS", 16)))


def params(path):
    path = str(path)
    z = np.load(path if path.endswith(".npz") else path + ".npz", allow_pickle=True)
    return {k: np.asarray(z[k], float) for k in z.files if np.asarray(z[k]).dtype.kind in "fc"}


def dW(p0, p1):
    return float(np.sqrt(sum(np.sum((p1[k] - p0[k]) ** 2) for k in p0 if k in p1 and p0[k].shape == p1[k].shape)))


def main():
    rows = []
    for seed in SEEDS:
        rng = np.random.default_rng(10_000 + seed)
        T = e08.make_rule(rng)
        Tp = (e08.A - 1) - T
        b0 = Brain.compose(inputs=e08.K, actions=e08.A, modules=e08.MODULES, seed=seed, arousal=ArousalConfig())
        d = tempfile.mkdtemp()
        snap = b0.save(os.path.join(d, "anc"))
        p0 = params(snap)
        acc0 = e08.eval_on(Brain.load(snap), T)
        frng = np.random.default_rng(20_000 + seed)
        lessons = {
            "genuine": lambda c, a: 1.0 if a == int(T[c]) else -1.0,
            "fake_wrong": lambda c, a: 1.0 if a == int(Tp[c]) else -1.0,
            "fake_random": lambda c, a: 1.0 if frng.random() < .5 else -1.0,
        }
        for name, fn in lessons.items():
            b = Brain.load(snap)
            e08.ingest(b, e08.WITNESS_STEPS, fn)
            v = e08.eval_on(b, T) - acc0
            path = b.save(os.path.join(d, name))
            rows.append(dict(seed=seed, lesson=name, dW=dW(p0, params(path)), v=v))
        print(f"seed {seed}: " + "  ".join(f"{r['lesson']} dW {r['dW']:.2f} v {r['v']:+.2f}" for r in rows[-3:]), flush=True)
    print("-" * 72)
    for name in ("genuine", "fake_wrong", "fake_random"):
        r = [x for x in rows if x["lesson"] == name]
        print(f"  {name:11s} weight change {np.mean([x['dW'] for x in r]):.3f} (sd {np.std([x['dW'] for x in r]):.3f})"
              f"   measured worth {np.mean([x['v'] for x in r]):+.3f}")
    dws = np.array([x["dW"] for x in rows]); vs = np.array([x["v"] for x in rows])
    print(f"  correlation(weight change, worth) over all lessons: {np.corrcoef(dws, vs)[0, 1]:+.2f}")
    json.dump(rows, open(os.path.join(HERE, "EXP-37.json"), "w"))


if __name__ == "__main__":
    main()
