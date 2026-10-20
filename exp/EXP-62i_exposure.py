"""
EXP-62i: is the delayed-credit brain's low price for late knowledge a matter of exposure?
EXP-62h's harness (imported: budget 6, lesson 80, teachers, null, untaught, instruments) for A and D1, in two conditions:
off (EXP-62h exactly) and on (a stage-3 scaffold: every other lesson attempt starts with wood and stone done).
Primary: phi_A = (R(A,on) - R(A,off)) / (R(D1,off) - R(A,off)), R = mean(late worth) / mean(early worth), paired bootstrap.
PRE-REGISTRATION: experiments/EXP-62i.md (written before any EXP-62i data).

    TAG=check python -u EXP-62i_exposure.py               identity gate + scaffold self-check (prints no scaffolded accuracy)
    TAG=pilot WORKERS=4 python -u EXP-62i_exposure.py
    TAG=full WORKERS=4 python -u EXP-62i_exposure.py      (reads N and the scaffold share from EXP-62i-pilot.json)
"""
import importlib.util, json, math, os, time
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("TAG", "pilot")
_spec = importlib.util.spec_from_file_location("e62h", os.path.join(HERE, "EXP-62h_scaled_rate.py"))
H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(H)                           # EXP-62h: compose_for, and through it 62g / 62f / 62 / 49
G, E62 = H.G, H.E62
E49 = E62.E49

TAG = os.environ["TAG"]
WORKERS = int(os.environ.get("WORKERS", 4))
BUDGET, LESSON = 6, 80
SEED_BASE = 7_590_000 if TAG == "pilot" else 7_500_000
INSTRUMENTS = ("A", "D1")
CONDITIONS = ("off", "on")
SHARE = float(os.environ.get("SHARE", 0.5))           # 0.5 = every other attempt; 0.75 = the pre-registered fallback
PILOT_N, SE_TARGET, N_MIN, N_MAX = 24, 0.10, 96, 720
BOOT, BOOT_SEED, HALF = 10_000, 62, 0.5


def scaffolded(j, share):
    if share == 0.5:
        return j % 2 == 1
    if share == 0.75:
        return j % 4 != 0
    if share == 0.0:
        return False
    raise ValueError(share)


def live_scaffold(brain, attempts, rng, label, share):
    """EXP-49's live_world (V5's continuing-life loop under SEEN weather, call = step), with lesson attempt j started
    at stage 3 when scaffolded(j). The scaffold draws no random numbers. Returns (scaffolded attempts, first rights)."""
    f = brain.step
    j, n_sc, firsts = 0, 0, []

    def make():
        nonlocal n_sc
        c = E49.WeatherChamber(E49.SEEN[rng.integers(4)])
        if j < attempts and scaffolded(j, share):
            c.w = c.s = 1
            n_sc += 1
        if j < attempts:
            firsts.append(int(c.right()))
        return c

    c, g = make(), 0
    a = int(np.asarray(f(c.x())).reshape(-1)[0])
    for _ in range(attempts):
        while True:
            guided = (g % (E49.GUIDED + E49.AUTONOMOUS)) < E49.GUIDED
            ok, r = c.execute(a)
            t = label(c, a) if (label is not None and guided and not ok and not c.done) else None
            g += 1
            if c.done:
                j += 1
                c = make()
                a = int(np.asarray(f(c.x(), reward=np.array([r]), done=np.array([True]))).reshape(-1)[0])
                break
            kw = dict(reward=np.array([r]), done=np.array([False]))
            if t is not None:
                kw["teacher"] = np.array([t])
            a = int(np.asarray(f(c.x(), **kw)).reshape(-1)[0])
    brain.reset()
    return n_sc, firsts


def twin(seed, kind, lab_seed, share):
    """E62.twin with the lesson through live_scaffold; the 20 attempts alone are E62's own, never scaffolded."""
    rng = np.random.default_rng(seed)
    s = E62.compose(seed)
    stream = []
    lab = E62.logged(E62.labeller(kind, np.random.default_rng(lab_seed)), stream) if kind else None
    n_sc, firsts = live_scaffold(s, LESSON, rng, lab, share)
    E62.live_world(s, E62.VEST, rng)
    acts = E62.greedy_actions(s)
    hits = [a == r for a, r in zip(acts, E62.RIGHTS * len(E62.UNSEEN))]
    return dict(acc=float(np.mean(hits)), actions=acts, labels=stream, n_labels=len(stream), scaffolded=n_sc, firsts=firsts)


