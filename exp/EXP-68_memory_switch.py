"""
EXP-68: is the failure cost's harm a switch in the memory, and which part of the memory?
EXP-67's life (imported) on the hidden chain under the natural signal, seeds 68_000+, 48 lives per arm:
  ctx5         no cost
  pen@p        p in {1e-6, 1e-4, .005}: every non-terminal miss pays -p
  penm@.005    the learner gets the cost, the episodic memory sees 0 (both _received and _record_outcome)
  penmR@.005   replay restored only: the path stores 0 for the cost, _record_outcome still sees it
  penmW@.005   writes removed only: _record_outcome sees 0, the path keeps the cost (replay still stops there)
The masks patch two private Brain methods in this process only (a probe, not a proposed change). Rewards with
|r| < .5 are the cost; terminal rewards (+2 / -1) are never masked.
PREDICTION: experiments/EXP-68.md (written before any data).

    MODE=check WORKERS=4 python -u EXP-68_memory_switch.py
    WORKERS=4 python -u EXP-68_memory_switch.py
"""
import importlib.util, json, os, time
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("e67", os.path.join(HERE, "EXP-67_reward_only_penalty.py"))
E67 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E67)
E63, np = E67.E63, E67.np
import cadence.generic as G

MODE = os.environ.get("MODE", "run")
WORKERS = int(os.environ.get("WORKERS", 4))
CHAIN, N, SEED_BASE, CHECK_SEED = "hidden", 48, 68_000, 68_990
ARMS = [("ctx5", 0.0), ("pen", 1e-6), ("pen", 1e-4), ("pen", 0.005), ("penm", 0.005), ("penmR", 0.005), ("penmW", 0.005)]
MASKS = {"pen": (False, False), "penm": (True, True), "penmR": (True, False), "penmW": (False, True)}  # (path, outcome)
BAR = 0.5

# ============ The probe: what the episodic memory sees of the cost ============
MASK = {"path": False, "outcome": False}
SEEN = {"path": 0, "outcome": 0}
_orig_received, _orig_record_outcome = G.Brain._received, G.Brain._record_outcome


def _small(r):
    return (r != 0) & (np.abs(r) < BAR)


def _received(self, reward):
    r = np.asarray(reward, dtype=float)
    if MASK["path"] and _small(r).any():
        r = np.where(_small(r), 0.0, r)
    SEEN["path"] += int(_small(r).sum())
    return _orig_received(self, r)


def _record_outcome(self, observations, action, reward, done, learned, woken=False, salience=None):
    r = np.asarray(reward, dtype=float)
    if MASK["outcome"] and _small(r).any():
        r = np.where(_small(r), 0.0, r)
    SEEN["outcome"] += int((_small(r) & np.asarray(learned, bool)).sum())
    return _orig_record_outcome(self, observations, action, r, done, learned, woken=woken, salience=salience)


G.Brain._received, G.Brain._record_outcome = _received, _record_outcome


def life(arm, seed, pen):
    MASK["path"], MASK["outcome"] = MASKS.get(arm, (False, False))
    for k in SEEN:
        SEEN[k] = 0
    try:
        stats, rd, diag = E67.life(CHAIN, "ctx5" if arm == "ctx5" else "pen", 120, seed, pen)
    finally:
        MASK["path"] = MASK["outcome"] = False
    diag["memory_saw"] = dict(SEEN)          # counted during training and reading; reading has no cost
    return stats, rd, diag


def run(job):
    arm, pen, i = job
    import cadence as cd
    t0 = time.time()
    stats, rd, diag = life(arm, SEED_BASE + i, pen)
    row = dict(chain=CHAIN, arm=arm, pen=pen, seed=i, seed_base=SEED_BASE, signal="natural", **stats, **rd, diag=diag,
               secs=round(time.time() - t0, 1), cadence=cd.__version__)
    c, s = diag["charges"], diag["memory_saw"]
    print(f"  {arm:5s} p{pen:g} s{i:2d}: sampled {rd['sampled']:.2f} exact {int(rd['greedy_exact'])} | charged "
          f"{c['charged']}/{c['misses']} | memory saw path {s['path']} outcome {s['outcome']} ({row['secs']}s)", flush=True)
    return row


# ============ Check ============
def _check_job(job):
    tag, arm, pen = job
    if tag == "e67":
        stats, rd, diag = E67.life(CHAIN, arm, 120, CHECK_SEED, pen)
        return job, {**stats, **rd}
    stats, rd, diag = life(arm, CHECK_SEED, pen)
    return job, {**stats, **rd, "charges": diag["charges"], "saw": diag["memory_saw"]}


