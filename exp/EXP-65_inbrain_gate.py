"""
EXP-65: key EXP-63's outcome gate on signals Cadence actually receives, not on the chamber's success flag.
  lab5   hold a decision out of the temporal context when the corrective teacher's label follows it (the `teacher=` that
         step() receives right after a guided miss). Training only: no label arrives while the brain is read.
  td5    hold a decision when the brain's own signed forecast error for it (the learner's `dopamine`, computed inside the
         next step() call) is below TD_THRESH (0, fixed before any run). The gate acts inside step(): after learn(), before
         the demonstration is recorded and before act(). Training only: act() takes no feedback while the brain is read.
  out5t  EXP-63's oracle gate during training only (reads plain): the matched ceiling for the train-only gates.
Comparators ctx5 / hold5 / out5 are EXP-63's rows on the same seeds (MODE=check proves they recompute identically).
Diagnostic in every new arm: per training decision, the oracle outcome, the stage and the brain's dopamine, giving the AUC
with which the brain's own forecast error separates misses from successes (stage 1 of the invisible chain = the miss vs the
invisible correct WOOD).
PREDICTION: experiments/EXP-65.md (written before any run).

    MODE=check WORKERS=3 python -u EXP-65_inbrain_gate.py
    PHASE=pilot WORKERS=3 python -u EXP-65_inbrain_gate.py
    PHASE=full WORKERS=3 python -u EXP-65_inbrain_gate.py
"""
import importlib.util, json, os, tempfile, time
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("e63", os.path.join(HERE, "EXP-63_outcome_gate.py"))
E63 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E63)          # patches E56.Chamber.execute (LAST_OK) and defines OutcomeTrace, as in EXP-63
E56, np = E63.E56, E63.np

MODE = os.environ.get("MODE", "run")
PHASE = os.environ.get("PHASE", "full")
WORKERS = int(os.environ.get("WORKERS", 3))
TD_THRESH = float(os.environ.get("TD_THRESH", 0.0))
SIGNALS = ("natural", "corrective")
for a in ("out5t", "lab5", "td5"):
    E56.CONTEXT[a] = 0.5
NEW = {"natural": ("out5t", "td5"), "corrective": ("out5t", "lab5", "td5")}   # lab5 under natural = ctx5 (no labels)

# ============ What the world did (oracle, for the diagnostic only) and at which stage ============
LAST_STAGE = [None]
_tracked = E56.Chamber.execute          # EXP-63's wrapper: sets E63.LAST_OK


def _staged_execute(self, a):
    LAST_STAGE[0] = self.k
    return _tracked(self, a)


E56.Chamber.execute = _staged_execute
ObsTrace, OutcomeTrace = E63.ObsTrace, E63.OutcomeTrace


class Logged:
    """Wraps the brain's learn() to read the forecast error of the decision just answered (never changes it)."""

    def _install(self, b):
        self.log, self.ctx_changed, self._boundary = [], 0, False
        orig = b.learn

        def learn(*a, **k):
            before = None if b._context is None else b._context.copy()
            rep = orig(*a, **k)
            after = b._context
            if not ((before is None and after is None) or (before is not None and after is not None
                                                           and np.array_equal(before, after))):
                self.ctx_changed += 1
            if not self._boundary:
                self.log.append((LAST_STAGE[0], bool(E63.LAST_OK[0]), float(rep.get("dopamine", np.nan))))
            self._on_learn(b, rep)
            return rep

        b.learn = learn

    def _on_learn(self, b, rep):
        pass


class LoggedObs(ObsTrace, Logged):
    def __init__(self, brain, hold):
        ObsTrace.__init__(self, brain, hold)
        self._install(brain)

    def call(self, fn, x, boundary=False, **kw):
        self._boundary = boundary
        return ObsTrace.call(self, fn, x, boundary=boundary, **kw)


class LoggedOutcome(OutcomeTrace, Logged):
    def __init__(self, brain, hold):
        OutcomeTrace.__init__(self, brain, hold)
        self._install(brain)

    def call(self, fn, x, boundary=False, **kw):
        self._boundary = boundary
        return OutcomeTrace.call(self, fn, x, boundary=boundary, **kw)