def arms_for(seed, share):
    arms = {"null": twin(seed, "random", seed + 2, share), "untaught": twin(seed, None, None, share)}
    for kind in H.F.TEACHERS:
        arms[kind] = twin(seed, kind, seed + 1, share)
    return arms


def run(job):
    inst, k, cond, share = job
    import cadence as cd
    G.set_budget(BUDGET)
    E62.compose = H.compose_for(inst)
    t0 = time.time()
    seed = SEED_BASE + k
    arms = arms_for(seed, share if cond == "on" else 0.0)
    for a in arms.values():
        a["late_labels"] = G.late_labels(a)
        a["early_labels"] = a["n_labels"] - a["late_labels"]
        for key in ("actions", "labels", "firsts"):
            a.pop(key, None)
    out = dict(instrument=inst, cond=cond, share=share if cond == "on" else 0.0, student=k, seed=seed, arms=arms,
               secs=round(time.time() - t0, 1), cadence=cd.__version__)
    print(f"  {inst:2s} {cond:3s} st{k:3d} ({out['secs']}s)", flush=True)   # no accuracies printed while running
    return out


# ============ analysis ============

def arrays(rows):
    by = {(r["instrument"], r["cond"], r["student"]): r for r in rows}
    S = sorted({r["student"] for r in rows if all((i, c, r["student"]) in by for i in INSTRUMENTS for c in CONDITIONS)})
    acc = lambda i, c, a: np.array([by[(i, c, k)]["arms"][a]["acc"] for k in S])
    W = {}
    for i in INSTRUMENTS:
        for c in CONDITIONS:
            null = acc(i, c, "null")
            W[(i, c)] = dict(E=acc(i, c, "know-early-2") - null, L=acc(i, c, "know-late-2") - null,
                             K=acc(i, c, "know-4") - null, D=acc(i, c, "know-early-2") - acc(i, c, "know-late-2"),
                             U=acc(i, c, "untaught"))
    return S, W, by


def analyse(rows):
    S, W, by = arrays(rows)
    n = len(S)
    idx = np.random.default_rng(BOOT_SEED).integers(0, n, size=(BOOT, n))
    R = {key: float(w["L"].mean() / w["E"].mean()) for key, w in W.items()}
    Rb = {key: w["L"][idx].mean(axis=1) / w["E"][idx].mean(axis=1) for key, w in W.items()}
    phi = (R[("A", "on")] - R[("A", "off")]) / (R[("D1", "off")] - R[("A", "off")])
    phib = (Rb[("A", "on")] - Rb[("A", "off")]) / (Rb[("D1", "off")] - Rb[("A", "off")])
    ci = lambda x: [float(v) for v in np.percentile(x, [2.5, 97.5])]
    sem = lambda x: float(np.std(x, ddof=1) / np.sqrt(len(x)))
    rise = Rb[("A", "on")] - Rb[("A", "off")]
    d1 = Rb[("D1", "on")] - Rb[("D1", "off")]
    o = dict(n=n, phi_A=dict(value=float(phi), ci95=ci(phib), robust_se=float((np.percentile(phib, 84) - np.percentile(phib, 16)) / 2)),
             A_rise=dict(value=R[("A", "on")] - R[("A", "off")], ci95=ci(rise)),
             D1_change=dict(value=R[("D1", "on")] - R[("D1", "off")], ci95=ci(d1)), cells={})
    for (i, c), w in W.items():
        lab = lambda a, key: float(np.mean([by[(i, c, k)]["arms"][a][key] for k in S]))
        o["cells"][f"{i}|{c}"] = dict(
            R=R[(i, c)], R_ci95=ci(Rb[(i, c)]), early_worth=(float(w["E"].mean()), sem(w["E"])),
            late_worth=(float(w["L"].mean()), sem(w["L"])), know4_worth=(float(w["K"].mean()), sem(w["K"])),
            s=float(w["D"].mean() / w["K"].mean()), untaught=float(w["U"].mean()),
            late_labels={a: lab(a, "late_labels") for a in ("know-early-2", "know-late-2", "know-4")},
            early_labels={a: lab(a, "early_labels") for a in ("know-early-2", "know-late-2", "know-4")})
    lo, hi = o["phi_A"]["ci95"]
    o["verdict"] = "MOSTLY EXPOSURE" if lo > HALF else ("NOT MOSTLY EXPOSURE" if hi < HALF else "INCONCLUSIVE")
    o["some_exposure"] = bool(o["A_rise"]["ci95"][0] > 0 or o["A_rise"]["ci95"][1] < 0)
    return o


