"""
CAL-1: calibration-graded v(S) in the teacher market. Harness (the analysis is CAL-1_analysis.py, on the saved rows).
PRE-REGISTRATION: experiments/CAL-1.md (committed b70748c on 2026-11-13, Will's go, before any CAL-1 data).

Student side = EXP-77b's instrument through EXP-62's code, unchanged: compose (delayed-credit brain, scales trace 12.0,
founder lateral), live_world (weather chamber, corrective schedule), lesson 80, 20 attempts alone through `step`, greedy
per-state accuracy over 16 unseen states. The zero arms (null, untaught, random) call EXP-62's `twin`, hence its audited
`labeller`. New: teachers with a fixed identity (drawn once from their own seed), a 192-label probe before any teaching,
and jobs that are single twins (block, student, arm), run through EXP-73's pool-and-checkpoint loop.

    MODE=v1 python -u CAL-1_calibration_vs.py                 # V1 inspect check (the audit itself: EXP-77b_construction_audit.py)
    MODE=gate WORKERS=4 python -u CAL-1_calibration_vs.py     # V2 identity gate: EXP-77b student 0 on this version
    TAG=pilot WORKERS=4 python -u CAL-1_calibration_vs.py     # pilot: 1 group of 24 x 4 students, pilot rule for m
    TAG=full M=<6|8> WORKERS=4 python -u CAL-1_calibration_vs.py
"""
import importlib.util, inspect, json, os, time
from multiprocessing import get_context

import numpy as np

if os.environ.get("LATERAL"):
    raise SystemExit("CAL-1 reads the founder lateral: unset LATERAL")

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("e62", os.path.join(HERE, "EXP-62_content_market_committed_null.py"))
E62 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E62)
RIGHTS = E62.RIGHTS                                     # [0, 1, 2, 3]: the right action at stage i is i; WAIT = 4

MODE = os.environ.get("MODE", "run")
TAG = os.environ.get("TAG", "full")
M = int(os.environ.get("M", 6))
WORKERS = min(4, int(os.environ.get("WORKERS", 4)))     # hard cap: 4 worker processes
LESSON = 80
KNOW = ["know-1", "know-2", "know-3", "know-4"]
TRAINED_FAKES = ["random", "wrong-chain", "echo", "anti-echo"]
FAKES = TRAINED_FAKES + ["wrong-map"]
ZERO = ["null", "untaught", "random"]
GROUP_TRAIN = ["graded"] * 12 + KNOW + [k for k in TRAINED_FAKES for _ in range(2)]
GROUP_HELD = ["graded"] * 10 + KNOW + [k for k in FAKES for _ in range(2)]
assert len(GROUP_TRAIN) == 24 and len(GROUP_HELD) == 24


# ============ Teachers (the draft's sketch, verbatim in substance) ============

def make_teacher(kind, ident_seed):            # identity drawn once; kept on every student and on the probe
    r = np.random.default_rng(ident_seed)
    p = m = None                                # p and m are indexed by the right action, which is the stage
    if kind.startswith("know-"):
        known = set(r.choice(4, size=int(kind[5:]), replace=False).tolist())
        p = [float(i in known) for i in range(4)]
    elif kind == "graded":
        p = r.uniform(0.0, 1.0, 4).tolist()
    elif kind == "wrong-map":
        m = [int(r.choice([x for x in range(5) if x != i])) for i in range(4)]

    def labeller(noise):                        # noise = default_rng(lesson or probe seed)
        if p is not None:
            return lambda c, a: c.right() if noise.random() < p[c.right()] else int(noise.integers(5))
        if m is not None:
            return lambda c, a: m[c.right()]
        return E62.labeller(kind, noise)        # random, wrong-chain, echo, anti-echo: the existing code
    labeller.identity = dict(kind=kind, ident_seed=int(ident_seed), p=p, map=m)
    return labeller


class Stub:                                     # a probe context; the labeller reads only right() and the action
    def __init__(self, i):
        self.i = i

    def right(self):
        return RIGHTS[self.i]


def probe(lab, R=12):
    return [(i, a, int(lab(Stub(i), a))) for i in range(4) for a in range(5) if a != RIGHTS[i] for _ in range(R)]


def features(pr):                               # 21 numbers; none reads RIGHTS
    f, same = np.zeros((4, 5)), 0
    for i, a, t in pr:
        f[i, t] += 1
        same += t == a
    return np.r_[(f / f.sum(1, keepdims=True)).ravel(), same / len(pr)]


# ============ Pools and seeds (all fixed by the pre-registration) ============