class LabelTrace(ObsTrace, Logged):
    """Hold the last decision when the teacher's label for it arrives with this call (guided misses only)."""

    def __init__(self, brain, hold):
        ObsTrace.__init__(self, brain, hold)
        self._install(brain)
        self.held = []

    def call(self, fn, x, boundary=False, **kw):
        b = self.b
        self._boundary = boundary
        if self.hold and not boundary and self.prev is not None and "teacher" in kw:
            b._context = None if self.pre is None else self.pre.copy()
            self.held.append((LAST_STAGE[0], bool(E63.LAST_OK[0])))
        if boundary:
            pre = None if b._context is None else np.zeros_like(b._context)
        else:
            pre = None if b._context is None else b._context.copy()
        out = fn(x, **kw)
        self.prev, self.pre = x.copy(), pre
        return int(np.asarray(out).reshape(-1)[0])


class TDTrace(ObsTrace, Logged):
    """Hold the last decision when the brain's own signed forecast error for it is below TD_THRESH. Decided inside step():
    learn() computes the error, the context is restored, then the demonstration (if any) and act() read it."""

    def __init__(self, brain, hold):
        ObsTrace.__init__(self, brain, hold)
        self._install(brain)
        self.held = []

    def _on_learn(self, b, rep):
        if self.hold and not self._boundary and self.prev is not None and rep.get("dopamine", 0.0) < TD_THRESH:
            b._context = None if self.pre is None else self.pre.copy()
            self.held.append((LAST_STAGE[0], bool(E63.LAST_OK[0])))
        if self._boundary:
            self._cur_pre = None if b._context is None else np.zeros_like(b._context)
        else:
            self._cur_pre = None if b._context is None else b._context.copy()

    def call(self, fn, x, boundary=False, **kw):
        b = self.b
        self._boundary = boundary
        # default (no learn this call, i.e. the very first decision): the context before this decision, as in EXP-56
        if boundary:
            self._cur_pre = None if b._context is None else np.zeros_like(b._context)
        else:
            self._cur_pre = None if b._context is None else b._context.copy()
        out = fn(x, **kw)
        self.prev, self.pre = x.copy(), self._cur_pre
        return int(np.asarray(out).reshape(-1)[0])


TRAIN = dict(ctx5=(ObsTrace, False), hold5=(ObsTrace, True), out5=(OutcomeTrace, True), out5t=(LoggedOutcome, True),
             lab5=(LabelTrace, True), td5=(TDTrace, True), ctx5log=(LoggedObs, False))
READ = dict(ctx5=(ObsTrace, False), hold5=(ObsTrace, True), out5=(OutcomeTrace, True))    # every other arm reads plain


def auc(neg, pos):
    """P(a miss's forecast error < a success's), ties half: how well the brain's own error ranks misses below successes."""
    if not neg or not pos:
        return None
    neg, pos = np.asarray(neg), np.asarray(pos)
    less = (neg[:, None] < pos[None, :]).sum() + 0.5 * (neg[:, None] == pos[None, :]).sum()
    return float(less / (len(neg) * len(pos)))


def diagnose(tr, chain):
    log = getattr(tr, "log", None)
    if log is None:
        return {}
    d = dict(n_logged=len(log), ctx_changed_by_learn=tr.ctx_changed)
    dop = [(s, ok, v) for s, ok, v in log if np.isfinite(v)]
    d["auc_all"] = auc([v for s, ok, v in dop if not ok], [v for s, ok, v in dop if ok])
    d["auc_s1"] = auc([v for s, ok, v in dop if s == 0 and not ok], [v for s, ok, v in dop if s == 0 and ok])
    d["dop_mean"] = {f"s{s + 1}_{'ok' if ok else 'miss'}": (float(np.mean(v)) if (v := [x for t, o, x in dop if t == s
                     and o == ok]) else None) for s in range(4) for ok in (True, False)}
    d["n_s1"] = {"ok": sum(1 for s, ok, v in dop if s == 0 and ok), "miss": sum(1 for s, ok, v in dop if s == 0 and not ok)}
    held = getattr(tr, "held", None)
    if held is not None:
        miss_total = sum(1 for s, ok, v in log if not ok)
        d["held"] = dict(total=len(held), on_miss=sum(1 for s, ok in held if not ok), on_ok=sum(1 for s, ok in held if ok),
                         on_ok_s1=sum(1 for s, ok in held if ok and s == 0), misses=miss_total)
    return d


