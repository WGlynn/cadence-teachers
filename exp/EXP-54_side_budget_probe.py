import os, sys, importlib.util
sys.path.insert(0, os.path.expanduser("~/_cadence_197/src"))
import numpy as np
from multiprocessing import get_context
HERE = os.path.expanduser("~/cadence-lab/exp")

def load():
    spec = importlib.util.spec_from_file_location("e54", os.path.join(HERE, "EXP-54_surprise_teaching.py"))
    E = importlib.util.module_from_spec(spec); spec.loader.exec_module(E); return E

def job(a):
    L, k, kind, surprise = a
    import warnings; warnings.simplefilter("ignore")
    E = load()
    seed = 5_000_000 + 1000 * L + k
    rng = np.random.default_rng(seed); s = E.compose(seed, surprise)
    n = dict(lessons=0, exhausted=0); inner = s.step
    def step(*x, **kw):
        out = inner(*x, **kw)
        if kw.get("teacher") is not None:
            n["lessons"] += 1; n["exhausted"] += int(np.any(s.last_learning.get("demonstration_free_budget_exhausted", False)))
        return out
    s.step = step
    E.live_world(s, L, rng, label=E.labeller(kind, np.random.default_rng(seed + 1)))
    return (L, k, kind, surprise, n["lessons"], n["exhausted"])

if __name__ == "__main__":
    jobs = [(L, k, kind, sp) for L in (120, 240) for k in range(6) for kind in ("know-4", "random") for sp in (False, True)]
    with get_context("spawn").Pool(4) as p:
        rows = p.map(job, jobs)
    for sp in (False, True):
        for kind in ("know-4", "random"):
            r = [x for x in rows if x[2] == kind and x[3] == sp]
            print(f"surprise={sp!s:5} {kind:6}: lessons {sum(x[4] for x in r):5d}  free budget exhausted {sum(x[5] for x in r):3d}  "
                  f"students with any {sum(1 for x in r if x[5])}/{len(r)}")
