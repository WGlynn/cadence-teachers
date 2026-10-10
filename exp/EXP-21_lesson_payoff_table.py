"""
EXP-21 — the full lesson game table, measured on real Cadence students.

For every coalition of lessons (null; each single lesson + null; every unordered pair of lessons
from MENU, incl. same-lesson pairs) and every student seed in a pool, teach a fresh founder
(protocol-3 operating point, N trips per slot, interleaved) and score it on the full key-door task
(clean trips: fed with zero wrong presses). EXP-20b then lets learning teacher brains play many
rounds against this measured table (real payoffs, cheap rounds).

Usage: SEED0=s N=300 python EXP-21_lesson_payoff_table.py <count>   -> EXP-21-s<s>.json
"""
import os, sys, json, time, itertools, importlib.util
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("e20", os.path.join(HERE, "EXP-20_learning_teachers.py"))
e20 = importlib.util.module_from_spec(spec); spec.loader.exec_module(e20)
e19 = e20.e19

MENU = e20.MENU                      # 0 null, A key, B door, F lamp, S spam
N = int(os.environ.get("N", 300))
SEED0 = int(os.environ.get("SEED0", 0))
COUNT = int(sys.argv[1]) if len(sys.argv) > 1 else 2

COALS = ["00"] + [a + "0" for a in MENU[1:]] + ["".join(p) for p in
         itertools.combinations_with_replacement(MENU[1:], 2)]


def main():
    out = {}
    t0 = time.time()
    for sseed in range(SEED0, SEED0 + COUNT):
        row = {}
        for c in COALS:
            row[c] = e20.student_score(e19.interleave(c[0] * N, c[1] * N), 50_000 + sseed)
        out[sseed] = row
        print(f"student {sseed}  " + " ".join(f"{k}:{v:.2f}" for k, v in row.items())
              + f"  ({time.time()-t0:.0f}s)", flush=True)
        json.dump(dict(N=N, menu=MENU, coalitions=COALS, scores=out),
                  open(os.path.join(HERE, f"EXP-21-s{SEED0}.json"), "w"))


if __name__ == "__main__":
    main()
