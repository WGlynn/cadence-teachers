"""
EXP-63: an outcome-keyed gate. Hold out of Cadence's temporal context (the episodic key) only decisions the world answered
as failures (the chamber's own success flag for that decision), not every decision whose next observation is unchanged
(EXP-57's rule, `hold5`). Three chains, EXP-56's brain, signals, trace rule and readings:
  hidden    A, B, A, B   (EXP-56/57: progress is not in the observation)
  visible   inventory    (EXP-60: progress is in the observation)
  invisible A, A, B, C   (EXP-59: the correct WOOD changes nothing visible)
On the hidden and visible chains a wrong action is the only decision that leaves the observation unchanged, so the two
gates hold the same decisions (MODE=check verifies it per seed); they differ only on the invisible chain.
Arms: ctx5 (the founder key, memory_context .5), hold5 (observation gate), out5 (outcome gate).
PREDICTION: experiments/EXP-63.md (written before any run).

    MODE=check WORKERS=2 python -u EXP-63_outcome_gate.py
    PHASE=pilot WORKERS=2 python -u EXP-63_outcome_gate.py
    PHASE=full HORIZON=120 WORKERS=2 python -u EXP-63_outcome_gate.py
"""
import importlib.util, json, os, tempfile, time
from math import comb
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("e56", os.path.join(HERE, "EXP-56_ambiguous_chain_trace.py"))
E56 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E56)
np = E56.np

MODE = os.environ.get("MODE", "run")
PHASE = os.environ.get("PHASE", "full")
WORKERS = int(os.environ.get("WORKERS", 2))
HORIZON = int(os.environ.get("HORIZON", 120))     # the invisible chain's horizon in the full run, fixed by the pilot
SIGNALS = ("natural", "corrective")
E56.CONTEXT["out5"] = 0.5

# ============ The three chains (observations copied from EXP-56, EXP-60, EXP-59) ============
OBS_C = np.array([[0.35, 1.0, 1.0, 0.0, 0.5, 0.5, 1.0]])                # EXP-59
INVISIBLE = [E56.OBS_A, E56.OBS_A, E56.OBS_B, OBS_C]                    # the first (correct) WOOD changes nothing visible
VISIBLE = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1)]                  # EXP-60 / EXP-45: has wood, stone, fire


def x_hidden(self):
    return (E56.OBS_A if self.k % 2 == 0 else E56.OBS_B).copy()


def x_visible(self):
    w, s, f = VISIBLE[self.k]
    return np.array([[0.35, float(w), float(s), float(f), w / 2.0, s / 2.0, 1.0]])


def x_invisible(self):
    return INVISIBLE[self.k].copy()


CHAINS = dict(hidden=x_hidden, visible=x_visible, invisible=x_invisible)

# ============ The outcome gate ============
LAST_OK = [None]                     # the world's answer to the stream's last decision (the chamber's success flag)
_execute = E56.Chamber.execute


def _tracked_execute(self, a):
    ok, r = _execute(self, a)
    LAST_OK[0] = bool(ok)
    return ok, r


E56.Chamber.execute = _tracked_execute
ObsTrace = E56.Trace


class OutcomeTrace(ObsTrace):
    """EXP-56's trace rule keyed on the outcome: a decision the world answered as a failure never enters the stream's
    temporal context (the context is restored to its value before that decision); a correct decision always enters,
    whether or not it changed the observation. Never across a boundary."""

    def call(self, fn, x, boundary=False, **kw):
        b = self.b
        if self.hold and not boundary and self.prev is not None and LAST_OK[0] is False:
            b._context = None if self.pre is None else self.pre.copy()
        if boundary:     # the library clears the stream's context at done; the decision starts from an empty one
            pre = None if b._context is None else np.zeros_like(b._context)
        else:
            pre = None if b._context is None else b._context.copy()
        out = fn(x, **kw)
        self.prev, self.pre = x.copy(), pre
        return int(np.asarray(out).reshape(-1)[0])


