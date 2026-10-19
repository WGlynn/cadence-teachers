"""
EXP-62d: pooled zero with a noise allowance and a separation test.
EXP-62's harness unchanged (delayed-credit brain, weather chamber, corrective schedule, 20 attempts alone through `step`,
per-state greedy accuracy on unseen weather), lesson 80, 72 fresh students (seeds 6_600_000 + student). Only the
analysis is new: zero Z = per-student mean of the declared uninformative class {null, untaught, random, anti-echo}.
PRE-REGISTRATION: experiments/EXP-62d.md (written 2026-10-17, before any EXP-62d data).
Run gate (2026-10-19): the harness on 0.84.3 `8dc92d8` reproduced EXP-62c students 0-1 (6499e56) bit-identically,
actions and labels in all 10 arms (exp/GATE62-v0843-full.jsonl).

    TAG=full WORKERS=4 python -u EXP-62d_pooled_zero.py
"""
import json, os, time

os.environ.setdefault("PREFIX", "EXP-62d")
os.environ.setdefault("SEED_BASE", "6600000")
os.environ.setdefault("LENGTHS", "80")
os.environ.setdefault("STUDENTS", "72")
os.environ.setdefault("ARMS", "full")
__file__ = os.path.abspath(__file__)
_src = open(os.path.join(os.path.dirname(__file__), "EXP-62_content_market_committed_null.py"), encoding="utf-8").read()
_src = _src.replace('if __name__ == "__main__":\n    main()', "")   # take the harness, not its analysis
exec(compile(_src, "EXP-62_content_market_committed_null.py", "exec"))

import numpy as np
from multiprocessing import get_context

UNINF = ["null", "untaught", "random", "anti-echo"]          # declared uninformative class (the zero)
MISLEAD = ["wrong-chain", "echo"]
ARMS62D = KNOW + UNINF + MISLEAD


def analyse_pooled(rows, lesson):
    rs = sorted((r for r in rows if r["lesson"] == lesson and r["student"] < STUDENTS), key=lambda r: r["student"])
    acc = {a: np.array([r["arms"][a]["acc"] for r in rs]) for a in ARMS62D}
    Z = np.mean([acc[a] for a in UNINF], axis=0)
    worth = {a: acc[a] - Z for a in ARMS62D}
    o = dict(lesson=lesson, n=len(rs), zero=float(Z.mean()), arms={})
    for a in ARMS62D:
        o["arms"][a] = dict(acc=float(acc[a].mean()), worth=float(worth[a].mean()), sem=sem(worth[a]))
    kv = np.array([int(t.split("-")[1]) for t in KNOW for _ in rs], float)
    o["spearman_k"] = spearman(kv, np.concatenate([worth[t] for t in KNOW]))
    o["n_spearman"] = len(kv)
    means = [o["arms"][t]["worth"] for t in KNOW]
    o["ordered"] = bool(all(means[i] < means[i + 1] for i in range(3)))
    sep = {}
    for a in UNINF:
        d = acc["know-1"] - acc[a]
        sep[a] = dict(diff=float(d.mean()), sem=sem(d), z=float(d.mean() / sem(d)) if sem(d) > 0 else float("inf"))
    o["know1_sep"] = sep
    pay = {}
    for a in ARMS62D:
        p = 0.0
        for i in range(0, len(rs) - BATCH + 1, BATCH):
            w = worth[a][i:i + BATCH]
            m, se = float(w.mean()), sem(w)
            if m > 0 and se > 0 and m / se > 2:
                p += m
        pay[a] = p
    total = sum(pay.values()) or 1.0
    o["pay"] = {a: pay[a] / total for a in ARMS62D}
    o["fake_pay_share"] = float(sum(pay[a] for a in UNINF + MISLEAD) / total)
    fakes = UNINF + MISLEAD
    crit = dict(
        ordered_and_spearman=o["ordered"] and o["spearman_k"] >= 0.3 and o["n_spearman"] >= 288,
        know4_ge_2=o["arms"]["know-4"]["worth"] >= 0.2,
        no_fake_above_0_by_2sem=all(not (o["arms"][a]["worth"] > 2 * o["arms"][a]["sem"]) for a in fakes),
        know1_beats_uninf_by_2sem=all(sep[a]["z"] >= 2 for a in UNINF),
        fake_pay_le_10=o["fake_pay_share"] <= 0.10)
    o["criteria"] = crit
    k2 = o["arms"]["know-2"]["worth"]
    o["kill"] = bool(any(o["arms"][a]["worth"] >= k2 for a in fakes))
    o["verdict"] = "KILL" if o["kill"] else "CONFIRM" if all(crit.values()) else "BOUNDARY"
    return o


def report_pooled(o):
    print(f"\n  lesson {o['lesson']}: n={o['n']}  zero = mean of {UNINF} = {o['zero']:.3f}")
    print(f"    {'arm':12s} {'acc':>6s} {'worth':>7s} {'sem':>6s} {'w/sem':>6s} {'pay':>6s}")
    for a, v in o["arms"].items():
        r = v["worth"] / v["sem"] if v["sem"] > 0 else float("nan")
        print(f"    {a:12s} {v['acc']:6.3f} {v['worth']:+7.3f} {v['sem']:6.3f} {r:+6.2f} {o['pay'][a]:6.3f}")
    print("    know-1 minus uninformative arm (paired): "
          + "  ".join(f"{a} {s['diff']:+.3f} ({s['z']:.2f} SEM)" for a, s in o["know1_sep"].items()))
    print(f"    Spearman(worth, k) = {o['spearman_k']:.3f} (n={o['n_spearman']})  ordered={o['ordered']}  "
          f"fake pay share = {o['fake_pay_share']:.3f}")
    print(f"    criteria: {o['criteria']}  kill={o['kill']}  -> {o['verdict']}")


def main62d():
    import cadence
    t0 = time.time()
    ckpt = os.path.join(HERE, f"{PREFIX}-{TAG}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["lesson"], r["student"]) for r in rows}
    jobs = [(L, k) for k in range(STUDENTS) for L in LENGTHS if (L, k) not in done]
    print(f"{PREFIX} [{TAG}]: cadence {getattr(cadence, '__version__', '?')} at {os.path.dirname(cadence.__file__)}; "
          f"{len(jobs)} students to go ({len(done)} done); seeds {SEED_BASE}+; lengths {LENGTHS}", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as fh:
                    fh.write(json.dumps(r) + "\n")
    print(f"\n{PREFIX} [{TAG}] summary ({time.time() - t0:.0f}s); worth = arm - pooled uninformative zero, same student")
    summ = {}
    for L in LENGTHS:
        o = analyse_pooled(rows, L)
        summ[str(L)] = o
        report_pooled(o)
    json.dump(dict(summary=summ, version=getattr(cadence, "__version__", "?")),
              open(os.path.join(HERE, f"{PREFIX}-{TAG}.json"), "w"))


if __name__ == "__main__":
    main62d()
