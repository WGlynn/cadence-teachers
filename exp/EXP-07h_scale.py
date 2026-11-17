"""EXP-07h: does the episodic memory's lift hold as the number of situations grows, and does it carry anything to a
situation it never saw?

Pre-registered in experiments/EXP-07h.md before any data. Run: TAG=<sha> PER_SIT=<n> python -u exp/EXP-07h_scale.py
SMOKE=1 runs 30 moments of one seed per arm and size and prints only that each composes, trains and answers.
PILOT=1 times one MEM life at the largest size (moments in chunks, one exam) and prints timings only, no scores.

Task family: F features and C contexts; a situation (f, c) is a 2-hot input over F + C inputs (feature f, context c).
Every seed's rule is t(f, c) = g(f) XOR h(c) with g balanced over the features and h balanced over the contexts.
At (4, 2) this is EXP-07b's combination family. Sizes (4, 2), (8, 4), (16, 8): 8, 32, 128 situations.
Ceiling: pair the g=0 and g=1 features and the h=0 and h=1 contexts; each (feature pair, context pair) is a
quadruple of 4 situations with an XOR pattern, and the quadruples tile the table. No sum of input weights with a
threshold gets all 4 of an XOR quadruple right (the two right-sum pairs add to the same total), so on any union of
whole quadruples the ceiling is at most 3/4; "1 if g-class 0 or h-class 0" gets exactly 3/4. Held-out situations
are whole quadruples (none at 8, 1 at 32, 4 at 128), so the trained ceiling is exactly 3/4 and the held-out
targets are half 1, half 0 (chance .5; one answer for every cue scores exactly .5).
Arms add settings to the founder compose(inputs=F+C, actions=2, arousal=True):
  FOUNDER  control, nothing added
  MEM      memory_choice=True (EXP-07f/07g's MEM)
  MEMCTX0  memory_choice=True, memory_context=0.0 (EXP-07g's MEMCTX0)
Training: PER_SIT moments per trained situation on average, the situation drawn uniformly from the trained set each
moment, +1 right / -1 wrong given with the next moment (EXP-07g's contract). Greedy exam on a deepcopy per cue at
25%, 50% and 100% of the budget, every situation (trained and held out).
The JSON is written as .partial and renamed when the run finishes.
"""
import copy
import itertools
import json
import os
import sys
import time

import numpy as np

import cadence
from cadence import Brain

SEEDS = int(os.environ.get("SEEDS", "10"))
SMOKE = os.environ.get("SMOKE") == "1"
PILOT = os.environ.get("PILOT") == "1"
PER_SIT = int(os.environ.get("PER_SIT", "100"))
BASE = 7_080_000
SIZES = ((4, 2), (8, 4), (16, 8))
HOLD_QUADS = {8: 0, 32: 1, 128: 4}
FRACTIONS = (0.25, 0.5, 1.0)
ARMS = ("FOUNDER", "MEM", "MEMCTX0")
SETTINGS = {
    "FOUNDER": dict(),
    "MEM": dict(memory_choice=True),
    "MEMCTX0": dict(memory_choice=True, memory_context=0.0),
}
CEILING = 0.75
HERE = os.path.dirname(os.path.abspath(__file__))


