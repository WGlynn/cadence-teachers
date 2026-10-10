"""
EXP-30 — over-teaching: does parent grading HURT students at large budgets? (EXP-28 teacher arm, M swept 300-1500)
PREDICTION: if the 600-trip drop (8/8 -> 5/8) grows with M, over-drilling is real; flat = the dip was noise.

Matched budgets of M trips on the same corridors, same student seeds:
  world   : the world's own reward only (+1 opening the door holding the key, -0.25 wrong presses)
  teacher : parent grading (EXP-22 run B: +1 when the move matches the parent's, -0.25 otherwise)
Score = clean full-task pass (EXP-19 test). PREDICTION (before running): teacher wins clearly at small
M (dense per-move feedback); the gap closes by M=600. If the arms are equal at every M, teaching is
redundant for this skill.
"""
import os, sys, json, time, importlib.util
import numpy as np
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
BUDGETS = [int(x) for x in os.environ.get("BUDGETS", "300,600,1000,1500").split(",")]
ARMS = os.environ.get("ARMS", "world,teacher").split(",")
STUDENTS = int(os.environ.get("STUDENTS", 8))
PARENT = os.path.join(HERE, "exp24_brains", "founder_2.npz")


def e22():
    spec = importlib.util.spec_from_file_location("e22", os.path.join(HERE, "EXP-22_generation_chains.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def job(args):
    arm, M, s = args
    m = e22(); e19 = m.e19
    seed = 400_000 + s
    c = e19.make_brain(e19.POINT, seed, None, True)
    rng = np.random.default_rng(seed + 1)
    if arm == "world":
        m.train_end_to_end(c, M, rng)
    else:
        m.teach_by_grading(c, PARENT, M, rng)
    path = c.save(os.path.join(e19.TMP, f"e28_{arm}_{M}_{s}.npz"))
    return arm, M, s, e19.test_fed(path, seed)


def main():
    assert os.path.exists(PARENT), PARENT
    t0 = time.time()
    jobs = [(a, M, s) for M in BUDGETS for a in ARMS for s in range(STUDENTS)]
    with get_context("spawn").Pool(int(os.environ.get("WORKERS", 3))) as pool:
        res = pool.map(job, jobs)
    print(f"EXP-28 teacher vs world  students={STUDENTS}  ({time.time()-t0:.0f}s)")
    for M in BUDGETS:
        w = [d >= .9 for a, m, s, d in res if a == "world" and m == M]
        t = [d >= .9 for a, m, s, d in res if a == "teacher" and m == M]
        print(f"  M={M:4d} trips   world {sum(w)}/{len(w)}   teacher {sum(t)}/{len(t)}")
    json.dump(res, open(os.path.join(HERE, os.environ.get("OUTJ", "EXP-28.json")), "w"))


if __name__ == "__main__":
    main()
