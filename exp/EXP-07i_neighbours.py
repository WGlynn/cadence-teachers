"""EXP-07i: does the episodic memory carry anything to an unseen situation when similar situations share answers,
and how does it compare with a plain lookup table?

Pre-registered in experiments/EXP-07i.md before any data. Run: TAG=<sha> python -u exp/EXP-07i_neighbours.py
CHECK=1 builds every seed's rule and prints the rule-level checks only (ceilings, neighbour references); no brain.
SMOKE=1 runs 30 moments of one seed per arm and size and prints only that each composes, trains and answers.
PILOT=1 times one FOUNDER and one MEMCTX0 life at size 128 (moments in chunks, one exam) and prints timings only.
XOR=0 skips the optional arm (the pilot's budget rule decides whether it runs).

Task family (regular rule with context exceptions): F features and C contexts; a situation (f, c) is a 2-hot input
over F + C inputs. g is balanced over the features, h over the contexts. Pairing the g = 0 with the g = 1 features
and the h = 0 with the h = 1 contexts tiles the table with quadruples {a, b} x {x, y}, g(a) = 0, g(b) = 1, h(x) = 0,
h(y) = 1 (EXP-07h's tiling). The regular rule is t = g(f): the answer follows the feature. In a few "exception"
quadruples the context y reverses it for both features (t(a, y) = 1, t(b, y) = 0), so inside them t = g XOR h.
Sizes (8, 4) and (16, 8): 32 and 128 situations; 2 and 8 exception quadruples; 1 and 4 held-out quadruples, drawn
from the regular ones, so held-out targets are half 1 and half 0 and every held-out situation's feature neighbours
share its answer except where an exception sits in that row.
Ceiling: a sum of input weights with a threshold on these 2-hot inputs answers 1 where w_f + v_c + b > 0, which is
exactly a table whose rows are prefixes of one common column order. The script finds the best such table on the
trained cells by trying every column order (C! orders, each row then picks its best prefix), so the ceiling is exact
per seed. Checked: equals 3/4 on EXP-07h's XOR family, and equals an integer-weight search on random 4 x 2 tables.
Arms:
  TABLE    a plain table keyed on the situation: the last rewarded answer, a random answer when it has none
  FOUNDER  Brain.compose(inputs=F+C, actions=2, arousal=True), nothing added
  MEMCTX0  the same plus memory_choice=True, memory_context=0.0 (EXP-07g/07h's MEMCTX0)
  MEMORY   (diagnostic, not an arm) MEMCTX0's place records alone at each exam: the sign of the records' vote for
           action 1 over action 0, read on a copy (the read is pure); an exact tie scores 1/2
Optional (XOR): MEMCTX0 at 128 situations on EXP-07h's XOR rules and seeds with 100 moments per trained situation,
through EXP-07h's own run function, so its first 5600 moments are EXP-07h's run; exams at 2800, 5600, 11200.
Training: PER_SIT = 50 moments per trained situation on average, the situation drawn uniformly from the trained set
each moment, +1 right / -1 wrong given with the next moment (EXP-07g's contract). Greedy exam of every situation on a
deepcopy per cue at 25%, 50% and 100% of the budget. Seeds 7_090_000 + 100 x size index + s.
The JSON is written as .partial and renamed when the run finishes.
"""
import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_k] = "1"  # BLAS threads pinned to 1, before NumPy loads

import copy  # noqa: E402
import importlib.util  # noqa: E402
import itertools  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402

import cadence  # noqa: E402
from cadence import Brain  # noqa: E402