def report(o):
    for key, v in o["cells"].items():
        print(f"  [{key}] R late/early {v['R']:+.3f} (95% {v['R_ci95'][0]:+.3f}..{v['R_ci95'][1]:+.3f}) | early worth "
              f"{v['early_worth'][0]:+.3f} ({v['early_worth'][1]:.3f}) | late worth {v['late_worth'][0]:+.3f} ({v['late_worth'][1]:.3f}) | "
              f"know-4 {v['know4_worth'][0]:+.3f} | s {v['s']:+.3f} | untaught {v['untaught']:.3f} | late labels {v['late_labels']} | "
              f"early labels {v['early_labels']}")
    p, a, d = o["phi_A"], o["A_rise"], o["D1_change"]
    print(f"  phi_A {p['value']:+.3f} (95% {p['ci95'][0]:+.3f}..{p['ci95'][1]:+.3f}, robust SE {p['robust_se']:.3f})")
    print(f"  A rise {a['value']:+.3f} (95% {a['ci95'][0]:+.3f}..{a['ci95'][1]:+.3f}); D1 change {d['value']:+.3f} "
          f"(95% {d['ci95'][0]:+.3f}..{d['ci95'][1]:+.3f})")
    print(f"  VERDICT: {o['verdict']} (some exposure: {o['some_exposure']})")


# ============ check ============

def check():
    """(a) identity of the off condition with E62.twin and with EXP-62h's stored student 0; (b) the scaffold's shape."""
    import cadence as cd
    G.set_budget(BUDGET)
    out = dict(cadence=cd.__version__, identity={}, stored_62h={}, scaffold={})
    stored = {}
    path = os.path.join(HERE, "EXP-62h-full.jsonl")
    for line in open(path):
        r = json.loads(line)
        if r["student"] == 0:
            stored[r["instrument"]] = r
    for inst in INSTRUMENTS:
        E62.compose = H.compose_for(inst)
        seed = SEED_BASE + 999                         # a seed outside every run range of this script's students
        mine = twin(seed, "know-late-2", seed + 1, 0.0)
        ref = E62.twin(seed, LESSON, "know-late-2", seed + 1)
        same = mine["acc"] == ref["acc"] and mine["labels"] == ref["labels"] and mine["actions"] == ref["actions"]
        out["identity"][inst] = same
        s0 = stored[inst]
        rep = {a: twin(s0["seed"], k, l, 0.0)["acc"] for a, k, l in (
            ("null", "random", s0["seed"] + 2), ("untaught", None, None), ("know-early-2", "know-early-2", s0["seed"] + 1),
            ("know-late-2", "know-late-2", s0["seed"] + 1), ("know-4", "know-4", s0["seed"] + 1))}
        out["stored_62h"][inst] = all(rep[a] == s0["arms"][a]["acc"] for a in rep)
        on = twin(seed, "know-late-2", seed + 1, SHARE)            # shape only; its accuracy is not printed or stored
        out["scaffold"][inst] = dict(scaffolded=on["scaffolded"], fire_first=sum(1 for x in on["firsts"] if x == E49.E48.E45.FIRE),
                                     lesson_attempts=len(on["firsts"]), off_scaffolded=mine["scaffolded"])
    ok_id = all(out["identity"].values())
    ok_sc = all(v["scaffolded"] == int(LESSON * SHARE) and v["fire_first"] == v["scaffolded"] and v["off_scaffolded"] == 0
                and v["lesson_attempts"] == LESSON for v in out["scaffold"].values())
    out["pass"] = bool(ok_id and ok_sc)
    print(json.dumps(out, indent=1))
    print("CHECK", "PASS" if out["pass"] else "FAIL", "| stored EXP-62h reproduced:", all(out["stored_62h"].values()))
    return out