def life(chain, arm, signal, episodes, seed):
    E56.Chamber.x = E63.CHAINS[chain]
    E56.EPISODES = episodes
    cls, hold = TRAIN[arm]
    b = E56.compose(arm if arm != "ctx5log" else "ctx5", seed)
    tr = cls(b, hold)
    stats = E56.train(b, tr, signal)
    diag = diagnose(tr, chain)
    rcls, rhold = READ.get(arm, (ObsTrace, False))
    E56.Trace = rcls                        # E56.read builds its trace from this name
    with tempfile.TemporaryDirectory() as d:
        rd = E56.read(b.save(os.path.join(d, "b.npz")), rhold)
    return stats, rd, diag


def run(job):
    phase, chain, arm, signal, episodes, i, base = job
    import cadence as cd
    t0 = time.time()
    stats, rd, diag = life(chain, arm, signal, episodes, base + i)
    row = dict(phase=phase, chain=chain, arm=arm, signal=signal, episodes=episodes, seed=i, seed_base=base, **stats, **rd,
               diag=diag, secs=round(time.time() - t0, 1), cadence=cd.__version__)
    ft = " ".join("  - " if v is None else f"{v:.2f}" for v in rd["first_try"])
    h = diag.get("held", {})
    a1 = diag.get("auc_s1")
    print(f"  {chain:9s} {arm:5s} {signal:10s} s{i:2d}: exact {int(rd['greedy_exact'])} sampled {rd['sampled']:.2f} "
          f"first-try {ft} | held {h.get('on_miss', '-')}/{h.get('misses', '-')} misses, {h.get('on_ok', '-')} ok "
          f"({h.get('on_ok_s1', '-')} at s1) | auc s1 {'-' if a1 is None else f'{a1:.2f}'} ({row['secs']}s)", flush=True)
    return row


# ============ Check ============
READ_FIELDS = E63.READ_FIELDS


def _check_job(job):
    tag, chain, arm, signal, episodes, seed, thresh = job
    global TD_THRESH
    TD_THRESH = thresh
    stats, rd, diag = life(chain, arm, signal, episodes, seed)
    return job, {**stats, **rd, "diag": diag}


