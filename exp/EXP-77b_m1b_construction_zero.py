"""
EXP-77b: re-cross M1b on Cadence 0.89.0 with the zero admitted by construction.
EXP-77 exactly (EXP-73's harness, lesson 80, zero = mean of {null, untaught, random}, the six CONFIRM criteria, KILL),
on fresh seeds (9_000_000 + student). One rule changes, disclosed before data: the zero is admitted by
EXP-77b_construction_audit.py (code, blindness, 10^6-label seeded draw), run before the pilot; the per-run binomial
interval of EXP-73/77 is still computed and reported, not decisive.
PRE-REGISTRATION: experiments/EXP-77b.md (written 2026-10-27, before any EXP-77b data). Port gate on 0.89.0 with
LATERAL=-0.5: IDENTICAL (exp/EXP-77b-gate-81345d8.out).

    python -u EXP-77b_construction_audit.py > EXP-77b-audit.out
    TAG=pilot STUDENTS=6 SEED_BASE=8990000 WORKERS=4 python -u EXP-77b_m1b_construction_zero.py
    TAG=full WORKERS=4 python -u EXP-77b_m1b_construction_zero.py
"""
import os

if os.environ.get("LATERAL"):
    raise SystemExit("EXP-77b reads the founder lateral: unset LATERAL (it is only for the port gate)")
os.environ.setdefault("PREFIX", "EXP-77b")
os.environ.setdefault("SEED_BASE", "9000000")
__file__ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "EXP-73_m1b_measured_zero.py")
_src = open(__file__, encoding="utf-8").read()
_src = _src.replace('if __name__ == "__main__":\n    gate() if GATE else main73()', "")
exec(compile(_src, "EXP-73_m1b_measured_zero.py", "exec"))

_AUDIT = os.path.join(os.path.dirname(__file__), "EXP-77b-audit.out")
_analyse73 = analyse73


def analyse73(rows, lesson):          # main73 looks this name up at call time
    o = _analyse73(rows, lesson)
    o["zero_admitted_old_check"] = o["zero_admitted"]          # EXP-73/77's interval, reported only
    audit = open(_AUDIT, encoding="utf-8").read() if os.path.exists(_AUDIT) else ""
    o["zero_admitted"] = "ADMITTED BY CONSTRUCTION" in audit
    o["verdict"] = ("VOID (construction audit missing or failed)" if not o["zero_admitted"] else
                    "KILL" if o["kill"] else "CONFIRM" if all(o["criteria"].values()) else "BOUNDARY")
    print(f"    old interval check (reported, not decisive): {'admitted' if o['zero_admitted_old_check'] else 'not admitted'}")
    return o


if __name__ == "__main__":
    main73()
