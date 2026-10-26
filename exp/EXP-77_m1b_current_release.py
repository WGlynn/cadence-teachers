"""
EXP-77: re-cross M1b on a current Cadence release (0.88.1), founder lateral.
EXP-73 exactly (EXP-62's harness, lesson 80, zero = mean of {null, untaught, random}, the same decision rules), on
the ported composition: 0.85+ names `working_memory_scale` as `scales={'trace': ...}` (EXP-58's compose takes either).
Port gate (done before the pre-registration): on 0.88.1 with LATERAL=-0.5 the EXP-73 identity gate is IDENTICAL.
This run leaves `lateral` unset, so it reads 0.88.1's founder (0.0; 0.84.3's unset lateral was -0.5, upstream #220).
PRE-REGISTRATION: experiments/EXP-77.md (written 2026-10-26, before any EXP-77 data).

    LATERAL=-0.5 GATE=1 python -u EXP-73_m1b_measured_zero.py      # port gate (already IDENTICAL on 0.88.1)
    TAG=pilot STUDENTS=6 SEED_BASE=8390000 WORKERS=4 python -u EXP-77_m1b_current_release.py
    TAG=full WORKERS=4 python -u EXP-77_m1b_current_release.py      # LENGTHS per the pilot rule in EXP-77.md
"""
import os

if os.environ.get("LATERAL"):
    raise SystemExit("EXP-77 reads the founder lateral: unset LATERAL (it is only for the port gate)")
os.environ.setdefault("PREFIX", "EXP-77")
os.environ.setdefault("SEED_BASE", "8400000")
__file__ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "EXP-73_m1b_measured_zero.py")
_src = open(__file__, encoding="utf-8").read()
_src = _src.replace('if __name__ == "__main__":\n    gate() if GATE else main73()', "")
exec(compile(_src, "EXP-73_m1b_measured_zero.py", "exec"))

if __name__ == "__main__":
    main73()
