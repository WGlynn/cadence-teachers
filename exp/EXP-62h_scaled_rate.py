"""
EXP-62h: is the scaled exchange rate between early and late knowledge the same across brains?
EXP-62g's harness (imported: budget knob, labeller, twin) at budget 6, lesson 80. Instruments A (reference), C (EXP-62b's
near relative), D1 (EXP-62g's cross-family brain). Primary: s_I = mean(early - late) / mean(know-4 - null); pairs A-C and
A-D1, paired bootstrap over students. The pilot (24 students) sets N for an SE of about .05.
PRE-REGISTRATION: experiments/EXP-62h.md (written before any data).

    TAG=pilot WORKERS=4 python -u EXP-62h_scaled_rate.py
    TAG=full WORKERS=4 python -u EXP-62h_scaled_rate.py          (reads N from EXP-62h-pilot.json)
"""
import importlib.util, json, math, os, time
from dataclasses import replace
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("TAG", "pilot")
_spec = importlib.util.spec_from_file_location("e62g", os.path.join(HERE, "EXP-62g_budget_cross_family.py"))
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)                           # installs EXP-62f's labeller; set_budget, late_labels
F, E62, E58 = G.F, G.E62, G.F.E58

TAG = os.environ["TAG"]
WORKERS = int(os.environ.get("WORKERS", 4))
BUDGET, LESSON = 6, 80
SEED_BASE = 7_490_000 if TAG == "pilot" else 7_400_000
INSTRUMENTS = ("A", "C", "D1")
PAIRS = (("A", "C"), ("A", "D1"))
PILOT_N, SE_TARGET, N_MIN, N_MAX = 24, 0.05, 96, 720
BOOT, BOOT_SEED, EQ = 10_000, 62, 0.10


def compose_for(inst):
    import cadence as cd
    if inst == "A":
        return E58.compose
    if inst == "C":                                    # EXP-62b's C, unchanged
        O = dict(E58.OURS, modules=(64,), eta_critic=2.0)

        def c(seed):
            br = cd.Brain.compose(10, 5, modules=O["modules"], seed=int(seed), consolidation=O["consolidation"],
                                  working_memory_amplitude=O["working_memory_amplitude"],
                                  working_memory_scale=12.0, working_memory_decay=0.2)
            br.basal_ganglia.config = replace(br.basal_ganglia.config, **{k: O[k] for k in ("eta", "eta_bias", "lam", "gamma", "eta_critic")})
            return br
        return c
    if inst == "D1":
        return F.compose_for("D1")                     # EXP-62f / 62g's D1, unchanged
    raise ValueError(inst)


def run(job):
    inst, k = job
    import cadence as cd
    G.set_budget(BUDGET)
    E62.compose = compose_for(inst)
    t0 = time.time()
    seed = SEED_BASE + k
    arms = {"null": E62.twin(seed, LESSON, "random", seed + 2), "untaught": E62.twin(seed, LESSON, None, None)}
    for kind in F.TEACHERS:
        arms[kind] = E62.twin(seed, LESSON, kind, seed + 1)
    for a in arms.values():
        a["late_labels"] = G.late_labels(a)
        a.pop("actions", None)                         # keep the checkpoint small; accuracy and labels suffice
    out = dict(instrument=inst, student=k, seed=seed, lesson=LESSON, budget=BUDGET, arms=arms,
               secs=round(time.time() - t0, 1), cadence=cd.__version__)
    print(f"  {inst:2s} st{k:3d}: " + " ".join(f"{t} {a['acc']:.2f}" for t, a in arms.items()) + f" ({out['secs']}s)", flush=True)
    return out


def arrays(rows):
    by = {(r["instrument"], r["student"]): r for r in rows}
    S = sorted({r["student"] for r in rows if all((i, r["student"]) in by for i in INSTRUMENTS)})
    acc = lambda i, a: np.array([by[(i, k)]["arms"][a]["acc"] for k in S])
    D = {i: acc(i, "know-early-2") - acc(i, "know-late-2") for i in INSTRUMENTS}
    K = {i: acc(i, "know-4") - acc(i, "null") for i in INSTRUMENTS}
    E = {i: acc(i, "know-early-2") - acc(i, "null") for i in INSTRUMENTS}
    L = {i: acc(i, "know-late-2") - acc(i, "null") for i in INSTRUMENTS}
    U = {i: acc(i, "untaught") for i in INSTRUMENTS}
    return S, D, K, E, L, U, by


