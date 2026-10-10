"""
EXP-24 — calibrate: do teaching STRATEGIES differ in how well they teach (same parent skill)?

A strategy = genes used only when teaching by grading:
  match  : reward when the child's move matches the parent's
  miss   : penalty when it does not
  hold   : fraction of teaching trips where the child starts already holding the key
  floor  : whether floor cells are graded at all (floor presses are free in the task)
Same 4 passing parents (founders), same student seeds, M teaching trips. If child pass rate varies
by strategy, teaching ability is a real trait that selection can act on (EXP-25).
"""
import os, sys, json, time, importlib.util
import numpy as np
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
M = int(os.environ.get("M", 100))
OUT = os.path.join(HERE, "exp24_brains")
STRATS = {
    "plain":      dict(match=1.0, miss=0.25, hold=0.0, floor=1),
    "harsh":      dict(match=1.0, miss=1.0,  hold=0.0, floor=1),
    "soft":       dict(match=1.0, miss=0.0,  hold=0.0, floor=1),
    "nofloor":    dict(match=1.0, miss=0.25, hold=0.0, floor=0),
    "door-drill": dict(match=1.0, miss=0.25, hold=0.4, floor=0),
    "faint":      dict(match=0.2, miss=0.05, hold=0.0, floor=1),
    "mid":        dict(match=0.5, miss=0.12, hold=0.0, floor=1),
    "strong":     dict(match=2.0, miss=0.5,  hold=0.0, floor=1),
}


def _mod():
    spec = importlib.util.spec_from_file_location("e22", os.path.join(HERE, "EXP-22_generation_chains.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def teach_strategy(e22, child, parent_path, trips, rng, st):
    import cadence as cd
    from key_door import corridor, observe, INTERACT, FLOOR, CHEST
    e19 = e22.e19
    parent = cd.Brain.load(parent_path)
    pending = None
    for _ in range(trips):
        holding = bool(rng.random() < st["hold"])
        parent.reset()
        cells = corridor(e19.DELAY, e19.LENGTH, e19.JITTER, rng)
        for i, cell in enumerate(cells):
            x = observe(cell, holding, True)
            lab = int(parent.act(x, greedy=True)[0])
            fb = {} if pending is None else {"reward": [pending[0]], "done": [pending[1]]}
            a = int(child.step(x, **fb)[0])
            if cell == FLOOR and not st["floor"]:
                r = 0.0
            else:
                r = st["match"] if a == lab else -st["miss"]
            pending = (r, i == len(cells) - 1)
            if a == INTERACT and cell == CHEST and not holding:
                holding = True
    child.step(observe(FLOOR, False, True), reward=[pending[0]], done=[pending[1]])


def founder_job(i):
    e22 = _mod(); e19, e20 = e22.e19, e22.e20
    f = e19.make_brain(e19.POINT, 80_000 + i, None, True)
    rng = np.random.default_rng(5000 + i)
    if i % 2 == 0:
        e20.teach(f, e19.interleave("A" * 300, "B" * 300), rng)
    else:
        e22.train_end_to_end(f, 600, rng)
    path = f.save(os.path.join(OUT, f"founder_{i}.npz"))
    return path, e19.test_fed(path, 80_000 + i)


def child_job(args):
    parent_path, cseed, name, tag = args
    e22 = _mod(); e19 = e22.e19
    c = e19.make_brain(e19.POINT, cseed, None, True)
    teach_strategy(e22, c, parent_path, M, np.random.default_rng(cseed + 1), STRATS[name])
    path = c.save(os.path.join(OUT, f"{tag}.npz"))
    return name, cseed, e19.test_fed(path, cseed)


def main():
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    with get_context("spawn").Pool(int(os.environ.get("WORKERS", 6))) as pool:
        cands = pool.map(founder_job, range(2, 8))          # EXP-23 showed founders 2-8 pass
        parents = [p for p, d in cands if d >= .9][:4]
        print(f"parents: {len(parents)} passing  ({time.time()-t0:.0f}s)", flush=True)
        jobs = [(p, 200_000 + 10 * j + s, name, f"{name}_p{j}_s{s}")
                for name in STRATS for j, p in enumerate(parents) for s in range(3)]
        res = pool.map(child_job, jobs)
    out = {}
    for name, cseed, d in res:
        out.setdefault(name, []).append(d >= .9)
    print(f"EXP-24  M={M}  parents={len(parents)}  students/strategy={len(res)//len(STRATS)}  ({time.time()-t0:.0f}s)")
    for name, v in out.items():
        print(f"  {name:11s} child pass {np.mean(v):.2f}  ({sum(v)}/{len(v)})")
    # student-side control: same student seed across strategies
    json.dump(dict(M=M, results=[list(r) for r in res]), open(os.path.join(HERE, f"EXP-24-M{M}.json"), "w"))


if __name__ == "__main__":
    main()