def life(chain, arm, signal, episodes, seed):
    E56.Chamber.x = CHAINS[chain]
    E56.EPISODES = episodes
    E56.Trace = OutcomeTrace if arm == "out5" else ObsTrace       # E56.read builds its trace from this name
    hold = arm in ("hold5", "out5")
    b = E56.compose(arm, seed)
    stats = E56.train(b, E56.Trace(b, hold), signal)
    with tempfile.TemporaryDirectory() as d:
        rd = E56.read(b.save(os.path.join(d, "b.npz")), hold)
    return stats, rd


def run(job):
    phase, chain, arm, signal, episodes, i, base = job
    import cadence as cd
    t0 = time.time()
    stats, rd = life(chain, arm, signal, episodes, base + i)
    row = dict(phase=phase, chain=chain, arm=arm, signal=signal, episodes=episodes, seed=i, seed_base=base, **stats, **rd,
               secs=round(time.time() - t0, 1), cadence=cd.__version__)
    ft = " ".join("  - " if v is None else f"{v:.2f}" for v in rd["first_try"])
    print(f"  {chain:9s} {arm:5s} {signal:10s} ep{episodes} s{i:2d}: exact {int(rd['greedy_exact'])} sampled "
          f"{rd['sampled']:.2f} first-try {ft} ({row['secs']}s)", flush=True)
    return row


def mcnemar(b, c):
    n = b + c
    return min(1.0, 2 * sum(comb(n, k) for k in range(min(b, c) + 1)) / 2 ** n) if n else 1.0


# ============ Check: version identity with stored rows, and gate identity where the gates must agree ============
READ_FIELDS = ("train_success", "teacher_labels", "decisions", "sampled", "greedy_exact", "greedy_win", "greedy_stages",
               "p_right", "n_right", "first_try", "repeat_miss", "n_retries")


def _check_job(job):
    kind, chain, arm, signal, episodes, seed = job
    stats, rd = life(chain, arm, signal, episodes, seed)
    return job, {**stats, **rd}


def check():
    import cadence as cd
    print(f"EXP-63 check: cadence {cd.__version__} from {os.path.dirname(cd.__file__)}", flush=True)
    stored = {}
    for exp, chain, arm, signal, episodes, base in (("EXP-57", "hidden", "ctx5", "natural", 120, 57_000),
                                                    ("EXP-57", "hidden", "hold5", "corrective", 120, 57_000),
                                                    ("EXP-59", "invisible", "hold5", "natural", 120, 59_000),
                                                    ("EXP-60", "visible", "ctx5", "corrective", 120, 60_000)):
        rows = [json.loads(l) for l in open(os.path.join(HERE, f"{exp}-full.jsonl"))]
        r = next(r for r in rows if r["arm"] == arm and r["signal"] == signal and r["seed"] == 0
                 and r.get("episodes", 120) == episodes)
        stored[("stored", chain, arm, signal, episodes, base)] = (exp, r)
    jobs = list(stored)
    for chain in ("hidden", "visible", "invisible"):
        for arm in ("hold5", "out5"):
            for signal in (SIGNALS if chain != "invisible" else ("natural",)):
                jobs.append(("gate", chain, arm, signal, 120, 63_990))
    with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
        got = dict(pool.map(_check_job, jobs))
    ok = True
    for job, (exp, r) in stored.items():
        same = all(got[job][f] == r[f] for f in READ_FIELDS)
        print(f"  {exp} row ({job[1]}, {job[2]}, {job[3]}, seed {job[5]}) at {cd.__version__} head identical to the stored "
              f"23dba71 row: {same}", flush=True)
        ok &= same
    for chain in ("hidden", "visible", "invisible"):
        for signal in (SIGNALS if chain != "invisible" else ("natural",)):
            h, o = got[("gate", chain, "hold5", signal, 120, 63_990)], got[("gate", chain, "out5", signal, 120, 63_990)]
            same = all(h[f] == o[f] for f in READ_FIELDS)
            want = chain != "invisible"
            print(f"  {chain:9s} {signal:10s}: out5 row identical to hold5 row: {same} (expected {want})", flush=True)
            ok &= same == want
    print(f"check: {'PASS' if ok else 'FAIL'}", flush=True)


