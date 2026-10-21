"""
EXP-69: does marking a miss with step(salience=) instead of charging it avoid the cost's harm on the reward-only chain?
EXP-68's life (imported; EXP-66/67's chambers, brain, cost and readings) on the hidden chain under the natural signal,
fresh seeds 69_000+, lateral = -0.5 set explicitly (upstream #220 may change the unset default). Arms, paired by seed:
  ctx5       no cost, no mark                                              seeds 0..95
  pen@.005   every non-terminal miss pays -.005 (EXP-66/67/68's cost)      seeds 0..47
  sal@.005   every non-terminal miss pays 0 and is marked salience=.005    seeds 0..95
  sal@1      the same mark at salience 1                                   seeds 0..47
What the library does with the mark (Cadence main be372b8, src/cadence/generic.py): salience= reaches only the episodic
memory. _received (3126-3133) stores the reward, not the salience, on the replay path, so a marked miss keeps 0.0 there and
the exact-zero replay test (3221-3223) does not stop at it. _record_outcome (3153-3154) turns salience > 0 into a known
outcome, so the miss is written as a record of value 0 (3160, _remember 3429). The actor-critic (learn 3380) never sees it.
PREDICTION: experiments/EXP-69.md (written before any data).

    MODE=check WORKERS=4 python -u EXP-69_salience_mark.py
    WORKERS=4 python -u EXP-69_salience_mark.py
"""
import importlib.util, json, os, time
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("e68", os.path.join(HERE, "EXP-68_memory_switch.py"))
E68 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E68)          # patches _received / _record_outcome with EXP-68's counters (masks off here)
E67 = E68.E67
E56, np, G = E67.E56, E67.np, E68.G

MODE = os.environ.get("MODE", "run")
WORKERS = int(os.environ.get("WORKERS", 4))
CHAIN, SEED_BASE, CHECK_SEED = "hidden", 69_000, 69_990
ARMS = [("ctx5", 0.0, 96), ("pen", 0.005, 48), ("sal", 0.005, 96), ("sal", 1.0, 48)]   # (arm, size, lives)
N = max(n for _, _, n in ARMS)
HALF = min(n for _, _, n in ARMS)

# ============ Pin: lateral set explicitly ============
LATERAL = [-0.5]                       # None leaves it unset (check (a) only, to show the pin changes nothing today)


def compose(arm, seed):
    import cadence as cd
    kw = {} if LATERAL[0] is None else dict(lateral=LATERAL[0])
    return cd.Brain.compose(7, 5, modules=(48, 24), seed=int(seed), arousal=True, memory_choice=True,
                            memory_context=E56.CONTEXT[arm], **kw)


E56.compose = compose                  # E67.life builds its brain through E56.compose

# ============ The mark: step(salience=s) on every non-terminal miss ============
SAL = [None]                           # None: no mark (ctx5, pen); a float: the salience passed on a miss
MISS = [False]                         # the last executed action was a miss that did not end the attempt
MARKS = dict(misses=0, marked=0, written=0)
REACH = dict(successes=0, reach=0, stopped=0)
TRAINED = {}
_inner_execute = E56.Chamber.execute   # EXP-67's execute (EXP-66's cost, EXP-63's LAST_OK, EXP-56's chamber)


def _execute(self, a):
    ok, r = _inner_execute(self, a)
    MISS[0] = (not ok) and (not self.done)
    MARKS["misses"] += MISS[0]
    return ok, r


E56.Chamber.execute = _execute
_step = G.Brain.step


def _marked_step(self, observations, **kw):
    if SAL[0] is not None and MISS[0] and kw.get("reward") is not None and not np.asarray(kw.get("done")).any():
        kw["salience"] = np.array([SAL[0]])
        MARKS["marked"] += 1
    MISS[0] = False
    return _step(self, observations, **kw)


G.Brain.step = _marked_step
_record_outcome_68 = G.Brain._record_outcome


