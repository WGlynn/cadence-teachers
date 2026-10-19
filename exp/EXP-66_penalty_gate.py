"""
EXP-66: a per-miss penalty through the reward channel, with and without the gate keyed on it (upstream #202, Bernhard's
2026-10-18 ask: "compare that reward change with and without the gate").
  ctx5   no penalty, no gate (the founder key)
  out5t  no penalty, EXP-63's oracle gate during training only (the ceiling, as in EXP-65)
  pen    a non-terminal miss pays -PEN instead of 0, no gate
  peng   the same penalty, gate keyed on the reward step() receives: hold the last decision when reward < 0 (non-boundary)
Every arm reads with the plain context. Fresh seeds 66_000+, Cadence 0.84.3. PEN is fixed by the pilot (smallest grid value
the learner's own forecast error can see, stage-1 AUC >= .75) and read from EXP-66-pilot.json by the full run.
PREDICTION: experiments/EXP-66.md (written before any run).

    MODE=check WORKERS=4 python -u EXP-66_penalty_gate.py
    PHASE=pilot WORKERS=4 python -u EXP-66_penalty_gate.py
    PHASE=full WORKERS=4 python -u EXP-66_penalty_gate.py
"""
import importlib.util, json, os, tempfile, time
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("e65", os.path.join(HERE, "EXP-65_inbrain_gate.py"))
E65 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E65)          # patches E56.Chamber.execute (stage + LAST_OK), defines the logged traces
E63, E56, np = E65.E63, E65.E56, E65.np

MODE = os.environ.get("MODE", "run")
PHASE = os.environ.get("PHASE", "full")
WORKERS = int(os.environ.get("WORKERS", 4))
SIGNALS = ("natural", "corrective")
ARMS = ("ctx5", "out5t", "pen", "peng")
GRID = (0.02, 0.05, 0.10)
AUC_BAR = 0.75

# ============ The penalty: a non-terminal miss pays -PEN instead of 0 (terminal +2 / -1 unchanged) ============
PEN_NOW = [0.0]
_prev_execute = E56.Chamber.execute


def _penalised_execute(self, a):
    ok, r = _prev_execute(self, a)
    if PEN_NOW[0] and not ok and not self.done:
        r = -PEN_NOW[0]
    return ok, r


E56.Chamber.execute = _penalised_execute
ObsTrace = E63.ObsTrace


class RewardGate(ObsTrace, E65.Logged):
    """Hold the last decision out of the temporal context when the reward delivered with this call is below 0.
    Reads only the reward argument step() receives; never acts on a boundary (the library clears the context at done)."""

    def __init__(self, brain, hold):
        ObsTrace.__init__(self, brain, hold)
        self._install(brain)
        self.held = []

    def call(self, fn, x, boundary=False, **kw):
        b = self.b
        self._boundary = boundary
        r = kw.get("reward")
        if self.hold and not boundary and self.prev is not None and r is not None and float(np.asarray(r).reshape(-1)[0]) < 0:
            b._context = None if self.pre is None else self.pre.copy()
            self.held.append((E65.LAST_STAGE[0], bool(E63.LAST_OK[0])))
        if boundary:
            pre = None if b._context is None else np.zeros_like(b._context)
        else:
            pre = None if b._context is None else b._context.copy()
        out = fn(x, **kw)
        self.prev, self.pre = x.copy(), pre
        return int(np.asarray(out).reshape(-1)[0])


TRAIN = dict(ctx5=(E65.LoggedObs, False), out5t=(E65.LoggedOutcome, True), pen=(E65.LoggedObs, False),
             peng=(RewardGate, True))


def life(chain, arm, signal, episodes, seed, pen):
    E56.Chamber.x = E63.CHAINS[chain]
    E56.EPISODES = episodes
    PEN_NOW[0] = pen if arm in ("pen", "peng") else 0.0
    cls, hold = TRAIN[arm]
    b = E56.compose("ctx5", seed)                  # memory_context .5 in every arm
    tr = cls(b, hold)
    stats = E56.train(b, tr, signal)
    diag = E65.diagnose(tr, chain)
    PEN_NOW[0] = 0.0
    E56.Trace = ObsTrace                           # every arm reads plain; E56.read builds its trace from this name
    with tempfile.TemporaryDirectory() as d:
        rd = E56.read(b.save(os.path.join(d, "b.npz")), False)
    return stats, rd, diag


