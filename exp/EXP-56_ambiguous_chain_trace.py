"""
EXP-56: on an ambiguous chain (A->WOOD, B->STONE, A->FIRE, B->WARM, the two A's and the two B's byte-identical; Huncho's
V7.2), does Cadence 0.83's fixed temporal context fail because misses push the one memory that matters out of the key?

Chamber: EXP-45's V5 chamber (5 actions, strict order, a wrong action changes nothing, 10 decisions per attempt, +2 success
/ -1 timeout, V5 event order) with two observations, A at stages 1 and 3 and B at stages 2 and 4. Brain: 0.83
Brain.compose(7, 5, modules=(48, 24), arousal=True, memory_choice=True), efference off (the composed default here).
Arms (paired by seed): place (memory_context 0), ctx5 (0.5), ctx8 (0.8), hold5 (0.5, and a decision whose next
observation is unchanged never enters the temporal context: the instrument restores the stream's context to its value
before that decision; never across done). Signals: natural (world reward), corrective (V5 corrective teacher).
Readings on a saved copy with the same trace rule, all in sequence: sampled success (EVAL attempts), greedy exact pass,
greedy stages, P(right | r misses already made at this stage), first-try accuracy per stage.
PREDICTION: experiments/EXP-56.md (written before the pilot).

    MODE=check python -u EXP-56_ambiguous_chain_trace.py
    SEEDS=2 TAG=pilot python -u EXP-56_ambiguous_chain_trace.py
    SEEDS=24 WORKERS=4 TAG=full python -u EXP-56_ambiguous_chain_trace.py
"""
import json, os, sys, tempfile, time
from multiprocessing import get_context

CADENCE_SRC = os.path.expanduser(os.environ.get("CADENCE_SRC", "~/_cadence_study/src"))
sys.path.insert(0, CADENCE_SRC)
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
MODE = os.environ.get("MODE", "run")
SEEDS = int(os.environ.get("SEEDS", 24))
EPISODES = int(os.environ.get("EPISODES", 120))
EVAL = int(os.environ.get("EVAL", 100))
WORKERS = int(os.environ.get("WORKERS", 4))
TAG = os.environ.get("TAG", "full")
ARMS = os.environ.get("ARMS", "place,ctx5,ctx8,hold5").split(",")
SIGNALS = os.environ.get("SIGNALS", "natural,corrective").split(",")
CONTEXT = dict(place=0.0, ctx5=0.5, ctx8=0.8, hold5=0.5)
MAX_DECISIONS, SUCCESS, FAILURE = 10, 2.0, -1.0
GUIDED, AUTONOMOUS = 4, 8
WOOD, STONE, FIRE, WARM, WAIT = range(5)
RIGHTS = [WOOD, STONE, FIRE, WARM]
OBS_A = np.array([[0.35, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]])   # stages 1 and 3, byte-identical
OBS_B = np.array([[0.35, 1.0, 0.0, 0.0, 0.5, 0.0, 1.0]])   # stages 2 and 4, byte-identical


class Chamber:
    def __init__(self):
        self.k, self.t, self.done, self.success = 0, 0, False, False

    def x(self):
        return (OBS_A if self.k % 2 == 0 else OBS_B).copy()

    def right(self):
        return RIGHTS[self.k]

    def execute(self, a):
        ok = a == self.right()
        if ok:
            self.k += 1
            if self.k == 4:
                self.success = self.done = True
        self.t += 1
        if not self.done and self.t >= MAX_DECISIONS:
            self.done = True
        return ok, ((SUCCESS if self.success else FAILURE) if self.done else 0.0)


class Trace:
    """Calls into the brain. With hold, a decision whose next observation is unchanged never enters the stream's temporal
    context: before the next call the context is restored to its value before that decision. Never across a boundary."""

    def __init__(self, brain, hold):
        self.b, self.hold = brain, hold
        self.reset()

    def reset(self):
        self.prev, self.pre = None, None

    def call(self, fn, x, boundary=False, **kw):
        b = self.b
        if self.hold and not boundary and self.prev is not None and np.array_equal(x, self.prev):
            b._context = None if self.pre is None else self.pre.copy()
        if boundary:     # the library clears the stream's context at done; the decision starts from an empty one
            pre = None if b._context is None else np.zeros_like(b._context)
        else:
            pre = None if b._context is None else b._context.copy()
        out = fn(x, **kw)
        self.prev, self.pre = x.copy(), pre
        return int(np.asarray(out).reshape(-1)[0])


