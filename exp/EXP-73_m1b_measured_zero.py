"""
EXP-73: M1b on the content-taking brain with the zero declared by measured information.
EXP-62's harness unchanged (through EXP-62d's, as EXP-62e), lesson 80, 216 fresh students (seeds 8_200_000 + student).
Zero = per-student mean of {null, untaught, random}: the two random-label arms (labels right 1 time in 5 by
construction, checked on this run) and the arm with no labels. anti-echo stays a knowledge-free arm: it is not in the
zero, it counts as a fake for pay, and the weakest real teacher must beat it by 2 SEM.
PRE-REGISTRATION: experiments/EXP-73.md (written 2026-10-25, before any EXP-73 data).

    GATE=1 python -u EXP-73_m1b_measured_zero.py        # identity gate: EXP-62e student 0 on this version
    TAG=full WORKERS=4 python -u EXP-73_m1b_measured_zero.py
"""
import json, os, time

GATE = os.environ.get("GATE") == "1"
os.environ.setdefault("PREFIX", "EXP-73")
os.environ.setdefault("SEED_BASE", "6800000" if GATE else "8200000")
os.environ.setdefault("LENGTHS", "80")
os.environ.setdefault("STUDENTS", "216")
os.environ.setdefault("ARMS", "full")
__file__ = os.path.abspath(__file__)
_src = open(os.path.join(os.path.dirname(__file__), "EXP-62d_pooled_zero.py"), encoding="utf-8").read()
_src = _src.replace('if __name__ == "__main__":\n    main62d()', "")   # take 62d's harness + analysis, not its main
exec(compile(_src, "EXP-62d_pooled_zero.py", "exec"))

MARGIN = 1 / 32
ZERO = ["null", "untaught", "random"]           # measured-chance zero class
KNOWLEDGE_FREE = ["null", "untaught", "random", "anti-echo", "wrong-chain", "echo"]
NONSUP = ["null", "untaught", "random", "wrong-chain", "echo"]   # anti-echo reported, not in the margin test
UNINF[:] = ZERO                                  # analyse_pooled reads this global for Z and the know-1 separations


def label_info(rows, lesson, arm):
    """Pooled share of labels that name the right action, with a binomial 95% interval."""
    hits = n = 0
    for r in rows:
        if r["lesson"] == lesson and r["student"] < STUDENTS:
            for right, _, label in r["arms"][arm]["labels"]:
                hits += int(label == right)
                n += 1
    p = hits / n if n else float("nan")
    half = 1.96 * (p * (1 - p) / n) ** 0.5 if n else float("nan")
    return dict(rate=p, n=n, lo=p - half, hi=p + half)


def analyse73(rows, lesson):
    o = analyse_pooled(rows, lesson)             # Z = mean of ZERO (UNINF replaced above); worth for every arm
    rs = sorted((r for r in rows if r["lesson"] == lesson and r["student"] < STUDENTS), key=lambda r: r["student"])
    acc = {a: np.array([r["arms"][a]["acc"] for r in rs]) for a in ARMS62D}
    d = acc["know-1"] - acc["anti-echo"]
    o["know1_vs_anti_echo"] = dict(diff=float(d.mean()), sem=sem(d), z=float(d.mean() / sem(d)))
    o["upper"] = {a: o["arms"][a]["worth"] + 1.645 * o["arms"][a]["sem"] for a in NONSUP}
    o["label_info"] = {a: label_info(rows, lesson, a) for a in ("null", "random", "anti-echo")}
    o["fake_pay_share_all"] = float(sum(o["pay"][a] for a in KNOWLEDGE_FREE))   # o["pay"] is already a share of total pay
    zero_ok = all(o["label_info"][a]["lo"] <= 0.2 <= o["label_info"][a]["hi"] for a in ("null", "random"))
    o["criteria"] = dict(ordered_and_spearman=o["ordered"] and o["spearman_k"] >= 0.3 and o["n_spearman"] >= 864,
                         know4_ge_2=o["arms"]["know-4"]["worth"] >= 0.2,
                         nonsuperiority=all(u < MARGIN for u in o["upper"].values()),
                         know1_beats_zero_by_2sem=all(o["know1_sep"][a]["z"] >= 2 for a in ZERO),
                         know1_beats_anti_echo_by_2sem=o["know1_vs_anti_echo"]["z"] >= 2,
                         fake_pay_le_10=o["fake_pay_share_all"] <= 0.10)
    k2 = o["arms"]["know-2"]["worth"]
    o["kill"] = bool(any(o["arms"][a]["worth"] >= k2 for a in KNOWLEDGE_FREE))
    o["zero_admitted"] = zero_ok
    o["verdict"] = ("VOID (zero class failed its information check)" if not zero_ok else
                    "KILL" if o["kill"] else "CONFIRM" if all(o["criteria"].values()) else "BOUNDARY")
    return o


def gate():
    import cadence
    ref = [json.loads(l) for l in open(os.path.join(HERE, "EXP-62e-full.jsonl"))]
    ref = next(r for r in ref if r["student"] == 0 and r["lesson"] == 80)
    t0 = time.time()
    new = run((80, 0))
    same = {a: (new["arms"][a]["actions"] == ref["arms"][a]["actions"] and new["arms"][a]["labels"] == ref["arms"][a]["labels"])
            for a in ref["arms"]}
    print(f"identity gate on cadence {cadence.__version__}: seed {new['seed']} vs EXP-62e student 0 "
          f"({time.time() - t0:.0f}s): " + ("IDENTICAL" if all(same.values()) else f"DIFFERS {same}"), flush=True)


def main73():
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
    print(f"\n{PREFIX} [{TAG}] summary ({time.time() - t0:.0f}s); worth = arm - mean of {ZERO}, same student")
    summ = {}
    for L in LENGTHS:
        o = analyse73(rows, L)
        summ[str(L)] = o
        report_pooled(o)
        print("    upper bounds (worth + 1.645 SEM) vs margin 1/32: " + "  ".join(f"{a} {u:+.3f}" for a, u in o["upper"].items()))
        print(f"    anti-echo worth {o['arms']['anti-echo']['worth']:+.3f} (sem {o['arms']['anti-echo']['sem']:.3f}); "
              f"know-1 minus anti-echo {o['know1_vs_anti_echo']['diff']:+.3f} ({o['know1_vs_anti_echo']['z']:.1f} SEM)")
        print("    label information: " + "  ".join(f"{a} {v['rate']:.3f} [{v['lo']:.3f}, {v['hi']:.3f}] n={v['n']}"
                                                   for a, v in o["label_info"].items()))
        print(f"    fake pay share over all knowledge-free arms {o['fake_pay_share_all']:.3f}")
        print(f"    criteria {o['criteria']}  zero admitted {o['zero_admitted']}  kill {o['kill']}  -> {o['verdict']}")
    json.dump(dict(summary=summ, version=getattr(cadence, "__version__", "?")),
              open(os.path.join(HERE, f"{PREFIX}-{TAG}.json"), "w"))


if __name__ == "__main__":
    gate() if GATE else main73()