def check():
    import cadence as cd
    print(f"EXP-68 check: cadence {cd.__version__}", flush=True)
    jobs = [("ours", "ctx5", 0.0), ("ours", "penm", 0.0), ("ours", "penmR", 0.0), ("ours", "penmW", 0.0),
            ("ours", "pen", 0.005), ("ours", "penm", 0.005), ("ours", "penmR", 0.005), ("ours", "penmW", 0.005),
            ("ours", "pen", 1e-6), ("e67", "pen", 0.005)]
    with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
        got = dict(pool.map(_check_job, jobs))
    F, ok = E67.E66.READ_FIELDS, True
    for j in jobs[1:4]:
        same = all(got[j][f] == got[jobs[0]][f] for f in F)
        print(f"  (a) {j[1]} at p = 0 identical to ctx5: {same}", flush=True)
        ok &= same
    want = {"pen": (True, True), "penm": (False, False), "penmR": (False, True), "penmW": (True, False)}
    for j in jobs[4:8]:
        s = got[j]["saw"]
        good = ((s["path"] > 0) == want[j[1]][0]) and ((s["outcome"] > 0) == want[j[1]][1])
        print(f"  (b) {j[1]} at .005, memory saw path {s['path']} outcome {s['outcome']}: {good}", flush=True)
        ok &= good
    c = got[jobs[8]]["charges"]
    good = c["charged"] == c["misses"] > 0 and got[jobs[8]]["saw"]["outcome"] > 0
    print(f"  (b) pen at 1e-6 charges every non-terminal miss and the memory sees it: {good} ({c})", flush=True)
    ok &= good
    same = all(got[jobs[4]][f] == got[jobs[9]][f] for f in F)
    print(f"  (c) pen at .005 through this script identical to EXP-67's life(): {same}", flush=True)
    ok &= same
    print(f"check: {'PASS' if ok else 'FAIL'}", flush=True)


# ============ Run + summary ============
def sem(x):
    return float(np.std(x, ddof=1) / np.sqrt(len(x))) if len(x) > 1 else 0.0


def z(m, s):
    if s == 0:
        return 0.0 if m == 0 else float(np.inf * np.sign(m))
    return m / s


def summary(rows):
    by = {(r["arm"], r["pen"], r["seed"]): r for r in rows}
    S = lambda a, p: np.array([by[(a, p, i)]["sampled"] for i in range(N)])
    base, out = S("ctx5", 0.0), {}
    for a, p in ARMS:
        x = S(a, p)
        d = x - base
        out[f"{a}@{p:g}"] = dict(sampled=float(x.mean()), delta=(float(d.mean()), sem(d)),
                                 clean=int(sum(by[(a, p, i)]["greedy_exact"] for i in range(N))),
                                 saw=dict(path=float(np.mean([by[(a, p, i)]["diag"]["memory_saw"]["path"] for i in range(N)])),
                                          outcome=float(np.mean([by[(a, p, i)]["diag"]["memory_saw"]["outcome"] for i in range(N)]))))
    pen = S("pen", 0.005)
    for a in ("penm", "penmR", "penmW"):
        d = S(a, 0.005) - pen
        out[f"{a}-pen@.005"] = (float(d.mean()), sem(d))
    d = (S("penmR", 0.005) - pen) + (S("penmW", 0.005) - pen) - (S("penm", 0.005) - pen)
    out["additivity (R + W - both)"] = (float(d.mean()), sem(d))
    print(f"\n  [{CHAIN}, natural] n={N} per arm: sampled success, delta vs ctx5 (paired SEM), clean greedy, memory saw "
          f"(path / outcome, mean per life)")
    for k, v in out.items():
        if isinstance(v, tuple):
            print(f"      {k:26s} {v[0]:+.3f} ({v[1]:.3f})")
        else:
            print(f"      {k:12s} {v['sampled']:.3f}  delta {v['delta'][0]:+.3f} ({v['delta'][1]:.3f})  clean {v['clean']}  "
                  f"saw {v['saw']['path']:.0f} / {v['saw']['outcome']:.0f}")
    switch = z(*out["pen@1e-06"]["delta"]) <= -2
    rec = z(*out["penm-pen@.005"]) >= 2 and z(*out["penm@0.005"]["delta"]) > -2
    verdict = ("MEMORY SWITCH" if rec else "SWITCH OUTSIDE THE MEMORY") if switch else "DOSE"
    print(f"\n  pen@1e-6 harmful at 2 SEM: {switch} | penm recovers: {rec}\n  VERDICT: {verdict}")
    return dict(arms=out, switch=switch, recovers=rec, verdict=verdict)


def main():
    t0 = time.time()
    ckpt = os.path.join(HERE, "EXP-68-full.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["arm"], r["pen"], r["seed"]) for r in rows}
    jobs = [(a, p, i) for i in range(N) for a, p in ARMS if (a, p, i) not in done]
    print(f"EXP-68: {len(jobs)} lives to go ({len(done)} done); workers {WORKERS}", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as fh:
                    fh.write(json.dumps(r) + "\n")
    print(f"\nEXP-68 done in {time.time() - t0:.0f}s", flush=True)
    json.dump(dict(summary=summary(rows)), open(os.path.join(HERE, "EXP-68-full.json"), "w"))


if __name__ == "__main__":
    check() if MODE == "check" else main()