def compose(arm, seed):
    import cadence as cd
    return cd.Brain.compose(7, 5, modules=(48, 24), seed=int(seed), arousal=True, memory_choice=True,
                            memory_context=CONTEXT[arm])


def train(b, tr, signal):
    c, g, wins, teach = Chamber(), 0, 0, 0
    a = tr.call(b.step, c.x())
    for _ in range(EPISODES):
        while True:
            guided = (g % (GUIDED + AUTONOMOUS)) < GUIDED
            right = c.right()
            ok, r = c.execute(a)
            teacher = np.array([right]) if (signal == "corrective" and guided and not ok and not c.done) else None
            teach += teacher is not None
            g += 1
            if c.done:
                wins += c.success
                c = Chamber()
                a = tr.call(b.step, c.x(), boundary=True, reward=np.array([r]), done=np.array([True]))
                break
            kw = dict(reward=np.array([r]), done=np.array([False]))
            if teacher is not None:
                kw["teacher"] = teacher
            a = tr.call(b.step, c.x(), **kw)
    b.reset()
    tr.reset()
    return dict(train_success=wins / EPISODES, teacher_labels=teach, decisions=g)


def attempt(b, tr, greedy, log=None):
    b.reset()
    tr.reset()
    c, miss, last = Chamber(), 0, None
    while not c.done:
        k = c.k
        a = tr.call(lambda x: b.act(x, greedy=greedy), c.x())
        ok, _ = c.execute(a)
        if log is not None:
            log.append((k, miss, bool(ok), (a == last) if miss else None))
        miss, last = (0, None) if ok else (miss + 1, a)
    return c.success, c.k, c.t


def read(path, hold):
    import cadence as cd
    b = cd.Brain.load(path)
    win, stages, t = attempt(b, Trace(b, hold), True)
    b = cd.Brain.load(path)
    tr, log = Trace(b, hold), []
    sampled = float(np.mean([attempt(b, tr, False, log)[0] for _ in range(EVAL)]))
    def p(sel):
        v = [e[2] for e in log if sel(e[0], e[1])]
        return (float(np.mean(v)) if v else None), len(v)
    pr = {f"r{n}": p(f) for n, f in (("0", lambda k, m: m == 0), ("1", lambda k, m: m == 1), ("2+", lambda k, m: m >= 2),
                                    ("1+", lambda k, m: m >= 1))}
    first = [p(lambda k, m, s=s: k == s and m == 0) for s in range(4)]
    rep = [e[3] for e in log if e[3] is not None]          # post-hoc (added after the pilot): a retry repeats the miss
    return dict(sampled=sampled, greedy_exact=bool(win and t == 4), greedy_win=bool(win), greedy_stages=int(stages),
                p_right={k: v[0] for k, v in pr.items()}, n_right={k: v[1] for k, v in pr.items()},
                first_try=[f[0] for f in first], repeat_miss=(float(np.mean(rep)) if rep else None), n_retries=len(rep))


def run(job):
    arm, signal, i = job
    import cadence as cd
    t0 = time.time()
    seed = 56_000 + i
    b = compose(arm, seed)
    stats = train(b, Trace(b, arm == "hold5"), signal)
    with tempfile.TemporaryDirectory() as d:
        rd = read(b.save(os.path.join(d, "b.npz")), arm == "hold5")
    row = dict(arm=arm, signal=signal, seed=i, **stats, **rd, secs=round(time.time() - t0, 1), cadence=cd.__version__)
    pr = rd["p_right"]
    f = lambda v: "  - " if v is None else f"{v:.2f}"
    print(f"  {arm:5s} {signal:10s} s{i:2d}: sampled {rd['sampled']:.2f} greedy exact {int(rd['greedy_exact'])} stages "
          f"{rd['greedy_stages']} | P(right|r) r0 {f(pr['r0'])} r1 {f(pr['r1'])} r2+ {f(pr['r2+'])} | first-try "
          f"{' '.join(f(v) for v in rd['first_try'])} | repeat {f(rd['repeat_miss'])} | train {stats['train_success']:.2f} ({row['secs']}s)", flush=True)
    return row