def check():
    import cadence as cd
    print(f"EXP-65 check: cadence {cd.__version__} from {os.path.dirname(cd.__file__)}", flush=True)
    stored_rows = [json.loads(l) for l in open(os.path.join(HERE, "EXP-63-full.jsonl"))]
    want = {}
    for chain, arm, signal in (("invisible", "ctx5", "natural"), ("invisible", "out5", "corrective"),
                               ("hidden", "out5", "corrective")):
        want[("stored", chain, arm, signal, 120, 63_000, 0.0)] = next(
            r for r in stored_rows if (r["chain"], r["arm"], r["signal"], r["seed"], r["episodes"]) == (chain, arm, signal, 0, 120))
    S = 65_990
    jobs = list(want) + [("ident", "invisible", "ctx5", "natural", 120, S, 0.0),
                         ("ident", "invisible", "td5", "natural", 120, S, float("-inf")),
                         ("ident", "invisible", "lab5", "natural", 120, S, 0.0),
                         ("ident", "invisible", "ctx5log", "natural", 120, S, 0.0),
                         ("pair", "invisible", "out5", "corrective", 120, S, 0.0),
                         ("pair", "invisible", "out5t", "corrective", 120, S, 0.0),
                         ("probe", "invisible", "td5", "natural", 120, S, 0.0),
                         ("probe", "invisible", "td5", "corrective", 120, S, 0.0)]
    with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
        got = dict(pool.map(_check_job, jobs))
    ok = True
    for job, r in want.items():
        same = all(got[job][f] == r[f] for f in READ_FIELDS)
        print(f"  EXP-63 row ({job[1]}, {job[2]}, {job[3]}, seed 0) recomputes identically through this script: {same}", flush=True)
        ok &= same
    base = got[("ident", "invisible", "ctx5", "natural", 120, S, 0.0)]
    for arm, th in (("td5", float("-inf")), ("lab5", 0.0), ("ctx5log", 0.0)):
        same = all(got[("ident", "invisible", arm, "natural", 120, S, th)][f] == base[f] for f in READ_FIELDS)
        print(f"  {arm:7s} (natural{', threshold -inf' if arm == 'td5' else ''}) identical to ctx5: {same} (expected True)", flush=True)
        ok &= same
    o, t = got[("pair", "invisible", "out5", "corrective", 120, S, 0.0)], got[("pair", "invisible", "out5t", "corrective", 120, S, 0.0)]
    same_train = all(o[f] == t[f] for f in ("train_success", "teacher_labels", "decisions"))
    same_greedy = o["greedy_exact"] == t["greedy_exact"]
    print(f"  out5t training identical to out5: {same_train}; greedy exact identical: {same_greedy} (expected True, True)", flush=True)
    ok &= same_train and same_greedy
    for sig in SIGNALS:
        g = got[("probe", "invisible", "td5", sig, 120, S, 0.0)]
        dg = g["diag"]
        live = any(v is not None and v != 0 for v in dg["dop_mean"].values())
        print(f"  td5 {sig}: learn() changed the context {dg['ctx_changed_by_learn']} times (expected 0); dopamine alive: {live}; "
              f"held {dg['held']}; auc s1 {dg['auc_s1']}, auc all {dg['auc_all']}; n s1 {dg['n_s1']}", flush=True)
        print(f"      dopamine means {json.dumps({k: (None if v is None else round(v, 4)) for k, v in dg['dop_mean'].items()})}", flush=True)
        ok &= dg["ctx_changed_by_learn"] == 0
    print(f"check: {'PASS' if ok else 'FAIL'}", flush=True)


# ============ Run ============
def plan():
    if PHASE == "pilot":     # chain links per arm on the invisible chain; seeds 63_500+ pair with EXP-63's pilot rows
        return [("invisible", 120, 6, 63_500)]
    return [("invisible", 120, 48, 63_000), ("hidden", 120, 24, 63_000)]


def mcnemar(b, c):
    return E63.mcnemar(b, c)


