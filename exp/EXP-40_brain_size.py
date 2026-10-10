"""
EXP-40: are our brains too small? Brain size x world size in the teaching network (first experiment run on the
`teachers` library).

Will (2026-10-10): "are our brains too small? would we benefit from bigger ones if time and CPU isn't an issue". The only
test so far (EXP-33, K=32) found a 2x brain at .816 vs .790 for the default, within noise: capacity did not bind there.
Capacity can only bind in a bigger world, so this sweeps both.
World: teachers.network.run_network (EXP-33 peer network: 8 brains, founders know K/8 contexts each, random pairs teach
both ways with grading, M=16 steps per lesson). Arms: 'base' (no fix: stale teaching + forgetting, the EXP-33 plateau) and
'both' (notes + drift-check + rehearse). Brain sizes (Cadence modules): (16, 8) default, (32, 16), (64, 32). Worlds:
K = 32 and K = 96 contexts.
Read-outs per (arm, K, size): network knowledge before teaching (founder mastery), final, mean over time, forgetting
share per lesson; 12 seeds (SEM).
PREDICTION (2026-10-10, written before the pilot): at K=32 size changes nothing beyond noise in either arm (EXP-33).
At K=96 the default brain forgets more and plateaus lower in 'base'; (64, 32) lifts 'base' final knowledge by >= .05 and
cuts forgetting; under 'both' the size effect shrinks (stale teaching, not capacity, is the main limit).
REVISED PREDICTION (2026-10-10, after the 2-seed pilot, before the 12-seed run; the original above is scored as written
on all 12 seeds, this revision only on seeds 2-11, which the pilot did not run): (a) 'both', either K: no size effect,
|final(64x32) - final(16x8)| < .02 at K=32 and < .03 at K=96. (b) 'base', K=32: 64x32 beats 16x8 by >= .03 in final
knowledge and forgetting falls with size. (c) 'base', K=96: 64x32 beats 16x8 by .02 to .05. (d) size helps only where
stale teaching is unfixed: the 64x32 - 16x8 gain in 'base' exceeds the gain in 'both' at both K. An effect must clear
2 SEM (unpaired, over seeds). Full text: experiments/EXP-40.md.
"""
import json, os, sys, time
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

K_LIST = [int(k) for k in os.environ.get("KS", "32,96").split(",")]
SIZES = [tuple(int(x) for x in s.split("x")) for s in os.environ.get("SIZES", "16x8,32x16,64x32").split(",")]
ARMS = os.environ.get("ARMS", "base,both").split(",")
SEEDS = int(os.environ.get("SEEDS", 12))
ROUNDS = {32: int(os.environ.get("ROUNDS32", 16)), 96: int(os.environ.get("ROUNDS96", 24))}
TAG = os.environ.get("TAG", "full")


def job(args):
    arm, K, size, seed = args
    from teachers.lessons import RandomTeacher
    from teachers.network import run_network
    t0 = time.time()
    r = run_network(RandomTeacher(), seed=seed, rounds=ROUNDS.get(K, 16), arm=arm, K=K, modules=size)
    return dict(arm=arm, K=K, size="x".join(map(str, size)), seed=seed, before=r["acc"][0], final=r["final"],
                mean_over_time=r["mean_over_time"], forgetting=r["forgetting"], acc=r["acc"], cadence=r["cadence"],
                secs=round(time.time() - t0, 1))


def main():
    t0 = time.time()
    ckpt = os.path.join(HERE, f"EXP-40-{TAG}.jsonl")
    res = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["arm"], r["K"], r["size"], r["seed"]) for r in res}
    jobs = [(a, K, s, sd) for K in K_LIST for a in ARMS for s in SIZES for sd in range(SEEDS)
            if (a, K, "x".join(map(str, s)), sd) not in done]
    print(f"resuming: {len(done)} done, {len(jobs)} to run", flush=True)
    with get_context("spawn").Pool(int(os.environ.get("WORKERS", 3))) as pool:
        for r in pool.imap_unordered(job, jobs):
            res.append(r)
            with open(ckpt, "a") as f:
                f.write(json.dumps(r) + "\n")
    print(f"EXP-40 brain size x world size  seeds={SEEDS} rounds={ROUNDS}  ({time.time()-t0:.0f}s)")
    sem = lambda x: np.std(x, ddof=1) / len(x) ** .5 if len(x) > 1 else 0.0
    for K in K_LIST:
        for a in ARMS:
            for s in SIZES:
                rs = [r for r in res if r["K"] == K and r["arm"] == a and r["size"] == "x".join(map(str, s)) and r["seed"] < SEEDS]
                if not rs:
                    continue
                f = np.array([r["final"] for r in rs]); fg = np.array([r["forgetting"] for r in rs])
                print(f"  K={K:3d} {a:5s} size {'x'.join(map(str, s)):6s}  before {np.mean([r['before'] for r in rs]):.3f}"
                      f"  final {f.mean():.3f} (SEM {sem(f):.3f})  mean-over-time {np.mean([r['mean_over_time'] for r in rs]):.3f}"
                      f"  forgetting {fg.mean():.3f} (SEM {sem(fg):.3f})  ~{np.mean([r['secs'] for r in rs]):.0f}s/run  n={len(rs)}")
    json.dump(res, open(os.path.join(HERE, f"EXP-40-{TAG}.json"), "w"))


if __name__ == "__main__":
    main()
