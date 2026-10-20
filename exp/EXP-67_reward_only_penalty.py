"""
EXP-67: can any failure cost help a learner with no teacher, or does it make the learner timid at every size?
EXP-66's chambers, brain, gate, readings and per-miss penalty (imported), under the natural signal only, with a finer
grid and one new form:
  ctx5     no cost, no gate (the base)               out5t    no cost, EXP-63's oracle gate during training
  pen@p    every non-terminal miss pays -p           peng@p   the same cost, gate keyed on reward < 0 (EXP-66's peng)
  penr@p   only a REPEAT miss at a stage within an attempt pays -p (the first miss there is free); no gate
Fresh seeds 67_000+, Cadence 0.84.3. Primary reading: sampled success vs ctx5, paired by seed.
PREDICTION: experiments/EXP-67.md (written before any data).

    MODE=check WORKERS=4 python -u EXP-67_reward_only_penalty.py
    WORKERS=4 python -u EXP-67_reward_only_penalty.py
"""
import importlib.util, json, os, tempfile, time
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("e66", os.path.join(HERE, "EXP-66_penalty_gate.py"))
E66 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E66)          # patches the chamber (stage, LAST_OK, EXP-66's penalty); defines RewardGate
E65, E63, E56, np = E66.E65, E66.E63, E66.E56, E66.np

MODE = os.environ.get("MODE", "run")
WORKERS = int(os.environ.get("WORKERS", 4))
SIGNAL = "natural"
SEED_BASE, CHECK_SEED = 67_000, 67_990
PLAN = (("invisible", 36), ("hidden", 36), ("visible", 24))
ARMS = ([("ctx5", 0.0), ("out5t", 0.0)] + [("pen", p) for p in (0.005, 0.01, 0.02, 0.05)]
        + [("peng", p) for p in (0.005, 0.01, 0.02)] + [("penr", p) for p in (0.005, 0.01, 0.02, 0.05)])
PENALISED = ("pen", "peng", "penr")
HELP_SEM, HARM_SEM = 3.0, 2.0

# ============ The cost: EXP-66's per-miss penalty, plus the repeat-only form ============
REPEAT = [False]
COUNT = dict(misses=0, first=0, charged=0)


def _execute(self, a):
    k = self.k                                        # stage at which this action is taken
    ok, r = E66._prev_execute(self, a)                # the chamber before EXP-66's penalty (stage + LAST_OK tracked)
    if E66.PEN_NOW[0] and not ok and not self.done:   # non-terminal miss; terminal +2 / -1 unchanged
        missed = self.__dict__.setdefault("_missed67", set())   # a new Chamber per attempt, so per attempt
        first = k not in missed
        missed.add(k)
        COUNT["misses"] += 1
        COUNT["first"] += first
        if not (REPEAT[0] and first):
            r = -E66.PEN_NOW[0]
            COUNT["charged"] += 1
    return ok, r


E56.Chamber.execute = _execute
TRAIN = dict(ctx5=E66.TRAIN["ctx5"], out5t=E66.TRAIN["out5t"], pen=(E65.LoggedObs, False), penr=(E65.LoggedObs, False),
             peng=(E66.RewardGate, True))


def life(chain, arm, episodes, seed, pen):
    E56.Chamber.x = E63.CHAINS[chain]
    E56.EPISODES = episodes
    E66.PEN_NOW[0] = pen if arm in PENALISED else 0.0
    REPEAT[0] = arm == "penr"
    for k in COUNT:
        COUNT[k] = 0
    cls, hold = TRAIN[arm]
    b = E56.compose("ctx5", seed)                     # memory_context .5 in every arm (EXP-66)
    tr = cls(b, hold)
    stats = E56.train(b, tr, SIGNAL)
    diag = E65.diagnose(tr, chain)
    diag["charges"] = dict(COUNT)
    E66.PEN_NOW[0], REPEAT[0] = 0.0, False
    E56.Trace = E66.ObsTrace                          # every arm reads plain
    with tempfile.TemporaryDirectory() as d:
        rd = E56.read(b.save(os.path.join(d, "b.npz")), False)
    return stats, rd, diag


def run(job):
    chain, arm, pen, i = job
    import cadence as cd
    t0 = time.time()
    stats, rd, diag = life(chain, arm, 120, SEED_BASE + i, pen)
    row = dict(chain=chain, arm=arm, pen=pen, seed=i, seed_base=SEED_BASE, signal=SIGNAL, **stats, **rd, diag=diag,
               secs=round(time.time() - t0, 1), cadence=cd.__version__)
    c = diag["charges"]
    print(f"  {chain:9s} {arm:5s} p{pen:.3f} s{i:2d}: exact {int(rd['greedy_exact'])} sampled {rd['sampled']:.2f} | "
          f"charged {c['charged']}/{c['misses']} misses ({row['secs']}s)", flush=True)
    return row


# ============ Check ============
def _check_job(job):
    tag, arm, pen = job
    if tag == "e66":                                  # EXP-66's own penalty code path, for (c)
        E56.Chamber.execute = E66._penalised_execute
        try:
            stats, rd, diag = E66.life("invisible", arm, SIGNAL, 120, CHECK_SEED, pen)
        finally:
            E56.Chamber.execute = _execute
        return job, {**stats, **rd}
    stats, rd, diag = life("invisible", arm, 120, CHECK_SEED, pen)
    return job, {**stats, **rd, "charges": diag["charges"]}