def main():
    t0 = time.time()
    ckpt = os.path.join(HERE, f"EXP-65-{PHASE}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["chain"], r["arm"], r["signal"], r["episodes"], r["seed"]) for r in rows}
    jobs = [(PHASE, chain, a, s, ep, i, base) for chain, ep, n, base in plan() for i in range(n) for s in SIGNALS
            for a in NEW[s] if (chain, a, s, ep, i) not in done]
    print(f"EXP-65 {PHASE}: {len(jobs)} lives to go ({len(done)} done); plan {plan()}; workers {WORKERS}; "
          f"td threshold {TD_THRESH}", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as fh:
                    fh.write(json.dumps(r) + "\n")
    ref_file = os.path.join(HERE, f"EXP-63-{PHASE}.jsonl")
    ref = [json.loads(l) for l in open(ref_file)] if os.path.exists(ref_file) else []
    by = {(r["chain"], r["arm"], r["signal"], r["episodes"], r["seed"]): r for r in ref + rows}
    sem = lambda x: float(np.std(x, ddof=1) / np.sqrt(len(x))) if len(x) > 1 else 0.0
    print(f"\nEXP-65 {PHASE} summary ({time.time() - t0:.0f}s); comparators from {os.path.basename(ref_file)}")
    summary = {}
    for chain, ep, n, base in plan():
        for scope in list(SIGNALS) + ["pooled"]:
            sigs = SIGNALS if scope == "pooled" else (scope,)
            arms = [a for a in ("ctx5", "hold5", "out5", "out5t", "lab5", "td5")
                    if all((chain, a, s, ep, i) in by for s in sigs for i in range(n))]
            o = dict(clean={}, first_try={}, sampled={}, pairs={}, diag={})
            for a in arms:
                rs = [by[(chain, a, s, ep, i)] for s in sigs for i in range(n)]
                o["clean"][a] = int(sum(r["greedy_exact"] for r in rs))
                o["first_try"][a] = [float(np.nanmean([np.nan if r["first_try"][k] is None else r["first_try"][k] for r in rs]))
                                     for k in range(4)]
                o["sampled"][a] = float(np.mean([r["sampled"] for r in rs]))
                dg = [r.get("diag") or {} for r in rs]
                if any(dg):
                    a1 = [x["auc_s1"] for x in dg if x.get("auc_s1") is not None]
                    aa = [x["auc_all"] for x in dg if x.get("auc_all") is not None]
                    hl = [x["held"] for x in dg if "held" in x]
                    o["diag"][a] = dict(auc_s1=(float(np.mean(a1)), sem(a1), len(a1)) if a1 else None,
                                        auc_all=(float(np.mean(aa)), sem(aa), len(aa)) if aa else None,
                                        held={k: int(sum(h[k] for h in hl)) for k in ("total", "on_miss", "on_ok", "on_ok_s1", "misses")}
                                        if hl else None)
            for x, y in (("lab5", "ctx5"), ("lab5", "out5"), ("td5", "ctx5"), ("td5", "hold5"), ("td5", "out5"),
                         ("out5t", "ctx5"), ("out5t", "out5"), ("lab5", "out5t")):
                if x not in arms or y not in arms:
                    continue
                pairs = [(by[(chain, x, s, ep, i)], by[(chain, y, s, ep, i)]) for s in sigs for i in range(n)]
                xb = sum(u["greedy_exact"] and not v["greedy_exact"] for u, v in pairs)
                yb = sum(v["greedy_exact"] and not u["greedy_exact"] for u, v in pairs)
                stage = []
                for k in range(4):
                    d = [u["first_try"][k] - v["first_try"][k] for u, v in pairs
                         if u["first_try"][k] is not None and v["first_try"][k] is not None]
                    stage.append((float(np.mean(d)), sem(d), len(d)) if d else (None, None, 0))
                r0 = [u["p_right"]["r0"] - v["p_right"]["r0"] for u, v in pairs
                      if u["p_right"]["r0"] is not None and v["p_right"]["r0"] is not None]
                sd = [u["sampled"] - v["sampled"] for u, v in pairs]
                o["pairs"][f"{x}-{y}"] = dict(n=len(pairs), x_only=xb, y_only=yb, p=mcnemar(xb, yb), stage=stage,
                                              r0=(float(np.mean(r0)), sem(r0)), sampled=(float(np.mean(sd)), sem(sd)))
            summary[f"{chain}-{ep}-{scope}"] = o
            print(f"  [{chain} ep{ep} {scope}] clean greedy " + "  ".join(f"{a} {o['clean'][a]}" for a in arms)
                  + " | sampled " + "  ".join(f"{a} {o['sampled'][a]:.3f}" for a in arms))
            for a in arms:
                line = f"      first try by stage {a:5s}: " + " ".join(f"{v:.2f}" for v in o["first_try"][a])
                if a in o["diag"]:
                    dg = o["diag"][a]
                    f = lambda t: "-" if t is None else f"{t[0]:.3f} ({t[1]:.3f}, n={t[2]})"
                    line += f" | auc s1 {f(dg['auc_s1'])} all {f(dg['auc_all'])} | held {dg['held']}"
                print(line)
            for name, q in o["pairs"].items():
                st = "  ".join(f"s{k + 1} {m:+.3f} ({se:.3f})" for k, (m, se, _) in enumerate(q["stage"]) if m is not None)
                print(f"      {name:11s} n={q['n']:3d} clean {name.split('-')[0]}-only {q['x_only']} / "
                      f"{name.split('-')[1]}-only {q['y_only']} (p {q['p']:.4f}) | first try {st} | all first tries "
                      f"{q['r0'][0]:+.3f} ({q['r0'][1]:.3f}) | sampled {q['sampled'][0]:+.3f} ({q['sampled'][1]:.3f})")
    json.dump(dict(rows=rows, summary=summary), open(os.path.join(HERE, f"EXP-65-{PHASE}.json"), "w"))


if __name__ == "__main__":
    check() if MODE == "check" else main()
