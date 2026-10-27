"""
EXP-77b admission by construction: is the zero class's label source uniform over the five actions and blind to the
right answer, by its code and by a large seeded draw, outside any run?
Replaces EXP-73/77's per-run binomial interval (which false-fails about 10% of runs, EXP-77) as the VOID gate.
PRE-REGISTRATION: experiments/EXP-77b.md. Deterministic; prints PASS or FAIL per check and an overall line.

    python -u EXP-77b_construction_audit.py
"""
import inspect, os, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_src = open(os.path.join(HERE, "EXP-62_content_market_committed_null.py"), encoding="utf-8").read()
_src = _src.split('\nif __name__ == "__main__":')[0]
ns = {"__file__": os.path.join(HERE, "EXP-62_content_market_committed_null.py"), "__name__": "exp62"}
exec(compile(_src, "EXP-62_content_market_committed_null.py", "exec"), ns)
labeller, E52 = ns["labeller"], ns["E52"]

N = 1_000_000
TOL = 0.002          # 5 SE at n = 10^6 for a share near .2
checks = {}

# 1. code: the entry point both zero-class labelled arms use routes "random" to E52, whose branch draws rng.integers(5)
src62 = inspect.getsource(labeller)
src52 = inspect.getsource(E52.labeller)
checks["code_route"] = 'if kind == "anti-echo"' in src62 and "return E52.labeller(kind, rng)" in src62
checks["code_branch"] = 'if kind == "random":\n        return lambda c, a: int(rng.integers(5))' in src52


# 2. blindness: the label is produced without reading the chamber or the action at all
class Untouchable:
    def right(self):
        raise RuntimeError("label read the right answer")

    def __int__(self):
        raise RuntimeError("label read the action")

    def __index__(self):
        raise RuntimeError("label read the action")


lab = labeller("random", np.random.default_rng(77_000_001))
try:
    out = [lab(Untouchable(), Untouchable()) for _ in range(1000)]
    checks["blind"] = all(isinstance(t, int) and 0 <= t < 5 for t in out)
except RuntimeError as e:
    print("blindness:", e)
    checks["blind"] = False


# 3. seeded draw of 10^6 labels: each action's share and the hit rate against a seeded right-answer stream
class Fixed:
    def __init__(self, r):
        self.r = r

    def right(self):
        return self.r


lab = labeller("random", np.random.default_rng(77_000_002))
rights = np.random.default_rng(77_000_003).integers(4, size=N)
labels = np.fromiter((lab(Fixed(int(r)), 0) for r in rights), dtype=np.int64, count=N)
shares = np.bincount(labels, minlength=5) / N
hit = float((labels == rights).mean())
hit_by_right = [float((labels[rights == r] == r).mean()) for r in range(4)]
checks["shares"] = bool(np.all(np.abs(shares - 0.2) <= TOL))
checks["hit_rate"] = abs(hit - 0.2) <= TOL
checks["hit_by_right"] = all(abs(h - 0.2) <= 2 * TOL for h in hit_by_right)   # n ~ 250k each, 2*TOL = 5 SE

print(f"shares by action {np.round(shares, 4).tolist()}  hit {hit:.4f}  hit by right {[round(h, 4) for h in hit_by_right]}")
for k, v in checks.items():
    print(f"  {k:14s} {'PASS' if v else 'FAIL'}")
print("ADMITTED BY CONSTRUCTION" if all(checks.values()) else "NOT ADMITTED: EXP-77b is VOID before any run")