def task(F, C, seed):
    """The rule, the quadruple tiling, the held-out quadruples and the trained cells for one seed and size."""
    rng = np.random.default_rng(seed)
    g = rng.permutation([0] * (F // 2) + [1] * (F // 2))
    h = rng.permutation([0] * (C // 2) + [1] * (C // 2))
    t = {(f, c): int(g[f] ^ h[c]) for f in range(F) for c in range(C)}
    r0, r1 = rng.permutation(np.flatnonzero(g == 0)), rng.permutation(np.flatnonzero(g == 1))
    c0, c1 = rng.permutation(np.flatnonzero(h == 0)), rng.permutation(np.flatnonzero(h == 1))
    quads = [[(int(a), int(x)), (int(a), int(y)), (int(b), int(x)), (int(b), int(y))]
             for a, b in zip(r0, r1) for x, y in zip(c0, c1)]
    n_hold = HOLD_QUADS[F * C]
    held_q = sorted(int(i) for i in rng.choice(len(quads), n_hold, replace=False)) if n_hold else []
    held = [cell for i in held_q for cell in quads[i]]
    trained = [cell for i, q in enumerate(quads) if i not in held_q for cell in q]
    return dict(g=g.tolist(), h=h.tolist(), t=t, quads=quads, held=held, trained=trained, rng=rng)


def check_ceiling(F, C, tk):
    """Assert the tiling and the exact 3/4 ceiling on the trained cells; returns (upper bound, construction)."""
    cells = {(f, c) for f in range(F) for c in range(C)}
    tiled = [cell for q in tk["quads"] for cell in q]
    assert len(tiled) == len(cells) and set(tiled) == cells, "quadruples do not tile the table"
    t = tk["t"]
    for (a, x), (a2, y), (b, x2), (b2, y2) in tk["quads"]:
        assert t[(a, x)] == t[(b, y2)] != t[(a, y)] == t[(b, x2)], "a quadruple is not an XOR pattern"
    n = len(tk["trained"])
    upper = (n - n // 4) / n                       # one error per whole quadruple, at least
    pred = {cell: int(tk["g"][cell[0]] == 0 or tk["h"][cell[1]] == 0) for cell in cells}
    best = max(sum(int((1 - pred[c] if flip else pred[c]) == t[c]) for c in tk["trained"]) for flip in (0, 1)) / n
    held = [t[c] for c in tk["held"]]
    assert sum(held) * 2 == len(held), "held-out targets are not half 1, half 0"
    return upper, best


def best_linear(F, C, tk):
    """Exhaustive linear-threshold ceiling over integer weights and bias in -3..3 (only feasible at F + C = 6)."""
    cells = [(f, c) for f in range(F) for c in range(C)]
    X = np.array([enc(F, C, cell)[0] for cell in cells])
    y = np.array([tk["t"][cell] for cell in cells], dtype=bool)
    n = F + C
    grid = np.array(list(itertools.product(range(-3, 4), repeat=n + 1)), dtype=float)
    act = (grid[:, :n] @ X.T + grid[:, n:n + 1]) > 0
    return int((act == y).sum(axis=1).max())


def enc(F, C, cell):
    v = np.zeros((1, F + C))
    v[0, cell[0]] = 1.0
    v[0, F + cell[1]] = 1.0
    return v


def compose(arm, F, C, seed):
    return Brain.compose(inputs=F + C, actions=2, arousal=True, seed=seed, **SETTINGS[arm])


def settings_read(arm, F, C):
    b = compose(arm, F, C, BASE)
    c = b.basal_ganglia.config
    ep = getattr(b, "_episodic", None)
    return dict(actor_eta=float(c.eta), actor_eta_bias=float(c.eta_bias), memory_choice=bool(b.memory_choice),
                memory_context=(float(ep.share) if ep is not None and hasattr(ep, "share") else None),
                backend=str(getattr(b, "backend", None)))


def moment(brain, obs, reward=None):
    """One training moment under the documented refusal contract (EXP-07g's helper, unchanged)."""
    for _ in range(5):
        try:
            if reward is None:
                return int(brain.live(obs)[0])
            return int(brain.live(obs, reward=np.array([float(reward)]))[0])
        except RuntimeError:
            if not brain.pending_feedback:
                reward = None
    raise RuntimeError("no settled answer in 5 tries")


def exam(brain, F, C, cells):
    return {cell: int(copy.deepcopy(brain).act(enc(F, C, cell), greedy=True)[0]) for cell in cells}


def run(arm, F, C, s, budget=None, checks=None, timing=False):
    seed = BASE + 100 * SIZES.index((F, C)) + s
    tk = task(F, C, seed)
    rng = tk["rng"]                                # continues after the task draws; same stream in every arm
    trained, held = tk["trained"], tk["held"]
    allc = trained + held
    total = budget if budget is not None else PER_SIT * len(trained)
    checks = checks or tuple(int(round(total * x)) for x in FRACTIONS)
    brain = compose(arm, F, C, seed)
    owed, exams, visits, times = None, {}, np.zeros(len(trained), dtype=int), []
    t_chunk = time.time()
    for k in range(1, total + 1):
        i = int(rng.integers(len(trained)))
        visits[i] += 1
        cell = trained[i]
        a = moment(brain, enc(F, C, cell), owed)
        owed = 1.0 if a == tk["t"][cell] else -1.0
        if timing and k % 500 == 0:
            times.append((k, time.time() - t_chunk))
            t_chunk = time.time()
        if k in checks:
            te = time.time()
            ans = exam(brain, F, C, allc)
            if timing:
                times.append(("exam", time.time() - te))
                t_chunk = time.time()
                continue
            tr = sum(int(ans[c] == tk["t"][c]) for c in trained) / len(trained)
            ho = (sum(int(ans[c] == tk["t"][c]) for c in held) / len(held)) if held else None
            exams[k] = dict(trained=tr, held=ho, one_answer=int(len(set(ans.values())) == 1),
                            ans=[ans[c] for c in allc])
    return dict(arm=arm, size=F * C, F=F, C=C, seed=seed, g=tk["g"], h=tk["h"], held=held, total=total,
                visits_min=int(visits.min()), visits_max=int(visits.max()), exams=exams, times=times)


def verdict(xs):
    n_beat = int(sum(1 for x in xs if x > CEILING))
    return ("LEARNS" if n_beat >= 7 else ("PARTIAL" if n_beat >= 3 else "FAILS")), n_beat


def sem(xs):
    xs = np.asarray(xs, dtype=float)
    return float(xs.std(ddof=1) / np.sqrt(len(xs))) if len(xs) > 1 else float("nan")


def main():
    t0 = time.time()
    mode = " (SMOKE)" if SMOKE else (" (PILOT)" if PILOT else "")
    print(f"EXP-07h on cadence {cadence.__version__}: sizes {[F * C for F, C in SIZES]}, arms {ARMS}, "
          f"{SEEDS} seeds, PER_SIT {PER_SIT}{mode}", flush=True)
    # ceiling checks for every seed and size, before any brain runs
    for F, C in SIZES:
        ups, bests = set(), set()
        for s in range(SEEDS):
            tk = task(F, C, BASE + 100 * SIZES.index((F, C)) + s)
            u, b = check_ceiling(F, C, tk)
            ups.add(round(u, 6)); bests.add(round(b, 6))
        lin = sorted({best_linear(F, C, task(F, C, BASE + s)) for s in range(SEEDS)}) if F + C == 6 else "n/a"
        print(f"  size {F * C}: trained ceiling upper bound {sorted(ups)}, construction {sorted(bests)}, "
              f"exhaustive linear (of {F * C}) {lin}", flush=True)
    if PILOT:
        F, C = SIZES[-1]
        r = run("MEM", F, C, 0, budget=2000, checks=(2000,), timing=True)
        for k, dt in r["times"]:
            print(f"  pilot MEM size {F * C}: {'exam of ' + str(F * C) + ' cues' if k == 'exam' else 'moments to ' + str(k)}"
                  f" {dt:.1f} s", flush=True)
        print(f"PILOT ok ({round(time.time() - t0)} s)")
        return 0
    rows = []
    for F, C in SIZES:
        for arm in ARMS:
            for s in range(1 if SMOKE else SEEDS):
                ts = time.time()
                if SMOKE:
                    run(arm, F, C, s, budget=30, checks=(30,))
                    print(f"  smoke {arm} size {F * C}: composed, trained 30 moments, answered {F * C} cues "
                          f"({time.time() - ts:.1f} s)", flush=True)
                    continue
                r = run(arm, F, C, s)
                rows.append(r)
                k = r["total"]
                e = r["exams"][k]
                curve = "  ".join(f"{kk}:{r['exams'][kk]['trained']:.3f}" for kk in sorted(r["exams"]))
                print(f"  {arm:<7} size {F * C:<3} seed {r['seed']}  trained {curve}  held {e['held']}  "
                      f"one-answer {e['one_answer']}  visits {r['visits_min']}-{r['visits_max']}  "
                      f"({time.time() - ts:.0f} s)", flush=True)
    read = {f"{arm}@{F * C}": settings_read(arm, F, C) for F, C in SIZES for arm in ARMS}
    for key, v in read.items():
        print(f"  settings {key:<12} {v}", flush=True)
    if SMOKE:
        print(f"SMOKE ok ({round(time.time() - t0)} s)")
        return 0
    out = {}
    for F, C in SIZES:
        n = F * C
        for arm in ARMS:
            rs = [r for r in rows if r["arm"] == arm and r["size"] == n]
            ks = sorted(rs[0]["exams"])
            d = {}
            for idx, k in enumerate(ks):
                tr = [r["exams"][k]["trained"] for r in rs]
                v, n_beat = verdict(tr)
                ho = [r["exams"][k]["held"] for r in rs] if rs[0]["exams"][k]["held"] is not None else None
                d[FRACTIONS[idx]] = dict(moments=k, trained_mean=float(np.mean(tr)), trained_sem=sem(tr), beat=n_beat,
                                         full=int(sum(1 for x in tr if x == 1.0)),
                                         one_answer=int(sum(r["exams"][k]["one_answer"] for r in rs)), verdict=v,
                                         held_mean=(float(np.mean(ho)) if ho else None), held_sem=(sem(ho) if ho else None))
            out[f"{arm}@{n}"] = d
            o = d[1.0]
            held_txt = (f"held {o['held_mean']:.3f} (SEM {o['held_sem']:.3f})" if o["held_mean"] is not None else "held n/a")
            print(f"{arm:<7} size {n:<3} @{o['moments']}: trained {o['trained_mean']:.3f} (SEM {o['trained_sem']:.3f})  "
                  f"above 3/4 {o['beat']}/{SEEDS}  all right {o['full']}/{SEEDS}  one answer {o['one_answer']}/{SEEDS}  "
                  f"-> {o['verdict']}  | {held_txt}  | curve "
                  + "  ".join(f"{d[x]['moments']}:{d[x]['trained_mean']:.3f}" for x in FRACTIONS), flush=True)
    print("VERDICTS at the full budget: " + "  ".join(f"{key}={v[1.0]['verdict']}" for key, v in out.items())
          + f"  ({round(time.time() - t0)} s)")
    tag = os.environ.get("TAG", "run")
    path = os.path.join(HERE, f"EXP-07h-{tag}.json")
    for r in rows:
        r["exams"] = {str(k): v for k, v in r["exams"].items()}
        r.pop("times", None)
    with open(path + ".partial", "w", encoding="utf-8") as f:
        json.dump(dict(version=cadence.__version__, per_sit=PER_SIT, settings=read,
                       checks={k: {str(x): y for x, y in v.items()} for k, v in out.items()}, rows=rows),
                  f, indent=1, default=float)
    os.replace(path + ".partial", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