def check():
    import cadence as cd
    print(f"EXP-67 check: cadence {cd.__version__}", flush=True)
    jobs = [("ours", "ctx5", 0.0), ("ours", "pen", 0.0), ("ours", "peng", 0.0), ("ours", "penr", 0.0),
            ("ours", "penr", 0.02), ("ours", "pen", 0.02), ("ours", "pen", 0.05), ("e66", "pen", 0.05)]
    with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
        got = dict(pool.map(_check_job, jobs))
    F, ok = E66.READ_FIELDS, True
    base = got[jobs[0]]
    for j in jobs[1:4]:
        same = all(got[j][f] == base[f] for f in F)
        print(f"  (a) {j[1]} at p = 0 identical to ctx5: {same}", flush=True)
        ok &= same
    c = got[jobs[4]]["charges"]
    good = c["charged"] == c["misses"] - c["first"] and c["charged"] > 0
    print(f"  (b) penr at .02 charges exactly the repeat misses: {good} ({c})", flush=True)
    ok &= good
    c = got[jobs[5]]["charges"]
    good = c["charged"] == c["misses"] > 0
    print(f"  (b) pen at .02 charges every non-terminal miss: {good} ({c})", flush=True)
    ok &= good
    same = all(got[jobs[6]][f] == got[jobs[7]][f] for f in F)
    print(f"  (c) pen at .05 through this script identical to EXP-66's life(): {same}", flush=True)
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
    by = {(r["chain"], r["arm"], r["pen"], r["seed"]): r for r in rows}
    out = {}
    for chain, n in PLAN:
        o = {}
        base = [by[(chain, "ctx5", 0.0, i)] for i in range(n)]
        for arm, p in ARMS:
            rs = [by[(chain, arm, p, i)] for i in range(n)]
            d = [u["sampled"] - v["sampled"] for u, v in zip(rs, base)]
            xb = sum(u["greedy_exact"] and not v["greedy_exact"] for u, v in zip(rs, base))
            yb = sum(v["greedy_exact"] and not u["greedy_exact"] for u, v in zip(rs, base))
            a1 = [r["diag"]["auc_s1"] for r in rs if r["diag"].get("auc_s1") is not None]
            o[f"{arm}@{p}"] = dict(sampled=float(np.mean([r["sampled"] for r in rs])), delta=(float(np.mean(d)), sem(d)),
                                   clean=int(sum(r["greedy_exact"] for r in rs)), mcnemar=(xb, yb, E63.mcnemar(xb, yb)),
                                   auc_s1=float(np.mean(a1)) if a1 else None)
        for p in (0.005, 0.01, 0.02, 0.05):
            d = [by[(chain, "penr", p, i)]["sampled"] - by[(chain, "pen", p, i)]["sampled"] for i in range(n)]
            o[f"penr-pen@{p}"] = (float(np.mean(d)), sem(d))
        out[chain] = o
        print(f"\n  [{chain}] n={n} per arm, sampled success (delta vs ctx5, paired SEM) | clean greedy (vs ctx5 only)")
        for k, v in o.items():
            if k.startswith("penr-pen"):
                print(f"      {k:14s} {v[0]:+.3f} ({v[1]:.3f})")
            else:
                print(f"      {k:11s} {v['sampled']:.3f}  delta {v['delta'][0]:+.3f} ({v['delta'][1]:.3f})  clean {v['clean']} "
                      f"({v['mcnemar'][0]}/{v['mcnemar'][1]}, p {v['mcnemar'][2]:.3f})  auc s1 "
                      + ("-" if v["auc_s1"] is None else f"{v['auc_s1']:.3f}"))
    helps = []
    for arm, p in ARMS:
        if arm not in PENALISED:
            continue
        k = f"{arm}@{p}"
        vis = out["visible"][k]["delta"]
        if any(z(*out[c][k]["delta"]) >= HELP_SEM for c in ("invisible", "hidden")) and z(*vis) > -HARM_SEM:
            helps.append(k)
    p0 = z(*out["hidden"]["pen@0.05"]["delta"]) <= -HARM_SEM
    small = z(*out["hidden"]["pen@0.005"]["delta"]) <= -HARM_SEM
    verdict = "HELPS" if helps else ("TIMID AT EVERY SIZE" if small else "NULL")
    print(f"\n  P0 (pen@.05 hidden delta <= -2 SEM): {p0} | helping arms: {helps} | pen@.005 hidden harmful: {small}")
    print(f"  VERDICT: {verdict}")
    return dict(chains=out, helps=helps, p0=p0, smallest_harmful=small, verdict=verdict)


def main():
    t0 = time.time()
    ckpt = os.path.join(HERE, "EXP-67-full.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["chain"], r["arm"], r["pen"], r["seed"]) for r in rows}
    jobs = [(c, a, p, i) for c, n in PLAN for i in range(n) for a, p in ARMS if (c, a, p, i) not in done]
    print(f"EXP-67: {len(jobs)} lives to go ({len(done)} done); workers {WORKERS}", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as fh:
                    fh.write(json.dumps(r) + "\n")
    print(f"\nEXP-67 done in {time.time() - t0:.0f}s", flush=True)
    s = summary(rows)
    json.dump(dict(summary=s), open(os.path.join(HERE, "EXP-67-full.json"), "w"))


if __name__ == "__main__":
    check() if MODE == "check" else main()