def main():
    t0 = time.time()
    if TAG == "check":
        o = check()
        json.dump(o, open(os.path.join(HERE, "EXP-62i-check.json"), "w"))
        return
    share = SHARE
    if TAG == "pilot":
        N = PILOT_N
    else:
        pj = os.path.join(HERE, "EXP-62i-pilot.json")
        if not os.path.exists(pj):
            raise SystemExit("run the pilot first: the full run reads N from EXP-62i-pilot.json")
        P = json.load(open(pj))
        if P["N"] is None:
            raise SystemExit(f"the pilot stopped the full run: {P['stop']}")
        N, share = int(P["N"]), float(P["share"])
    ckpt = os.path.join(HERE, f"EXP-62i-{TAG}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    rows = [r for r in rows if r["cond"] == "off" or r["share"] == share]
    done = {(r["instrument"], r["cond"], r["student"]) for r in rows}
    jobs = [(i, k, c, share) for k in range(N) for i in INSTRUMENTS for c in CONDITIONS if (i, c, k) not in done]
    print(f"EXP-62i [{TAG}]: N {N}, share {share}, budget {BUDGET}, lesson {LESSON}; {len(jobs)} jobs to go ({len(done)} done); "
          f"seeds {SEED_BASE}+", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as fh:
                    fh.write(json.dumps(r) + "\n")
    rows = [r for r in rows if r["student"] < N]
    print(f"\nEXP-62i [{TAG}] summary ({time.time() - t0:.0f}s)")
    o = analyse(rows)
    if TAG == "pilot":                                  # validity, exposure check and N only; the pilot's phi is not reported
        cells = o["cells"]
        ceil = [k for k, v in cells.items() if v["untaught"] >= 0.90]
        blind = [k for k, v in cells.items() if v["know4_worth"][0] < 0.10 or v["know4_worth"][0] < 2 * v["know4_worth"][1]]
        a_on = cells["A|on"]["late_labels"]["know-late-2"]
        d1_off = cells["D1|off"]["late_labels"]["know-late-2"]
        exposure_ok = a_on >= d1_off
        se = o["phi_A"]["robust_se"]
        n = int(math.ceil(PILOT_N * (se / SE_TARGET) ** 2 / 24) * 24)
        stop = (f"ceiling {ceil} " if ceil else "") + (f"blind {blind} " if blind else "")
        if not exposure_ok:
            stop += f"exposure: A on {a_on:.1f} late labels < D1 off {d1_off:.1f}" + (
                " -> rerun the pilot with SHARE=0.75" if share == 0.5 else " -> stop")
        N_full = None if stop else int(min(max(n, N_MIN), N_MAX))
        for k, v in cells.items():
            print(f"  [{k}] untaught {v['untaught']:.3f} | know-4 worth {v['know4_worth'][0]:+.3f} ({v['know4_worth'][1]:.3f}) | "
                  f"late labels (know-late-2) {v['late_labels']['know-late-2']:.1f}")
        print(f"  exposure check: A on {a_on:.1f} vs D1 off {d1_off:.1f} -> {'ok' if exposure_ok else 'FAIL'}")
        print(f"  pilot rule: phi robust SE {se:.3f} -> N {n} -> {N_full if N_full else 'STOP: ' + stop}")
        json.dump(dict(N=N_full, share=share, se=se, raw_n=n, stop=stop or None, exposure=dict(A_on=a_on, D1_off=d1_off),
                       validity={k: dict(untaught=v["untaught"], know4=v["know4_worth"]) for k, v in cells.items()}),
                  open(os.path.join(HERE, "EXP-62i-pilot.json"), "w"))
        return
    report(o)
    json.dump(o, open(os.path.join(HERE, "EXP-62i-full.json"), "w"))


if __name__ == "__main__":
    main()