def run(job):
    phase, chain, arm, signal, episodes, i, base, pen = job
    import cadence as cd
    t0 = time.time()
    stats, rd, diag = life(chain, arm, signal, episodes, base + i, pen)
    row = dict(phase=phase, chain=chain, arm=arm, signal=signal, episodes=episodes, seed=i, seed_base=base,
               pen=(pen if arm in ("pen", "peng") else 0.0), **stats, **rd, diag=diag, secs=round(time.time() - t0, 1),
               cadence=cd.__version__)
    ft = " ".join("  - " if v is None else f"{v:.2f}" for v in rd["first_try"])
    h = diag.get("held", {})
    a1 = diag.get("auc_s1")
    print(f"  {chain:9s} {arm:5s} p{row['pen']:.2f} {signal:10s} s{i:2d}: exact {int(rd['greedy_exact'])} sampled "
          f"{rd['sampled']:.2f} first-try {ft} | held {h.get('on_miss', '-')}/{h.get('misses', '-')} misses, "
          f"{h.get('on_ok', '-')} ok | auc s1 {'-' if a1 is None else f'{a1:.2f}'} ({row['secs']}s)", flush=True)
    return row


# ============ Check ============
READ_FIELDS = E63.READ_FIELDS


def _check_job(job):
    tag, chain, arm, signal, seed, pen = job
    if tag == "e63":
        PEN_NOW[0] = 0.0
        stats, rd = E63.life(chain, arm, signal, 120, seed)
        return job, {**stats, **rd}
    stats, rd, diag = life(chain, arm, signal, 120, seed, pen)
    return job, {**stats, **rd, "diag": diag}


def check():
    import cadence as cd
    print(f"EXP-66 check: cadence {cd.__version__} from {os.path.dirname(cd.__file__)}", flush=True)
    S = 66_990
    jobs = [("e63", "invisible", "ctx5", "natural", S, 0.0), ("ours", "invisible", "ctx5", "natural", S, 0.0),
            ("e63", "invisible", "out5", "corrective", S, 0.0), ("ours", "invisible", "out5t", "corrective", S, 0.0),
            ("ours", "invisible", "pen", "natural", S, 0.0), ("ours", "invisible", "peng", "natural", S, 0.0),
            ("ours", "invisible", "peng", "corrective", S, 0.05), ("ours", "invisible", "pen", "corrective", S, 0.05)]
    with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
        got = dict(pool.map(_check_job, jobs))
    ok = True
    a, b = got[jobs[0]], got[jobs[1]]
    same = all(a[f] == b[f] for f in READ_FIELDS)
    print(f"  (a) ctx5 through this script identical to EXP-63's harness at {cd.__version__}: {same}", flush=True)
    ok &= same
    o, t = got[jobs[2]], got[jobs[3]]
    same = all(o[f] == t[f] for f in ("train_success", "teacher_labels", "decisions")) and o["greedy_exact"] == t["greedy_exact"]
    print(f"  (a) out5t trains and passes greedily exactly as EXP-63's out5: {same}", flush=True)
    ok &= same
    for j in (jobs[4], jobs[5]):
        same = all(got[j][f] == b[f] for f in READ_FIELDS)
        print(f"  (b) {j[2]} at p = 0 identical to ctx5: {same}", flush=True)
        ok &= same
    h = got[jobs[6]]["diag"]["held"]
    good = h["total"] == h["on_miss"] == h["misses"] and h["on_ok"] == 0 and h["total"] > 0
    print(f"  (c) peng at p = .05 holds exactly the non-terminal misses: {good} ({h})", flush=True)
    ok &= good
    dg = got[jobs[7]]["diag"]
    vals = [v for v in dg["dop_mean"].values() if v is not None]
    live = any(v != 0 for v in vals) and len({round(v, 6) for v in vals}) > 1
    print(f"  (d) dopamine alive in pen at p = .05: {live}; auc s1 {dg['auc_s1']}; means "
          f"{json.dumps({k: (None if v is None else round(v, 4)) for k, v in dg['dop_mean'].items()})}", flush=True)
    ok &= live
    print(f"check: {'PASS' if ok else 'FAIL'}", flush=True)


