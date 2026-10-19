"""
EXP-62e: a non-superiority margin for the fakes, powered for the class.
EXP-62's harness unchanged, lesson 80, 216 fresh students (seeds 6_800_000 + student), zero = per-student mean of the
uninformative class {null, untaught, random, anti-echo} (EXP-62d's analysis), plus the decisive margin rule: every
fake's mean worth + 1.645 SEM < 1/32 (half of one of the 16 states accuracy is read on).
PRE-REGISTRATION: experiments/EXP-62e.md (written 2026-10-19, before any EXP-62e data).
Before the run, identity-gate one EXP-62d student on the current version (actions + labels bit-identical).

    TAG=full WORKERS=4 python -u EXP-62e_margin_zero.py
"""
import json, os, time

os.environ.setdefault("PREFIX", "EXP-62e")
os.environ.setdefault("SEED_BASE", "6800000")
os.environ.setdefault("LENGTHS", "80")
os.environ.setdefault("STUDENTS", "216")
os.environ.setdefault("ARMS", "full")
__file__ = os.path.abspath(__file__)
_src = open(os.path.join(os.path.dirname(__file__), "EXP-62d_pooled_zero.py"), encoding="utf-8").read()
_src = _src.replace('if __name__ == "__main__":\n    main62d()', "")   # take 62d's harness + analysis, not its main
exec(compile(_src, "EXP-62d_pooled_zero.py", "exec"))

MARGIN = 1 / 32


def analyse_margin(rows, lesson):
    o = analyse_pooled(rows, lesson)
    fakes = UNINF + MISLEAD
    o["margin"] = MARGIN
    o["upper"] = {a: o["arms"][a]["worth"] + 1.645 * o["arms"][a]["sem"] for a in fakes}
    c = o["criteria"]
    o["criteria_62d"] = dict(c)                                    # reported, not decisive
    o["criteria"] = dict(ordered_and_spearman=c["ordered_and_spearman"] and o["n_spearman"] >= 864,
                         know4_ge_2=c["know4_ge_2"],
                         nonsuperiority=all(u < MARGIN for u in o["upper"].values()),
                         know1_beats_uninf_by_2sem=c["know1_beats_uninf_by_2sem"],
                         fake_pay_le_10=c["fake_pay_le_10"])
    o["verdict"] = "KILL" if o["kill"] else "CONFIRM" if all(o["criteria"].values()) else "BOUNDARY"
    return o


def main62e():
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
        o = analyse_margin(rows, L)
        summ[str(L)] = o
        report_pooled(o)
        print("    upper bounds (worth + 1.645 SEM) vs margin 1/32 = .03125: "
              + "  ".join(f"{a} {u:+.3f}" for a, u in o["upper"].items()))
        print(f"    EXP-62d 2-SEM criteria on the same data (not decisive): {o['criteria_62d']}")
    json.dump(dict(summary=summ, version=getattr(cadence, "__version__", "?")),
              open(os.path.join(HERE, f"{PREFIX}-{TAG}.json"), "w"))


if __name__ == "__main__":
    main62e()