def teachers(block):
    """block: train | held | pilot | probe-only. Returns dicts with t (index in block), id (global), group, kind, seeds."""
    if block == "train":
        return [dict(block=block, t=t, id=t, group=t // 24, kind=GROUP_TRAIN[t % 24], ident_seed=11_000_000 + t,
                     probe_seed=30_000_000 + t) for t in range(192)]
    if block == "held":
        return [dict(block=block, t=t, id=200 + t, group=t // 24, kind=GROUP_HELD[t % 24], ident_seed=11_100_000 + t,
                     probe_seed=30_000_000 + 200 + t) for t in range(192)]
    if block == "pilot":
        return [dict(block=block, t=t, id=500 + t, group=0, kind=GROUP_HELD[t], ident_seed=11_900_000 + t,
                     probe_seed=30_000_000 + 500 + t) for t in range(24)]
    if block == "probe-only":                   # 16 know-4 (probe-gamer) + 64 wrong-chain clones (coordinated S2)
        return [dict(block=block, t=t, id=None, group=None, kind="know-4" if t < 16 else "wrong-chain",
                     ident_seed=11_200_000 + t, probe_seed=30_000_700 + t) for t in range(80)]
    raise ValueError(block)


def students(sblock, m=M):
    """sblock: train | held | audition | pilot. j = the student's index in its block (lesson noise), audition j = 900 + g."""
    if sblock == "train":
        return [dict(sblock=sblock, s=s, j=s, group=s // 3, seed=10_100_000 + 10 * s, tblock="train") for s in range(24)]
    if sblock == "held":
        return [dict(sblock=sblock, s=s, j=s, group=s // m, seed=10_200_000 + 10 * s, tblock="held") for s in range(8 * m)]
    if sblock == "audition":
        return [dict(sblock=sblock, s=g, j=900 + g, group=g, seed=10_300_000 + 10 * g, tblock="held") for g in range(8)]
    if sblock == "pilot":
        return [dict(sblock=sblock, s=s, j=s, group=0, seed=10_900_000 + 10 * s, tblock="pilot") for s in range(4)]
    raise ValueError(sblock)


def probe_of(T):
    lab = make_teacher(T["kind"], T["ident_seed"])
    return probe(lab(np.random.default_rng(T["probe_seed"]))), lab.identity


# ============ Twins ============

def zero_twin(seed, arm):
    """The zero arms through EXP-62's own twin(), so through the labeller EXP-77b's audit admits."""
    if arm == "null":
        return E62.twin(seed, LESSON, "random", seed + 2)
    if arm == "untaught":
        return E62.twin(seed, LESSON, None, None)
    if arm == "random":
        return E62.twin(seed, LESSON, "random", seed + 1)
    raise ValueError(arm)


def teacher_twin(seed, lab):
    """EXP-62's twin() line for line, with the teacher's labeller supplied instead of built from a kind."""
    rng = np.random.default_rng(seed)                      # same world draws for every arm of this student
    s = E62.compose(seed)
    stream = []
    lab = E62.logged(lab, stream) if lab else None
    E62.live_world(s, LESSON, rng, label=lab)
    E62.live_world(s, E62.VEST, rng)                       # alone through `step`, no labels (EXP-58)
    acts = E62.greedy_actions(s)
    hits = [a == r for a, r in zip(acts, RIGHTS * len(E62.UNSEEN))]
    return dict(acc=float(np.mean(hits)), actions=acts, labels=stream,
                label_right=float(np.mean([t == r for r, _, t in stream])) if stream else None, n_labels=len(stream))


def run_job(job):
    t0 = time.time()
    S, arm = job["student"], job["arm"]
    if arm in ZERO:
        out = zero_twin(S["seed"], arm)
        row = dict(sblock=S["sblock"], s=S["s"], group=S["group"], seed=S["seed"], arm=arm, **out)
    else:
        T = job["teacher"]
        lab_seed = 20_000_000 + 1000 * T["id"] + S["j"]
        lab = make_teacher(T["kind"], T["ident_seed"])
        out = teacher_twin(S["seed"], lab(np.random.default_rng(lab_seed)))
        pr, ident = probe_of(T)
        row = dict(sblock=S["sblock"], s=S["s"], group=S["group"], seed=S["seed"], arm="teacher", t=T["t"], id=T["id"],
                   tblock=T["block"], kind=T["kind"], identity=ident, lab_seed=lab_seed, probe_seed=T["probe_seed"],
                   probe=pr, **out)
    row["secs"] = round(time.time() - t0, 1)
    return row


def jobs_for(sblocks, m=M):
    pool = {b: teachers(b) for b in ("train", "held", "pilot")}
    out = []
    for sb in sblocks:
        for S in students(sb, m):
            for arm in ZERO:
                out.append(dict(student=S, arm=arm))
            for T in pool[S["tblock"]]:
                if T["group"] == S["group"]:
                    out.append(dict(student=S, arm=T["t"], teacher=T))
    return out


def key(r):
    return (r["sblock"], r["s"], r["arm"] if r["arm"] != "teacher" else r["t"])


def run_pool(jobs, ckpt):
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {key(r) for r in rows}
    todo = [j for j in jobs if (j["student"]["sblock"], j["student"]["s"], j["arm"]) not in done]
    import cadence
    print(f"CAL-1 [{TAG}]: cadence {getattr(cadence, '__version__', '?')} at {os.path.dirname(cadence.__file__)}; "
          f"{len(todo)} twins to go ({len(done)} done); {WORKERS} workers", flush=True)
    t0, n = time.time(), 0
    if todo:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(todo)))) as pool:
            for r in pool.imap_unordered(run_job, todo):
                rows.append(r)
                n += 1
                with open(ckpt, "a") as fh:
                    fh.write(json.dumps(r) + "\n")
                if n % 27 == 0 or n == len(todo):
                    print(f"  {n}/{len(todo)} twins, {time.time() - t0:.0f}s", flush=True)
    return rows


# ============ Probe signals (used by the pilot print and by the analysis) ============

def s1(pr):
    """Consistency: mean over the 16 contexts of the share of its labels equal to the context's most frequent label."""
    ctx = {}
    for i, a, t in pr:
        ctx.setdefault((i, a), []).append(t)
    return float(np.mean([np.bincount(v, minlength=5).max() / len(v) for v in ctx.values()]))


def ctx_counts(pr):
    c = np.zeros((4, 5, 5))                     # stage, executed action, label
    for i, a, t in pr:
        c[i, a, t] += 1
    return c


def s2_all(probes, extra=()):
    """Peer agreement: per context, the plurality label over all OTHER teachers in the block (plus `extra` reference
    probes); ties to the lowest action index; score = the teacher's share of labels equal to it, averaged over contexts."""
    C = [ctx_counts(p) for p in probes]
    tot = sum(C) + sum((ctx_counts(p) for p in extra), np.zeros((4, 5, 5)))
    out = []
    for c in C:
        other = tot - c
        shares = []
        for i in range(4):
            for a in range(5):
                if a == RIGHTS[i]:
                    continue
                plur = int(np.argmax(other[i, a]))          # argmax returns the lowest index on ties
                shares.append(c[i, a, plur] / c[i, a].sum())
        out.append(float(np.mean(shares)))
    return out


def k_key(pr):
    """Answer key K (a reference that reads the RIGHTS map): share of probe labels naming the right action."""
    return float(np.mean([t == RIGHTS[i] for i, a, t in pr]))


# ============ V1 and V2 ============

def v1():
    src = inspect.getsource(zero_twin)
    ok = ("E62.twin(" in src and "labeller(kind, np.random.default_rng(lab_seed))" in inspect.getsource(E62.twin)
          and E62.twin.__globals__["labeller"] is E62.labeller)
    print(f"V1 inspect: CAL-1's zero arms call EXP-62's twin, whose labeller is the audited EXP-62 entry point: "
          f"{'PASS' if ok else 'FAIL'}")
    return ok


def gate_job(spec):
    arm, path = spec
    seed = 9_000_000
    if path == "zero":
        return arm, path, zero_twin(seed, arm)
    lab = make_teacher(arm, 11_200_000)          # know-4: the identity cannot matter (all four stages known)
    return arm, path, teacher_twin(seed, lab(np.random.default_rng(seed + 1)))


def gate():
    import cadence
    t0 = time.time()
    ref = next(r for r in (json.loads(l) for l in open(os.path.join(HERE, "EXP-77b-full.jsonl")))
               if r["student"] == 0 and r["lesson"] == LESSON)
    assert ref["seed"] == 9_000_000, ref["seed"]
    specs = [("null", "zero"), ("untaught", "zero"), ("random", "zero"), ("random", "teacher"), ("know-4", "teacher"),
             ("wrong-chain", "teacher"), ("echo", "teacher"), ("anti-echo", "teacher")]
    with get_context("spawn").Pool(WORKERS) as pool:
        res = pool.map(gate_job, specs)
    same = {}
    for arm, path, new in res:
        same[f"{arm} ({path} path)"] = (new["actions"] == ref["arms"][arm]["actions"]
                                        and new["labels"] == ref["arms"][arm]["labels"])
        print(f"  {arm:12s} {path:8s} acc {new['acc']:.3f} (EXP-77b {ref['arms'][arm]['acc']:.3f}) labels {new['n_labels']:3d}"
              f"  {'same' if same[f'{arm} ({path} path)'] else 'DIFFERENT'}", flush=True)
    ok = all(same.values())
    print(f"V2 identity gate on cadence {cadence.__version__}: seed 9000000 vs EXP-77b student 0 ({time.time() - t0:.0f}s): "
          + ("IDENTICAL" if ok else f"DIFFERS {same}"), flush=True)
    return ok


# ============ Pilot ============

def pilot_report(rows):
    T = teachers("pilot")
    S = students("pilot")
    acc = {key(r): r["acc"] for r in rows}
    Z = np.array([np.mean([acc[("pilot", st["s"], z)] for z in ZERO]) for st in S])
    W = np.array([[acc[("pilot", st["s"], t["t"])] - Z[k] for k, st in enumerate(S)] for t in T])   # 24 x 4
    probes = [probe_of(t) for t in T]
    S1 = [s1(p) for p, _ in probes]
    S2 = s2_all([p for p, _ in probes])
    K = [k_key(p) for p, _ in probes]
    print("\nCAL-1 pilot chain print (RUN GATE line 5): class, identity, probe S1 / S2 (pilot pool) / K, W per student, mean")
    for k, t in enumerate(T):
        ident = probes[k][1]
        idtxt = (f"p={[round(x, 2) for x in ident['p']]}" if ident["p"] is not None else
                 f"map={ident['map']}" if ident["map"] is not None else "")
        print(f"  {t['kind']:11s} {idtxt:28s} S1 {S1[k]:.3f} S2 {S2[k]:.3f} K {K[k]:.3f} | W "
              + " ".join(f"{w:+.3f}" for w in W[k]) + f" | mean {W[k].mean():+.3f}")
    n = W.shape[1]
    ms_b = n * np.var(W.mean(1), ddof=1)
    v_w = float(np.mean(np.var(W, axis=1, ddof=1)))
    v_b = max(0.0, (ms_b - v_w) / n)
    rel = lambda m: v_b / (v_b + v_w / m) if (v_b + v_w / m) > 0 else 0.0
    know4 = float(W[[k for k, t in enumerate(T) if t["kind"] == "know-4"][0]].mean())
    sd_means = float(np.std(W.mean(1), ddof=1))
    print(f"\n  one-way split over 24 teachers x {n} students: between-teacher variance v_b {v_b:.5f}, "
          f"within-teacher (student) variance v_w {v_w:.5f}")
    print(f"  projected reliability at m = 6: {rel(6):.3f}; at m = 8: {rel(8):.3f}")
    stops = dict(P1_know4_below_10=bool(know4 < 0.10), P2_sd_of_means_below_05=bool(sd_means < 0.05),
                 P3_rel_at_8_below_7=bool(rel(8) < 0.7))
    m = 6 if rel(6) >= 0.7 else 8
    print(f"  know-4 W {know4:+.3f}; SD of the 24 teachers' mean W {sd_means:.3f}; stops {stops}")
    verdict = "PILOT STOP" if any(stops.values()) else f"GO with m = {m}"
    print(f"  pilot rule -> {verdict}", flush=True)
    json.dump(dict(W=W.tolist(), Z=Z.tolist(), S1=S1, S2=S2, K=K, kinds=[t["kind"] for t in T],
                   identities=[p[1] for p in probes], v_b=v_b, v_w=v_w, rel6=rel(6), rel8=rel(8), know4=know4,
                   sd_means=sd_means, stops=stops, m=m, verdict=verdict),
              open(os.path.join(HERE, "CAL-1-pilot.json"), "w"))


# ============ Main ============

def save_probes(blocks, path):
    out = []
    for b in blocks:
        for T in teachers(b):
            pr, ident = probe_of(T)
            out.append(dict(T, identity=ident, probe=pr))
    json.dump(out, open(path, "w"))
    print(f"  probes for {len(out)} instances written before any teaching: {os.path.basename(path)}", flush=True)


def main():
    t0 = time.time()
    if TAG == "pilot":
        save_probes(["pilot"], os.path.join(HERE, "CAL-1-pilot-probes.json"))
        rows = run_pool(jobs_for(["pilot"]), os.path.join(HERE, "CAL-1-pilot.jsonl"))
        pilot_report(rows)
    elif TAG == "full":
        assert M in (6, 8), M
        save_probes(["train", "held", "probe-only"], os.path.join(HERE, "CAL-1-full-probes.json"))
        rows = run_pool(jobs_for(["train", "held", "audition"]), os.path.join(HERE, "CAL-1-full.jsonl"))
        print(f"CAL-1 [full] m = {M}: {len(rows)} twins on disk", flush=True)
    else:
        raise SystemExit(f"unknown TAG {TAG}")
    print(f"CAL-1 [{TAG}] done in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    if MODE == "v1":
        raise SystemExit(0 if v1() else 1)
    if MODE == "gate":
        raise SystemExit(0 if gate() else 1)
    main()