def _record_outcome(self, observations, action, reward, done, learned, woken=False, salience=None):
    if salience is not None:           # a miss known only because it was marked: reward 0, not an end, salience > 0
        known = (np.asarray(salience) > 0) & (np.asarray(reward) == 0) & ~np.asarray(done) & np.asarray(learned, bool)
        MARKS["written"] += int(known.sum())
    return _record_outcome_68(self, observations, action, reward, done, learned, woken=woken, salience=salience)


G.Brain._record_outcome = _record_outcome
_replay = G.Brain._replay


def _measured_replay(self, reward, surprise, done, learned):
    """Read only: at each success that ends an attempt, how far back the exact-zero test lets replay walk, and whether
    it stopped at a decision whose received outcome was not nothing (the library's own test, generic.py 3221-3223)."""
    if self.memory_replay and len(self._paths) == len(reward):
        for row in np.flatnonzero((np.asarray(reward) > 0) & np.asarray(done) & np.asarray(learned, bool)):
            path = self._paths[row]
            full, k = min(len(path) - 1, self.memory_replay), 0
            while k < full and path[-2 - k][4] and path[-2 - k][3] == 0.0:
                k += 1
            REACH["successes"] += 1
            REACH["reach"] += k
            REACH["stopped"] += int(k < full and bool(path[-2 - k][4]) and path[-2 - k][3] != 0.0)
    return _replay(self, reward, surprise, done, learned)


G.Brain._replay = _measured_replay
_train = E56.train


def _counted_train(b, tr, signal):
    out = _train(b, tr, signal)
    TRAINED.update(marks=dict(MARKS), reach=dict(REACH))      # training only; the readings never call step
    return out


E56.train = _counted_train


def life(arm, seed, size):
    for d in (MARKS, REACH):
        for k in d:
            d[k] = 0
    TRAINED.clear()
    SAL[0] = size if arm == "sal" else None
    MISS[0] = False
    try:
        stats, rd, diag = E68.life("pen" if arm == "pen" else "ctx5", seed, size if arm == "pen" else 0.0)
    finally:
        SAL[0], MISS[0] = None, False
    diag.update(TRAINED)
    return stats, rd, diag


def run(job):
    arm, size, i = job
    import cadence as cd
    t0 = time.time()
    stats, rd, diag = life(arm, SEED_BASE + i, size)
    row = dict(chain=CHAIN, arm=arm, size=size, seed=i, seed_base=SEED_BASE, signal="natural", lateral=LATERAL[0],
               **stats, **rd, diag=diag, secs=round(time.time() - t0, 1), cadence=cd.__version__)
    m, r = diag["marks"], diag["reach"]
    print(f"  {arm:4s} {size:g} s{i:2d}: sampled {rd['sampled']:.2f} exact {int(rd['greedy_exact'])} | misses {m['misses']} "
          f"marked {m['marked']} written {m['written']} | successes {r['successes']} stopped {r['stopped']} "
          f"({row['secs']}s)", flush=True)
    return row


# ============ Check ============
def _check_job(job):
    tag, arm, size = job
    LATERAL[0] = None if tag == "unset" else -0.5
    t0 = time.time()
    stats, rd, diag = life(arm, CHECK_SEED, size)
    return job, {**stats, **rd, "diag": diag, "secs": time.time() - t0}