# ============ Run ============
def chosen_pen():
    f = os.path.join(HERE, "EXP-66-pilot.json")
    if not os.path.exists(f):
        raise SystemExit("run the pilot first: the full run reads the penalty from EXP-66-pilot.json")
    return float(json.load(open(f))["pen"])


def plan():
    if PHASE == "pilot":
        return [("invisible", ("pen", "peng"), 120, 6, 66_500, p) for p in GRID]
    p = chosen_pen()
    return [("invisible", ARMS, 120, 48, 66_000, p), ("hidden", ARMS, 120, 24, 66_000, p),
            ("visible", ARMS, 120, 24, 66_000, p)]


def key(r):
    return (r["chain"], r["arm"], r["signal"], r["episodes"], r["seed"], r["pen"])


def pilot_summary(rows):
    out = {}
    for p in GRID:
        a = [r["diag"]["auc_s1"] for r in rows if r["arm"] == "pen" and r["pen"] == p and r["diag"].get("auc_s1") is not None]
        out[p] = (float(np.mean(a)) if a else None, len(a))
    visible = [p for p in GRID if out[p][0] is not None and out[p][0] >= AUC_BAR]
    pen = min(visible) if visible else max(GRID)
    print("\nEXP-66 pilot: pen-arm stage-1 AUC (forecast error, miss vs the invisible WOOD), pooled over signals")
    for p in GRID:
        m, n = out[p]
        sub = [r for r in rows if r["pen"] == p]
        secs = np.mean([r["secs"] for r in sub]) if sub else float("nan")
        hl = [r["diag"]["held"] for r in sub if r["arm"] == "peng" and "held" in r["diag"]]
        held = {k: int(sum(h[k] for h in hl)) for k in ("total", "on_miss", "on_ok", "misses")} if hl else None
        clean = {a: int(sum(r["greedy_exact"] for r in sub if r["arm"] == a)) for a in ("pen", "peng")}
        print(f"  p {p:.2f}: auc s1 {'-' if m is None else f'{m:.3f}'} (n={n}) | peng held {held} | clean {clean} "
              f"| {secs:.1f}s per life")
    print(f"  rule: smallest p with auc >= {AUC_BAR} -> p = {pen}" + ("" if visible else " (none reached the bar; p = .10)"))
    json.dump(dict(pen=pen, auc={str(p): out[p] for p in GRID}, bar=AUC_BAR), open(os.path.join(HERE, "EXP-66-pilot.json"), "w"))