SEEDS = int(os.environ.get("SEEDS", "10"))
CHECK = os.environ.get("CHECK") == "1"
SMOKE = os.environ.get("SMOKE") == "1"
PILOT = os.environ.get("PILOT") == "1"
XOR = os.environ.get("XOR", "1") == "1"
PER_SIT = 50
XOR_PER_SIT = 100
BASE = 7_090_000
SIZES = ((8, 4), (16, 8))
HOLD_QUADS = {32: 1, 128: 4}
EXCEPT_QUADS = {32: 2, 128: 8}
FRACTIONS = (0.25, 0.5, 1.0)
ARMS = ("TABLE", "FOUNDER", "MEMCTX0")
SETTINGS = {"FOUNDER": dict(), "MEMCTX0": dict(memory_choice=True, memory_context=0.0)}
BUDGET_MIN = 75.0  # the optional XOR arm runs if the pilot's projection of everything is at most this many minutes
HERE = os.path.dirname(os.path.abspath(__file__))


def exp07h():
    """EXP-07h's script as a module (its rule family, seeds and run function, unchanged)."""
    spec = importlib.util.spec_from_file_location("exp07h", os.path.join(HERE, "EXP-07h_scale.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def task(F, C, seed):
    """The rule, the tiling, the exception and held-out quadruples and the trained cells for one seed and size."""
    rng = np.random.default_rng(seed)
    g = rng.permutation([0] * (F // 2) + [1] * (F // 2))
    h = rng.permutation([0] * (C // 2) + [1] * (C // 2))
    r0, r1 = rng.permutation(np.flatnonzero(g == 0)), rng.permutation(np.flatnonzero(g == 1))
    c0, c1 = rng.permutation(np.flatnonzero(h == 0)), rng.permutation(np.flatnonzero(h == 1))
    quads = [[(int(a), int(x)), (int(a), int(y)), (int(b), int(x)), (int(b), int(y))]
             for a, b in zip(r0, r1) for x, y in zip(c0, c1)]
    n = F * C
    order = [int(i) for i in rng.permutation(len(quads))]
    held_q = sorted(order[:HOLD_QUADS[n]])
    exc_q = sorted(order[HOLD_QUADS[n]:HOLD_QUADS[n] + EXCEPT_QUADS[n]])
    t = {(f, c): int(g[f]) for f in range(F) for c in range(C)}
    for i in exc_q:
        for f, c in quads[i]:
            if h[c] == 1:
                t[(f, c)] = 1 - int(g[f])
    held = [cell for i in held_q for cell in quads[i]]
    trained = [cell for i, q in enumerate(quads) if i not in held_q for cell in q]
    exceptions = [cell for cell in trained if t[cell] != g[cell[0]]]
    return dict(g=g.tolist(), h=h.tolist(), t=t, quads=quads, held_q=held_q, exc_q=exc_q, held=held,
                trained=trained, exceptions=exceptions, rng=rng)


def additive_ceiling(F, C, t, cells):
    """Exact best accuracy on ``cells`` of 1[w_f + v_c + b > 0]: rows are prefixes of one common column order."""
    T = np.zeros((F, C), dtype=int)
    M = np.zeros((F, C), dtype=bool)
    for f, c in cells:
        M[f, c] = True
        T[f, c] = t[(f, c)]
    delta = np.where(M, np.where(T == 0, 1, -1), 0)   # change in errors when a cell is answered 1 instead of 0
    base = (M & (T == 1)).sum(axis=1)                  # each row's errors when it answers 0 everywhere
    perms = np.array(list(itertools.permutations(range(C))))
    cs = np.cumsum(delta[:, perms], axis=2)             # (F, orders, C)
    err = (base[:, None] + np.minimum(0, cs.min(axis=2))).sum(axis=0).min()
    return (len(cells) - int(err)) / len(cells)


def enc(F, C, cell):
    v = np.zeros((1, F + C))
    v[0, cell[0]] = 1.0
    v[0, F + cell[1]] = 1.0
    return v


def int_search(F, C, t):
    """Integer weights and bias in -3..3 over all cells (EXP-07b/07h's search); only for F + C = 6."""
    cells = [(f, c) for f in range(F) for c in range(C)]
    X = np.array([enc(F, C, cell)[0] for cell in cells])
    y = np.array([t[cell] for cell in cells], dtype=bool)
    n = F + C
    grid = np.array(list(itertools.product(range(-3, 4), repeat=n + 1)), dtype=float)
    act = (grid[:, :n] @ X.T + grid[:, n:n + 1]) > 0
    return int((act == y).sum(axis=1).max()) / len(cells)


def neighbour_refs(tk):
    """Rule-level references for the held-out cells: the majority answer of the trained cells sharing the feature
    (row) and of those sharing the feature or the context (row and column); a tie scores 1/2."""
    t, trained = tk["t"], set(tk["trained"])
    out = {}
    for name in ("row", "row_col"):
        sc = []
        for f, c in tk["held"]:
            nb = [cell for cell in trained if cell[0] == f or (name == "row_col" and cell[1] == c)]
            ones = sum(t[cell] for cell in nb)
            pred = 0.5 if 2 * ones == len(nb) else float(2 * ones > len(nb))
            sc.append(1.0 - abs(pred - t[(f, c)]))
        out[name] = float(np.mean(sc))
    return out


def rule_checks(F, C, s):
    """Assert the construction for one seed and size; return its ceilings and references."""
    seed = BASE + 100 * SIZES.index((F, C)) + s
    tk = task(F, C, seed)
    t, g, h = tk["t"], tk["g"], tk["h"]
    cells = {(f, c) for f in range(F) for c in range(C)}
    tiled = [cell for q in tk["quads"] for cell in q]
    assert len(tiled) == len(cells) and set(tiled) == cells, "quadruples do not tile the table"
    for i in tk["exc_q"]:
        (a, x), (a2, y), (b, x2), (b2, y2) = tk["quads"][i]
        assert t[(a, x)] == t[(b, y2)] != t[(a, y)] == t[(b, x2)], "an exception quadruple is not an XOR pattern"
    held_t = [t[c] for c in tk["held"]]
    assert sum(held_t) * 2 == len(held_t), "held-out targets are not half 1, half 0"
    assert all(t[c] == g[c[0]] for c in tk["held"]), "a held-out cell is an exception"
    tr_f, tr_c = {c[0] for c in tk["trained"]}, {c[1] for c in tk["trained"]}
    assert all(c[0] in tr_f and c[1] in tr_c for c in tk["held"]), "a held-out feature or context is never trained"
    n = len(tk["trained"])
    ceil = additive_ceiling(F, C, t, tk["trained"])
    lo, hi = 1 - len(tk["exceptions"]) / n, 1 - len(tk["exc_q"]) / n
    assert lo - 1e-9 <= ceil <= hi + 1e-9, "ceiling outside its bounds"
    return dict(seed=seed, ceiling=ceil, g_only=lo, one_per_quad=hi, n_trained=n,
                n_exceptions=len(tk["exceptions"]), refs=neighbour_refs(tk))


def validate_ceiling():
    """The ceiling search against two references: 3/4 on EXP-07h's XOR rules, and the integer search at 4 x 2."""
    m = exp07h()
    xs = []
    for F, C in m.SIZES:
        for s in range(SEEDS):
            tk = m.task(F, C, m.BASE + 100 * m.SIZES.index((F, C)) + s)
            xs.append(additive_ceiling(F, C, tk["t"], tk["trained"]))
    rng = np.random.default_rng(7_090_999)
    agree = 0
    for _ in range(40):
        tab = {(f, c): int(rng.integers(2)) for f in range(4) for c in range(2)}
        allc = list(tab)
        agree += int(abs(additive_ceiling(4, 2, tab, allc) - int_search(4, 2, tab)) < 1e-9)
    return sorted(set(round(x, 6) for x in xs)), agree


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


def memory_votes(brain, F, C, cells):
    """The place records' vote for action 1 minus action 0 on each cell, read on a copy (no temporal key)."""
    b = copy.deepcopy(brain)
    out = {}
    for cell in cells:
        v = np.asarray(b._episodic.vote(b._placed(enc(F, C, cell)), None), dtype=float).reshape(-1)
        out[cell] = float(v[1] - v[0])
    return out


def score(ans, t, cells):
    """Mean score; an answer of 0.5 (a tie) scores 1/2."""
    return float(np.mean([1.0 - abs(ans[c] - t[c]) for c in cells])) if cells else None


def summarise(ans, tk):
    t = tk["t"]
    regular = [c for c in tk["trained"] if c not in set(tk["exceptions"])]
    return dict(trained=score(ans, t, tk["trained"]), held=score(ans, t, tk["held"]),
                exceptions=score(ans, t, tk["exceptions"]), regular=score(ans, t, regular),
                one_answer=int(len(set(ans.values())) == 1))


def run(arm, F, C, s, budget=None, checks=None, timing=False):
    seed = BASE + 100 * SIZES.index((F, C)) + s
    tk = task(F, C, seed)
    rng = tk["rng"]                                # continues after the task draws; same stream in every arm
    trained, held = tk["trained"], tk["held"]
    allc = trained + held
    total = budget if budget is not None else PER_SIT * len(trained)
    checks = checks or tuple(int(round(total * x)) for x in FRACTIONS)
    brain = None if arm == "TABLE" else compose(arm, F, C, seed)
    table, act_rng = {}, np.random.default_rng([seed, 1])
    owed, exams, visits, times = None, {}, np.zeros(len(trained), dtype=int), []
    t_chunk = time.time()
    for k in range(1, total + 1):
        i = int(rng.integers(len(trained)))
        visits[i] += 1
        cell = trained[i]
        if arm == "TABLE":
            a = table.get(cell)
            a = int(act_rng.integers(2)) if a is None else a
            if a == tk["t"][cell]:
                table[cell] = a                    # +1: keep the rewarded answer
            elif table.get(cell) == a:
                del table[cell]                    # -1 on the kept answer: forget it (never happens on this rule)
        else:
            a = moment(brain, enc(F, C, cell), owed)
            owed = 1.0 if a == tk["t"][cell] else -1.0
        if timing and k % 500 == 0:
            times.append((k, time.time() - t_chunk))
            t_chunk = time.time()
        if k in checks:
            te = time.time()
            if arm == "TABLE":
                ex_rng = np.random.default_rng([seed, 2, k])
                ans = {c: (table[c] if c in table else int(ex_rng.integers(2))) for c in allc}
            else:
                ans = exam(brain, F, C, allc)
            e = summarise(ans, tk)
            e["ans"] = [ans[c] for c in allc]
            if arm == "MEMCTX0":
                v = memory_votes(brain, F, C, allc)
                mans = {c: (0.5 if abs(v[c]) < 1e-12 else float(v[c] > 0)) for c in allc}
                e["memory"] = summarise(mans, tk)
                e["memory"].pop("one_answer")
                e["memory_ties"] = int(sum(1 for c in allc if mans[c] == 0.5))
                e["memory_vote"] = [v[c] for c in allc]
            if timing:
                times.append(("exam", time.time() - te))
                t_chunk = time.time()
                continue
            exams[k] = e
    return dict(arm=arm, size=F * C, F=F, C=C, seed=seed, g=tk["g"], h=tk["h"], held=held,
                exceptions=tk["exceptions"], total=total, visits_min=int(visits.min()),
                visits_max=int(visits.max()), exams=exams, times=times)


def sem(xs):
    xs = np.asarray(xs, dtype=float)
    return float(xs.std(ddof=1) / np.sqrt(len(xs))) if len(xs) > 1 else float("nan")


def ceiling_verdict(xs, ceils):
    n_beat = int(sum(1 for x, c in zip(xs, ceils) if x > c + 1e-9))
    return ("LEARNS" if n_beat >= 7 else ("PARTIAL" if n_beat >= 3 else "FAILS")), n_beat


def carry(m, se):
    if m > 0.5 + 2 * se:
        return "CARRIES"
    if m < 0.5 - 2 * se:
        return "BELOW"
    return "CHANCE"


def main():
    t0 = time.time()
    mode = " (CHECK)" if CHECK else (" (SMOKE)" if SMOKE else (" (PILOT)" if PILOT else ""))
    print(f"EXP-07i on cadence {cadence.__version__}: sizes {[F * C for F, C in SIZES]}, arms {ARMS}, "
          f"{SEEDS} seeds, PER_SIT {PER_SIT}, XOR arm {'on' if XOR else 'off'}{mode}", flush=True)
    xor_ceils, agree = validate_ceiling()
    print(f"  ceiling search: EXP-07h XOR rules {xor_ceils} (want [0.75]); integer search agrees on {agree}/40 "
          f"random 4 x 2 tables", flush=True)
    assert xor_ceils == [0.75] and agree == 40, "the ceiling search fails its references"
    rules = {}
    for F, C in SIZES:
        rs = [rule_checks(F, C, s) for s in range(SEEDS)]
        rules[F * C] = rs
        print(f"  size {F * C}: trained {rs[0]['n_trained']}, exceptions {rs[0]['n_exceptions']}, held "
              f"{HOLD_QUADS[F * C] * 4}; additive ceiling per seed {[round(r['ceiling'], 3) for r in rs]} "
              f"(g alone {rs[0]['g_only']:.3f}, one error per exception quadruple {rs[0]['one_per_quad']:.3f}); "
              f"held-out by the feature majority {np.mean([r['refs']['row'] for r in rs]):.3f}, by the feature and "
              f"context majority {np.mean([r['refs']['row_col'] for r in rs]):.3f}", flush=True)
    if CHECK:
        print(f"CHECK ok ({round(time.time() - t0)} s)")
        return 0
    if PILOT:
        F, C = SIZES[-1]
        rate = {}
        for arm in ("FOUNDER", "MEMCTX0"):
            r = run(arm, F, C, 0, budget=2000, checks=(2000,), timing=True)
            for k, dt in r["times"]:
                print(f"  pilot {arm} size {F * C}: "
                      f"{'exam of ' + str(F * C) + ' cues' if k == 'exam' else 'moments to ' + str(k)} {dt:.1f} s",
                      flush=True)
            mom = sum(dt for k, dt in r["times"] if k != "exam")
            rate[arm] = (mom / 2000, [dt for k, dt in r["times"] if k == "exam"][0] / (F * C))
        main_s = sum(SEEDS * (PER_SIT * (n - 4 * HOLD_QUADS[n]) * rate[arm][0] + 3 * n * rate[arm][1])
                     for n in (32, 128) for arm in ("FOUNDER", "MEMCTX0"))
        xor_s = SEEDS * (XOR_PER_SIT * 112 * rate["MEMCTX0"][0] + 3 * 128 * rate["MEMCTX0"][1])
        print(f"  projection: main {main_s / 60:.1f} min, optional XOR arm {xor_s / 60:.1f} min, total "
              f"{(main_s + xor_s) / 60:.1f} min; rule: XOR arm runs if the total is at most {BUDGET_MIN:.0f} min "
              f"-> {'RUN' if (main_s + xor_s) / 60 <= BUDGET_MIN else 'SKIP'}", flush=True)
        print(f"PILOT ok ({round(time.time() - t0)} s)")
        return 0
    rows = []
    for F, C in SIZES:
        for arm in ARMS:
            for s in range(1 if SMOKE else SEEDS):
                ts = time.time()
                if SMOKE:
                    r = run(arm, F, C, s, budget=30, checks=(30,))
                    mem = " memory read ok" if arm == "MEMCTX0" and "memory" in r["exams"][30] else ""
                    print(f"  smoke {arm} size {F * C}: composed, trained 30 moments, answered {F * C} cues{mem} "
                          f"({time.time() - ts:.1f} s)", flush=True)
                    continue
                r = run(arm, F, C, s)
                rows.append(r)
                e = r["exams"][r["total"]]
                curve = "  ".join(f"{kk}:{r['exams'][kk]['trained']:.3f}" for kk in sorted(r["exams"]))
                mem = (f"  memory trained {e['memory']['trained']:.3f} exc {e['memory']['exceptions']:.3f} held "
                       f"{e['memory']['held']:.3f} ties {e['memory_ties']}") if "memory" in e else ""
                print(f"  {arm:<7} size {F * C:<3} seed {r['seed']}  trained {curve}  exc {e['exceptions']:.3f}  "
                      f"held {e['held']:.3f}  one-answer {e['one_answer']}{mem}  visits {r['visits_min']}-"
                      f"{r['visits_max']}  ({time.time() - ts:.0f} s)", flush=True)
    xor_rows = []
    if XOR and not SMOKE:
        m = exp07h()
        ref = json.load(open(os.path.join(HERE, "EXP-07h-3961509.json"), encoding="utf-8"))
        refrows = {r["seed"]: r for r in ref["rows"] if r["arm"] == "MEMCTX0" and r["size"] == 128}
        F, C = m.SIZES[-1]
        for s in range(SEEDS):
            ts = time.time()
            r = m.run("MEMCTX0", F, C, s, budget=XOR_PER_SIT * 112, checks=(2800, 5600, 11200))
            same = {k: r["exams"][k]["ans"] == refrows[r["seed"]]["exams"][str(k)]["ans"] for k in (2800, 5600)}
            r.pop("times", None)
            r["same_as_07h"] = same
            xor_rows.append(r)
            curve = "  ".join(f"{kk}:{r['exams'][kk]['trained']:.3f}" for kk in sorted(r["exams"]))
            print(f"  XOR MEMCTX0 size 128 seed {r['seed']}  trained {curve}  answers as EXP-07h at 2800 "
                  f"{same[2800]}, 5600 {same[5600]}  ({time.time() - ts:.0f} s)", flush=True)
    read = {f"{arm}@{F * C}": settings_read(arm, F, C) for F, C in SIZES for arm in ARMS if arm != "TABLE"}
    for key, v in read.items():
        print(f"  settings {key:<12} {v}", flush=True)
    if SMOKE:
        print(f"SMOKE ok ({round(time.time() - t0)} s)")
        return 0
    out = {}
    for F, C in SIZES:
        n = F * C
        ceils = [r["ceiling"] for r in rules[n]]
        for arm in ARMS + ("MEMORY",):
            rs = [r for r in rows if r["arm"] == (arm if arm != "MEMORY" else "MEMCTX0") and r["size"] == n]
            ks = sorted(rs[0]["exams"])
            d = {}
            for idx, k in enumerate(ks):
                es = [(r["exams"][k]["memory"] if arm == "MEMORY" else r["exams"][k]) for r in rs]
                tr = [e["trained"] for e in es]
                ho = [e["held"] for e in es]
                v, n_beat = ceiling_verdict(tr, ceils)
                d[FRACTIONS[idx]] = dict(
                    moments=k, trained_mean=float(np.mean(tr)), trained_sem=sem(tr), beat=n_beat, verdict=v,
                    full=int(sum(1 for x in tr if x == 1.0)),
                    one_answer=(int(sum(e["one_answer"] for e in es)) if arm != "MEMORY" else None),
                    exceptions_mean=float(np.mean([e["exceptions"] for e in es])),
                    regular_mean=float(np.mean([e["regular"] for e in es])),
                    held_mean=float(np.mean(ho)), held_sem=sem(ho), carry=carry(float(np.mean(ho)), sem(ho)),
                    ties=(int(sum(r["exams"][k]["memory_ties"] for r in rs)) if arm == "MEMORY" else None))
            out[f"{arm}@{n}"] = d
            o = d[1.0]
            print(f"{arm:<7} size {n:<3} @{o['moments']}: trained {o['trained_mean']:.3f} (SEM {o['trained_sem']:.3f})  "
                  f"above ceiling {o['beat']}/{SEEDS} -> {o['verdict']}  all right {o['full']}/{SEEDS}  "
                  f"one answer {o['one_answer']}  exceptions {o['exceptions_mean']:.3f}  regular "
                  f"{o['regular_mean']:.3f}  | held {o['held_mean']:.3f} (SEM {o['held_sem']:.3f}) -> {o['carry']}"
                  + (f"  ties {o['ties']}" if o["ties"] is not None else "")
                  + "  | curve " + "  ".join(f"{d[x]['moments']}:{d[x]['trained_mean']:.3f}/{d[x]['held_mean']:.3f}"
                                             for x in FRACTIONS), flush=True)
        # paired differences at the full budget (registered readings)
        def full(arm, key):
            src = "MEMCTX0" if arm == "MEMORY" else arm
            rs = sorted((r for r in rows if r["arm"] == src and r["size"] == n), key=lambda r: r["seed"])
            return np.array([(r["exams"][r["total"]]["memory"] if arm == "MEMORY" else r["exams"][r["total"]])[key]
                             for r in rs])
        for a, b, key in (("TABLE", "MEMCTX0", "trained"), ("MEMCTX0", "FOUNDER", "held"),
                          ("MEMCTX0", "FOUNDER", "trained"), ("MEMORY", "MEMCTX0", "held")):
            dd = full(a, key) - full(b, key)
            out[f"diff {a}-{b} {key}@{n}"] = dict(mean=float(dd.mean()), sem=sem(dd))
            print(f"  paired {a} minus {b} on {key} at {n}: {dd.mean():+.3f} (SEM {sem(dd):.3f})", flush=True)
    if xor_rows:
        acc = {k: np.array([r["exams"][k]["trained"] for r in xor_rows]) for k in (2800, 5600, 11200)}
        gain = acc[11200] - acc[5600]
        out["XOR@128"] = dict({str(k): dict(mean=float(v.mean()), sem=sem(v)) for k, v in acc.items()},
                              gain=dict(mean=float(gain.mean()), sem=sem(gain)),
                              same_as_07h={str(k): int(sum(r["same_as_07h"][k] for r in xor_rows)) for k in (2800, 5600)})
        print(f"XOR MEMCTX0 size 128: trained 2800 {acc[2800].mean():.3f}, 5600 {acc[5600].mean():.3f} "
              f"(SEM {sem(acc[5600]):.3f}), 11200 {acc[11200].mean():.3f} (SEM {sem(acc[11200]):.3f}); paired gain "
              f"{gain.mean():+.3f} (SEM {sem(gain):.3f}); answers as EXP-07h on "
              f"{out['XOR@128']['same_as_07h']['2800']}/{SEEDS} at 2800, {out['XOR@128']['same_as_07h']['5600']}/{SEEDS} "
              f"at 5600", flush=True)
    print("VERDICTS at the full budget: " + "  ".join(f"{key}={v[1.0]['verdict']}/{v[1.0]['carry']}"
                                                      for key, v in out.items() if isinstance(v, dict) and 1.0 in v)
          + f"  ({round(time.time() - t0)} s)")
    tag = os.environ.get("TAG", "run")
    path = os.path.join(HERE, f"EXP-07i-{tag}.json")
    for r in rows + xor_rows:
        r["exams"] = {str(k): v for k, v in r["exams"].items()}
        r.pop("times", None)
    with open(path + ".partial", "w", encoding="utf-8") as f:
        json.dump(dict(version=cadence.__version__, per_sit=PER_SIT, xor_per_sit=XOR_PER_SIT, settings=read,
                       rules={str(k): v for k, v in rules.items()},
                       checks={k: ({str(x): y for x, y in v.items()} if 1.0 in v else v) for k, v in out.items()},
                       rows=rows, xor_rows=xor_rows), f, indent=1, default=float)
    os.replace(path + ".partial", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