def check():
    import cadence as cd
    b = compose("ctx5", CHECK_SEED)
    d = b.describe()
    print(f"EXP-69 check: cadence {cd.__version__} from {os.path.dirname(cd.__file__)}", flush=True)
    print(f"  pinned brain: lateral {d.get('lateral')}, memory_replay {b.memory_replay}, gamma {b.basal_ganglia.config.gamma}, "
          f"hippocampus rate {b.hippocampus.rate} consolidation {b.hippocampus.consolidation} decay {b.hippocampus.decay}, "
          f"context memory rate {b.context_memory.rate} consolidation {b.context_memory.consolidation}, "
          f"temperature {b.learner.config.temperature}, working_memory_scale {d.get('working_memory_scale')}", flush=True)
    jobs = [("unset", "ctx5", 0.0), ("ours", "ctx5", 0.0), ("ours", "sal", 0.0), ("ours", "sal", 0.005),
            ("ours", "sal", 1.0), ("ours", "pen", 0.005), ("unset", "pen", 0.005)]
    with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
        got = dict(pool.map(_check_job, jobs))
    F, ok = E67.E66.READ_FIELDS, True
    same = lambda a, b: all(got[a][f] == got[b][f] for f in F)
    s = same(jobs[1], jobs[0])
    print(f"  (a) ctx5 with lateral -0.5 explicit identical to lateral unset (EXP-68's life): {s}", flush=True)
    ok &= s
    s = same(jobs[5], jobs[6])
    print(f"  (a) pen@.005 with lateral -0.5 explicit identical to lateral unset: {s}", flush=True)
    ok &= s
    m = got[jobs[2]]["diag"]["marks"]
    s = same(jobs[2], jobs[1]) and m["marked"] == m["misses"] > 0 and m["written"] == 0
    print(f"  (b) sal@0 (salience 0 passed at every miss) identical to ctx5, nothing written: {s} ({m})", flush=True)
    ok &= s
    for j in (jobs[3], jobs[4]):
        m, r, saw = got[j]["diag"]["marks"], got[j]["diag"]["reach"], got[j]["diag"]["memory_saw"]
        s = (m["marked"] == m["misses"] == m["written"] > 0 and saw["path"] == 0 and saw["outcome"] == 0
             and r["successes"] > 0 and r["stopped"] == 0)
        print(f"  (c) sal@{j[2]:g}: every miss marked and written, no nonzero miss reward reached the memory, replay never "
              f"stopped at a miss: {s} (marks {m}, memory saw {saw}, replay {r})", flush=True)
        ok &= s
    r, saw = got[jobs[5]]["diag"]["reach"], got[jobs[5]]["diag"]["memory_saw"]
    s = saw["path"] > 0 and r["stopped"] > 0
    print(f"  (d) pen@.005: the memory saw the cost and replay stopped at a charged miss: {s} (memory saw {saw}, replay {r})",
          flush=True)
    ok &= s
    r = got[jobs[1]]["diag"]["reach"]
    print(f"  (info) ctx5 replay {r}; train_success ctx5 {got[jobs[1]]['train_success']:.3f}, "
          f"sal@.005 {got[jobs[3]]['train_success']:.3f}, pen@.005 {got[jobs[5]]['train_success']:.3f}", flush=True)
    per = float(np.mean([v["secs"] for v in got.values()]))
    lives = sum(n for _, _, n in ARMS)
    print(f"  (time) {per:.1f} s per life in the check; full run {lives} lives, about {per * lives / max(1, WORKERS) / 60:.0f} "
          f"min at {WORKERS} workers", flush=True)
    print(f"check: {'PASS' if ok else 'FAIL'}", flush=True)


# ============ Run + summary ============
def sem(x):
    return float(np.std(x, ddof=1) / np.sqrt(len(x))) if len(x) > 1 else 0.0


def z(m, s):
    if s == 0:
        return 0.0 if m == 0 else float(np.inf * np.sign(m))
    return m / s