def analyse(rows):
    S, D, K, E, L, U, by = arrays(rows)
    n = len(S)
    idx = np.random.default_rng(BOOT_SEED).integers(0, n, size=(BOOT, n))
    s = {i: float(D[i].mean() / K[i].mean()) for i in INSTRUMENTS}
    sb = {i: D[i][idx].mean(axis=1) / K[i][idx].mean(axis=1) for i in INSTRUMENTS}
    sem = lambda x: float(np.std(x, ddof=1) / np.sqrt(len(x)))
    o = dict(n=n, instruments={}, pairs={})
    for i in INSTRUMENTS:
        o["instruments"][i] = dict(s=s[i], know4=(float(K[i].mean()), sem(K[i])), D=(float(D[i].mean()), sem(D[i])),
                                   early=float(E[i].mean()), late=float(L[i].mean()), late_over_early=float(L[i].mean() / E[i].mean()),
                                   untaught=float(U[i].mean()),
                                   late_labels={a: float(np.mean([by[(i, k)]["arms"][a]["late_labels"] for k in S]))
                                                for a in ("know-early-2", "know-late-2", "know-4")})
    for a, b in PAIRS:
        d = sb[b] - sb[a]
        lo, hi = np.percentile(d, [2.5, 97.5])
        o["pairs"][f"{a}-{b}"] = dict(diff=s[b] - s[a], se=float(np.std(d, ddof=1)), lo=float(lo), hi=float(hi),
                                      excludes_0=bool(lo > 0 or hi < 0), inside_eq=bool(lo > -EQ and hi < EQ),
                                      raw_D_diff=float((D[b] - D[a]).mean()))
    return o


def report(o):
    for i, v in o["instruments"].items():
        print(f"  [{i}] n={o['n']} s = D/know-4 {v['s']:+.3f} | know-4 {v['know4'][0]:+.3f} ({v['know4'][1]:.3f}) | D {v['D'][0]:+.3f} "
              f"({v['D'][1]:.3f}) | late/early {v['late_over_early']:+.3f} | untaught {v['untaught']:.3f} | late labels {v['late_labels']}")
    for p, q in o["pairs"].items():
        print(f"  pair {p}: s diff {q['diff']:+.3f} (SE {q['se']:.3f}, 95% [{q['lo']:+.3f}, {q['hi']:+.3f}]) excludes 0: {q['excludes_0']}; "
              f"inside +-{EQ}: {q['inside_eq']} | raw D diff {q['raw_D_diff']:+.3f}")


def main():
    t0 = time.time()
    if TAG == "pilot":
        N = PILOT_N
    else:
        pj = os.path.join(HERE, "EXP-62h-pilot.json")
        if not os.path.exists(pj):
            raise SystemExit("run the pilot first: the full run reads N from EXP-62h-pilot.json")
        P = json.load(open(pj))
        if P["N"] is None:
            raise SystemExit(f"the pilot stopped the full run: {P['stop']}")
        N = int(P["N"])
    ckpt = os.path.join(HERE, f"EXP-62h-{TAG}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["instrument"], r["student"]) for r in rows}
    jobs = [(i, k) for k in range(N) for i in INSTRUMENTS if (i, k) not in done]
    print(f"EXP-62h [{TAG}]: N {N}, budget {BUDGET}, lesson {LESSON}; {len(jobs)} jobs to go ({len(done)} done); seeds {SEED_BASE}+",
          flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as fh:
                    fh.write(json.dumps(r) + "\n")
    rows = [r for r in rows if r["student"] < N]
    print(f"\nEXP-62h [{TAG}] summary ({time.time() - t0:.0f}s)")
    o = analyse(rows)
    if TAG == "pilot":
        ceil = [i for i, v in o["instruments"].items() if v["untaught"] >= 0.90]
        blind = [i for i, v in o["instruments"].items() if v["know4"][0] < 0.10 or v["know4"][0] < 2 * v["know4"][1]]
        se = max(q["se"] for q in o["pairs"].values())
        n = int(math.ceil(PILOT_N * (se / SE_TARGET) ** 2 / 24) * 24)
        N_full = None if (ceil or blind) else int(min(max(n, N_MIN), N_MAX))
        stop = (f"ceiling {ceil}" if ceil else "") + (f" blind {blind}" if blind else "")
        for i, v in o["instruments"].items():                     # validity only; the pilot's differences are not reported
            print(f"  [{i}] untaught {v['untaught']:.3f} | know-4 worth {v['know4'][0]:+.3f} ({v['know4'][1]:.3f})")
        print(f"  pilot rule: largest pair SE {se:.3f} -> N {n} -> {N_full if N_full else 'STOP: ' + stop}")
        json.dump(dict(N=N_full, se=se, raw_n=n, stop=stop or None, validity={i: dict(untaught=v["untaught"], know4=v["know4"])
                                                                              for i, v in o["instruments"].items()}),
                  open(os.path.join(HERE, "EXP-62h-pilot.json"), "w"))
        return
    report(o)
    pr = o["pairs"]
    if any(q["excludes_0"] for q in pr.values()):
        verdict = "RATE DEPENDS ON THE BRAIN"
    elif all(q["inside_eq"] for q in pr.values()):
        verdict = "RATE AGREES"
    else:
        verdict = "INCONCLUSIVE"
    o["verdict"] = verdict
    print(f"  VERDICT: {verdict}")
    json.dump(o, open(os.path.join(HERE, "EXP-62h-full.json"), "w"))


if __name__ == "__main__":
    main()