def summary(rows):
    by = {(r["chain"], r["arm"], r["signal"], r["seed"]): r for r in rows}
    sem = lambda x: float(np.std(x, ddof=1) / np.sqrt(len(x))) if len(x) > 1 else 0.0
    out = {}
    for chain, arms, ep, n, base, p in plan():
        for scope in list(SIGNALS) + ["pooled"]:
            sigs = SIGNALS if scope == "pooled" else (scope,)
            have = [a for a in arms if all((chain, a, s, i) in by for s in sigs for i in range(n))]
            o = dict(clean={}, first_try={}, sampled={}, pairs={}, diag={})
            for a in have:
                rs = [by[(chain, a, s, i)] for s in sigs for i in range(n)]
                o["clean"][a] = int(sum(r["greedy_exact"] for r in rs))
                o["first_try"][a] = [float(np.nanmean([np.nan if r["first_try"][k] is None else r["first_try"][k]
                                                       for r in rs])) for k in range(4)]
                o["sampled"][a] = float(np.mean([r["sampled"] for r in rs]))
                a1 = [r["diag"]["auc_s1"] for r in rs if r["diag"].get("auc_s1") is not None]
                hl = [r["diag"]["held"] for r in rs if "held" in r["diag"]]
                o["diag"][a] = dict(auc_s1=(float(np.mean(a1)), sem(a1), len(a1)) if a1 else None,
                                    held={k: int(sum(h[k] for h in hl)) for k in ("total", "on_miss", "on_ok", "on_ok_s1", "misses")}
                                    if hl else None)
            for x, y in (("out5t", "ctx5"), ("peng", "pen"), ("pen", "ctx5"), ("peng", "ctx5"), ("peng", "out5t")):
                if x not in have or y not in have:
                    continue
                pairs = [(by[(chain, x, s, i)], by[(chain, y, s, i)]) for s in sigs for i in range(n)]
                for u, v in pairs:
                    assert u["seed_base"] == v["seed_base"] == base and u["cadence"] == v["cadence"], (x, y, u["seed"])
                xb = sum(u["greedy_exact"] and not v["greedy_exact"] for u, v in pairs)
                yb = sum(v["greedy_exact"] and not u["greedy_exact"] for u, v in pairs)
                stage = []
                for k in range(4):
                    d = [u["first_try"][k] - v["first_try"][k] for u, v in pairs
                         if u["first_try"][k] is not None and v["first_try"][k] is not None]
                    stage.append((float(np.mean(d)), sem(d), len(d)) if d else (None, None, 0))
                sd = [u["sampled"] - v["sampled"] for u, v in pairs]
                o["pairs"][f"{x}-{y}"] = dict(n=len(pairs), x_only=xb, y_only=yb, p=E63.mcnemar(xb, yb), stage=stage,
                                              sampled=(float(np.mean(sd)), sem(sd)))
            out[f"{chain}-{scope}"] = o
            print(f"  [{chain} {scope}] p {p:.2f} | clean greedy " + "  ".join(f"{a} {o['clean'][a]}" for a in have)
                  + " | sampled " + "  ".join(f"{a} {o['sampled'][a]:.3f}" for a in have))
            for a in have:
                dg = o["diag"][a]
                f1 = "-" if dg["auc_s1"] is None else f"{dg['auc_s1'][0]:.3f} ({dg['auc_s1'][1]:.3f}, n={dg['auc_s1'][2]})"
                print(f"      first try by stage {a:5s}: " + " ".join(f"{v:.2f}" for v in o["first_try"][a])
                      + f" | auc s1 {f1} | held {dg['held']}")
            for name, q in o["pairs"].items():
                st = "  ".join(f"s{k + 1} {m:+.3f} ({se:.3f}, n={nn})" for k, (m, se, nn) in enumerate(q["stage"]) if m is not None)
                print(f"      {name:10s} n={q['n']:3d} clean {name.split('-')[0]}-only {q['x_only']} / "
                      f"{name.split('-')[1]}-only {q['y_only']} (p {q['p']:.4f}) | first try {st} | sampled "
                      f"{q['sampled'][0]:+.3f} ({q['sampled'][1]:.3f})")
    return out


def main():
    t0 = time.time()
    ckpt = os.path.join(HERE, f"EXP-66-{PHASE}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {key(r) for r in rows}
    jobs = [(PHASE, chain, a, s, ep, i, base, p) for chain, arms, ep, n, base, p in plan() for i in range(n)
            for s in SIGNALS for a in arms
            if (chain, a, s, ep, i, p if a in ("pen", "peng") else 0.0) not in done]
    print(f"EXP-66 {PHASE}: {len(jobs)} lives to go ({len(done)} done); plan {plan()}; workers {WORKERS}", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as fh:
                    fh.write(json.dumps(r) + "\n")
    print(f"\nEXP-66 {PHASE} done in {time.time() - t0:.0f}s", flush=True)
    if PHASE == "pilot":
        pilot_summary(rows)
        return
    s = summary(rows)
    json.dump(dict(rows=rows, summary=s, pen=chosen_pen()), open(os.path.join(HERE, "EXP-66-full.json"), "w"))


if __name__ == "__main__":
    check() if MODE == "check" else main()
