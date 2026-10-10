"""
EXP-20b — learning teachers play the MEASURED lesson game (EXP-21 table).

Each teacher is a Cadence brain (Brain.compose, 1 constant input, |MENU| actions, `step` learning).
Each round a student is drawn from the measured pool; both teachers pick a lesson; the coalition
scores are looked up from real Cadence students (EXP-21); each teacher is paid by a credit rule.

Credit rules compared (same table, same seeds):
  shapley : phi_i = 1/2 v(i) + 1/2 (v(12) - v(j))
  loo     : v(12) - v(j)            (overpays complementary pairs)
  equal   : v(12) / 2               (pays the pair's result regardless of own lesson)
Question: do teachers discover the complementary {key, door} split, avoid spam/lamp, and how
fast; which rule gets there and at what payout budget.
"""
import os, sys, json, glob
import numpy as np
import cadence as cd

HERE = os.path.dirname(os.path.abspath(__file__))
MENU = ["0", "A", "B", "F", "S"]
NAMES = {"0": "null", "A": "key", "B": "door", "F": "lamp", "S": "spam"}
ROUNDS = int(os.environ.get("ROUNDS", 1500))
RUNS = int(os.environ.get("RUNS", 12))
SCALE = 2.0


def load_table():
    scores = {}
    for f in glob.glob(os.path.join(HERE, "EXP-21-s*.json")):
        scores.update(json.load(open(f))["scores"])
    return list(scores.values())


def coal(a, b):
    if a == "0" and b == "0":
        return "00"
    if a == "0" or b == "0":
        return (b if a == "0" else a) + "0"
    return "".join(sorted((a, b), key=MENU.index))


def credits(row, c1, c2, rule):
    base = row["00"]
    v1, v2, v12 = row[coal(c1, "0")] - base, row[coal("0", c2)] - base, row[coal(c1, c2)] - base
    if rule == "shapley":
        return .5 * v1 + .5 * (v12 - v2), .5 * v2 + .5 * (v12 - v1), v12
    if rule == "loo":
        return v12 - v2, v12 - v1, v12
    return v12 / 2, v12 / 2, v12


def play(table, rule, run):
    rng = np.random.default_rng(7_000 + run)
    t1 = cd.Brain.compose(1, len(MENU), modules=(16,), seed=900 + 2 * run)
    t2 = cd.Brain.compose(1, len(MENU), modules=(16,), seed=901 + 2 * run)
    x = np.ones((1, 1))
    r1 = r2 = None
    hist, paid, made = [], 0.0, 0.0
    for _ in range(ROUNDS):
        fb1 = {} if r1 is None else {"reward": [r1], "done": [True]}
        fb2 = {} if r2 is None else {"reward": [r2], "done": [True]}
        c1 = MENU[int(t1.step(x, **fb1)[0])]
        c2 = MENU[int(t2.step(x, **fb2)[0])]
        row = table[int(rng.integers(len(table)))]
        p1, p2, v12 = credits(row, c1, c2, rule)
        paid += p1 + p2
        made += v12
        r1, r2 = SCALE * p1, SCALE * p2
        hist.append((c1, c2))
    t1.step(x, reward=[r1], done=[True]); t2.step(x, reward=[r2], done=[True])
    g = (MENU[int(t1.act(x, greedy=True)[0])], MENU[int(t2.act(x, greedy=True)[0])])
    late = hist[-300:]
    comp = np.mean([{a, b} == {"A", "B"} for a, b in late])
    bad = np.mean([a in "FS" or b in "FS" for a, b in late])
    first = next((i for i in range(len(hist) - 50)
                  if np.mean([{a, b} == {"A", "B"} for a, b in hist[i:i + 50]]) >= .8), None)
    return dict(greedy=g, comp=comp, bad=bad, first=first, paid=paid, made=made)


def main():
    table = load_table()
    print(f"EXP-20b  students in table={len(table)}  rounds={ROUNDS}  runs={RUNS}")
    for rule in ("shapley", "loo", "equal"):
        rs = [play(table, rule, r) for r in range(RUNS)]
        greedy_ok = sum({a, b} == {"A", "B"} for a, b in (r["greedy"] for r in rs))
        firsts = [r["first"] for r in rs if r["first"] is not None]
        print(f"{rule:8s} greedy end = key/door in {greedy_ok}/{RUNS} | last-300 key/door "
              f"{np.mean([r['comp'] for r in rs]):.2f} | lamp/spam {np.mean([r['bad'] for r in rs]):.2f} | "
              f"converged {len(firsts)}/{RUNS} (median round {int(np.median(firsts)) if firsts else '-'}) | "
              f"payout/value {sum(r['paid'] for r in rs)/max(1e-9, sum(r['made'] for r in rs)):.2f}",
              flush=True)
        for r in rs:
            print(f"   end {NAMES[r['greedy'][0]]}/{NAMES[r['greedy'][1]]}  comp {r['comp']:.2f}  "
                  f"bad {r['bad']:.2f}  first {r['first']}")


if __name__ == "__main__":
    main()