def check():
    """The hold rule, mechanically: with hold, a retry's decision key equals the first try's; without, it differs."""
    import cadence as cd
    print(f"EXP-56 check: cadence {cd.__version__} from {os.path.dirname(cd.__file__)}", flush=True)
    ok = True
    for hold in (False, True):
        b = compose("ctx5", 56_000)
        tr = Trace(b, hold)
        b.reset()
        keys = []
        for _ in range(3):                                   # three decisions on the same observation (two retries)
            tr.call(lambda x: b.act(x, greedy=True), OBS_A)
            keys.append(b._decision.copy())
        same = all(np.array_equal(keys[0], k) for k in keys[1:])
        print(f"  hold={hold}: retry keys equal to first try: {same}", flush=True)
        ok &= same == hold
    b = compose("place", 56_000)
    print(f"  place arm has no context store: {b.context_memory is None}", flush=True)
    ok &= b.context_memory is None
    print(f"check: {'PASS' if ok else 'FAIL'}", flush=True)


def main():
    t0 = time.time()
    ckpt = os.path.join(HERE, f"EXP-56-{TAG}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["arm"], r["signal"], r["seed"]) for r in rows}
    jobs = [(a, s, i) for i in range(SEEDS) for s in SIGNALS for a in ARMS if (a, s, i) not in done]
    print(f"EXP-56: {len(jobs)} lives to go ({len(done)} done); arms {ARMS}; signals {SIGNALS}; {EPISODES} attempts", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as fh:
                    fh.write(json.dumps(r) + "\n")
    rows = [r for r in rows if r["seed"] < SEEDS]
    sem = lambda x: float(np.std(x, ddof=1) / np.sqrt(len(x))) if len(x) > 1 else 0.0
    by = {(r["arm"], r["signal"], r["seed"]): r for r in rows}
    print(f"\nEXP-56 summary ({time.time() - t0:.0f}s), {SEEDS} seeds; chance: uniform .121, never-repeat .304, P(right) .2")
    summary = {}
    for scope in SIGNALS + ["pooled"]:
        sigs = SIGNALS if scope == "pooled" else [scope]
        keys = [(s, i) for s in sigs for i in range(SEEDS) if all((a, s, i) in by for a in ARMS)]
        o = {}
        for a in ARMS:
            rs = [by[(a, s, i)] for s, i in keys]
            o[a] = dict(sampled=float(np.mean([r["sampled"] for r in rs])),
                        greedy_exact=int(sum(r["greedy_exact"] for r in rs)), n=len(rs),
                        p_r0=float(np.nanmean([np.nan if r["p_right"]["r0"] is None else r["p_right"]["r0"] for r in rs])),
                        p_r1p=float(np.nanmean([np.nan if r["p_right"]["r1+"] is None else r["p_right"]["r1+"] for r in rs])),
                        repeat=float(np.nanmean([np.nan if r.get("repeat_miss") is None else r["repeat_miss"] for r in rs])))
        def diff(x, y, key):
            d = []
            for s, i in keys:
                u, v = by[(x, s, i)], by[(y, s, i)]
                if key == "sampled":
                    d.append(u["sampled"] - v["sampled"])
                else:
                    pu, pv = u["p_right"][key], v["p_right"][key]
                    if pu is not None and pv is not None:
                        d.append(pu - pv)
            return (float(np.mean(d)), sem(d), len(d)) if d else (None, None, 0)
        o["diffs"] = {f"{x}-{y} {k}": diff(x, y, k) for x, y in (("ctx5", "place"), ("hold5", "ctx5"), ("ctx8", "ctx5"),
                                                                  ("hold5", "ctx8")) if x in ARMS and y in ARMS
                      for k in ("sampled", "r0", "r1+")}
        summary[scope] = o
        print(f"  [{scope}] " + "  ".join(f"{a} sampled {o[a]['sampled']:.3f} exact {o[a]['greedy_exact']}/{o[a]['n']} "
                                          f"P(r0) {o[a]['p_r0']:.2f} P(r1+) {o[a]['p_r1p']:.2f} repeat {o[a]['repeat']:.2f}" for a in ARMS))
        for name, (m, se, n) in o["diffs"].items():
            if m is not None:
                print(f"      {name:22s} {m:+.3f} (SEM {se:.3f}, n={n})")
    json.dump(dict(rows=rows, summary=summary), open(os.path.join(HERE, f"EXP-56-{TAG}.json"), "w"))


if __name__ == "__main__":
    check() if MODE == "check" else main()