def summary(rows):
    by = {(r["arm"], r["size"], r["seed"]): r for r in rows}
    n = {(a, p): sum((a, p, i) in by for i in range(N)) for a, p, _ in ARMS}
    S = lambda a, p, m: np.array([by[(a, p, i)]["sampled"] for i in range(m)])
    out = {}

    def pair(a, p, b, q):
        m = min(n[(a, p)], n[(b, q)])
        d = S(a, p, m) - S(b, q, m)
        mu, se = float(d.mean()), sem(d)
        return dict(delta=mu, sem=se, z=z(mu, se), lo=mu - 1.96 * se, hi=mu + 1.96 * se, n=m)

    for a, p, _ in ARMS:
        m = n[(a, p)]
        rs = [by[(a, p, i)] for i in range(m)]
        ft = np.array([[np.nan if v is None else v for v in r["first_try"]] for r in rs], float)
        out[f"{a}@{p:g}"] = dict(
            n=m, sampled=float(S(a, p, m).mean()), sampled_sem=sem(S(a, p, m)), vs_ctx5=pair(a, p, "ctx5", 0.0),
            clean=int(sum(r["greedy_exact"] for r in rs)), train_success=float(np.mean([r["train_success"] for r in rs])),
            first_try=[float(x) for x in np.nanmean(ft, axis=0)],
            misses=float(np.mean([r["diag"]["marks"]["misses"] for r in rs])),
            marked=float(np.mean([r["diag"]["marks"]["marked"] for r in rs])),
            written=float(np.mean([r["diag"]["marks"]["written"] for r in rs])),
            successes=int(sum(r["diag"]["reach"]["successes"] for r in rs)),
            stopped=int(sum(r["diag"]["reach"]["stopped"] for r in rs)),
            reach=float(sum(r["diag"]["reach"]["reach"] for r in rs) / max(1, sum(r["diag"]["reach"]["successes"] for r in rs))))
    con = {"sal@.005 - pen@.005": pair("sal", 0.005, "pen", 0.005), "sal@1 - sal@.005": pair("sal", 1.0, "sal", 0.005),
           "sal@1 - pen@.005": pair("sal", 1.0, "pen", 0.005)}
    print(f"\n  [{CHAIN}, natural] sampled success; delta vs ctx5 paired by seed (SEM) [95% interval]; clean greedy; training "
          f"misses / marked / written per life; replay at successes: stopped / successes, mean reach")
    for k, v in out.items():
        c = v["vs_ctx5"]
        print(f"      {k:9s} n={v['n']:2d} {v['sampled']:.3f}  delta {c['delta']:+.3f} ({c['sem']:.3f}) "
              f"[{c['lo']:+.3f}, {c['hi']:+.3f}]  clean {v['clean']}  first-try {['%.2f' % x for x in v['first_try']]}  "
              f"misses {v['misses']:.0f} marked {v['marked']:.0f} written {v['written']:.0f}  "
              f"stopped {v['stopped']}/{v['successes']} reach {v['reach']:.2f}")
    for k, c in con.items():
        print(f"      {k:20s} {c['delta']:+.3f} ({c['sem']:.3f}) [{c['lo']:+.3f}, {c['hi']:+.3f}] n={c['n']}")
    p0 = out["pen@0.005"]["vs_ctx5"]["z"] <= -2
    rescue = con["sal@.005 - pen@.005"]["z"] >= 2
    safe = out["sal@0.005"]["vs_ctx5"]["z"] > -2
    verdict = ("VOID (P0 failed)" if not p0 else
               "SAFE SWAP" if rescue and safe else "PARTIAL" if rescue else "NO RESCUE")
    print(f"\n  P0 (pen@.005 harmful at 2 SEM): {p0} | rescue (sal@.005 above pen@.005 by 2 SEM): {rescue} | "
          f"safe (sal@.005 not below ctx5 by 2 SEM): {safe}\n  VERDICT: {verdict}")
    return dict(arms=out, contrasts=con, p0=p0, rescue=rescue, safe=safe, verdict=verdict)


def main():
    t0 = time.time()
    ckpt = os.path.join(HERE, "EXP-69-full.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["arm"], r["size"], r["seed"]) for r in rows}
    jobs = [(a, p, i) for i in range(N) for a, p, m in ARMS if i < m and (a, p, i) not in done]
    print(f"EXP-69: {len(jobs)} lives to go ({len(done)} done); workers {WORKERS}; lateral {LATERAL[0]}", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as fh:
                    fh.write(json.dumps(r) + "\n")
    print(f"\nEXP-69 done in {time.time() - t0:.0f}s", flush=True)
    json.dump(dict(summary=summary(rows)), open(os.path.join(HERE, "EXP-69-full.json"), "w"))


if __name__ == "__main__":
    check() if MODE == "check" else main()