# ============ Run ============
def plan():
    if PHASE == "pilot":     # the effect window on the invisible chain: horizon 120 vs 240, fresh seeds never reused
        return [("invisible", ("ctx5", "hold5", "out5"), ep, 6, 63_500) for ep in (120, 240)]
    return [("invisible", ("ctx5", "hold5", "out5"), HORIZON, 48, 63_000),
            ("hidden", ("ctx5", "out5"), 120, 24, 63_000),
            ("visible", ("ctx5", "out5"), 120, 24, 63_000)]


def main():
    t0 = time.time()
    ckpt = os.path.join(HERE, f"EXP-63-{PHASE}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["chain"], r["arm"], r["signal"], r["episodes"], r["seed"]) for r in rows}
    jobs = [(PHASE, chain, a, s, ep, i, base) for chain, arms, ep, n, base in plan() for i in range(n) for s in SIGNALS
            for a in arms if (chain, a, s, ep, i) not in done]
    print(f"EXP-63 {PHASE}: {len(jobs)} lives to go ({len(done)} done); plan {plan()}; workers {WORKERS}", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as fh:
                    fh.write(json.dumps(r) + "\n")
    by = {(r["chain"], r["arm"], r["signal"], r["episodes"], r["seed"]): r for r in rows}
    sem = lambda x: float(np.std(x, ddof=1) / np.sqrt(len(x))) if len(x) > 1 else 0.0
    print(f"\nEXP-63 {PHASE} summary ({time.time() - t0:.0f}s)")
    summary = {}
    for chain, arms, ep, n, base in plan():
        for scope in list(SIGNALS) + ["pooled"]:
            sigs = SIGNALS if scope == "pooled" else (scope,)
            o = dict(first_try={}, clean={}, sampled={}, pairs={})
            for a in arms:
                rs = [by[(chain, a, s, ep, i)] for s in sigs for i in range(n) if (chain, a, s, ep, i) in by]
                o["first_try"][a] = [float(np.nanmean([np.nan if r["first_try"][k] is None else r["first_try"][k]
                                                       for r in rs])) for k in range(4)]
                o["clean"][a] = int(sum(r["greedy_exact"] for r in rs))
                o["sampled"][a] = float(np.mean([r["sampled"] for r in rs]))
            for x, y in (("out5", "ctx5"), ("out5", "hold5"), ("hold5", "ctx5")):
                if x not in arms or y not in arms:
                    continue
                pairs = [(by[(chain, x, s, ep, i)], by[(chain, y, s, ep, i)]) for s in sigs for i in range(n)
                         if (chain, x, s, ep, i) in by and (chain, y, s, ep, i) in by]
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
                print(f"      first try by stage {a:5s}: " + " ".join(f"{v:.2f}" for v in o["first_try"][a]))
            for name, q in o["pairs"].items():
                st = "  ".join(f"s{k + 1} {m:+.3f} ({se:.3f})" for k, (m, se, _) in enumerate(q["stage"]) if m is not None)
                print(f"      {name:10s} n={q['n']:3d} clean {name.split('-')[0]}-only {q['x_only']} / "
                      f"{name.split('-')[1]}-only {q['y_only']} (p {q['p']:.4f}) | first try {st} | all first tries "
                      f"{q['r0'][0]:+.3f} ({q['r0'][1]:.3f}) | sampled {q['sampled'][0]:+.3f} ({q['sampled'][1]:.3f})")
    json.dump(dict(rows=rows, summary=summary), open(os.path.join(HERE, f"EXP-63-{PHASE}.json"), "w"))


if __name__ == "__main__":
    check() if MODE == "check" else main()
