"""
EXP-19 — teamwork credit (M2-SYNERGY) on Cadence's own key-door world, learned composition.

EXP-18 put the synergy in the data. Here the student has to COMPOSE two learned skills itself.
World = benchmarks/keydoor (corridor: floor.., chest, lamp, D levers, door; pouch sense = holding),
brain = protocol-3 operating point (Brain.compose modules=(32,), trace, consolidation, actor genes).
Teaching uses `step` (learns every outcome; AGENTS.md: "use step for explicit teaching").

Teachers (each = N teaching trips on the real corridor, real wrong-interaction cost):
  A  key teacher   : starts empty-handed; +1 for taking the key at the chest; door pays 0.
  B  door teacher  : starts HOLDING the key; +1 for opening the door.
  F  fake key      : starts empty-handed; +1 for interacting with the LAMP (wrong object).
  0  null trips    : starts empty-handed; every outcome 0 (experience without information).
Every coalition sees exactly 2N trips (missing teacher slots are filled with null trips),
interleaved trip by trip so order effects are shared.

Test (held-out, exogenous): the FULL task, 30 greedy trips on a loaded copy, no learning:
score = fed with ZERO wrong interactions (iter13 fix: fed-only let interact-everything pass). Neither A nor B alone teaches the chain.

v(S) = fed(S) - fed(null-only twin). Credits: solo, leave-one-out, Shapley (2 players).
"""
import json, os, sys, tempfile, time, warnings
import numpy as np
import cadence as cd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cadence_src import KEYDOOR  # noqa: E402
sys.path.insert(0, KEYDOOR)
from key_door import corridor, observe, make_brain, PASS, INTERACT, FLOOR, CHEST, LAMP, DOOR  # noqa

warnings.simplefilter("ignore")
PROTO = json.load(open(os.path.join(KEYDOOR, "protocol-3.json")))
POINT = PROTO["operating_point"]
COST, LENGTH, JITTER = float(PROTO["cost"]), int(PROTO["length"]), int(PROTO["jitter"])
DELAY = 2
N = int(os.environ.get("N", 300))
TEST_TRIPS = 30
SEED0 = int(os.environ.get("SEED0", 0))
SEEDS = range(SEED0, SEED0 + (int(sys.argv[1]) if len(sys.argv) > 1 else 8))
TMP = tempfile.mkdtemp(prefix="exp19_")


def teach(brain, kinds, rng):
    """Live the given sequence of trip kinds ('A','B','F','0') with `step`."""
    pending = None
    for kind in kinds:
        cells = corridor(DELAY, LENGTH, JITTER, rng)
        holding = kind == "B"
        for i, cell in enumerate(cells):
            fb = {} if pending is None else {"reward": [pending[0]], "done": [pending[1]]}
            a = int(brain.step(observe(cell, holding, True), **fb)[0])
            out = 0.0
            if a == INTERACT and kind != "0":
                if cell == CHEST and not holding:
                    holding = True
                    out = 1.0 if kind == "A" else (-COST if kind == "F" else 0.0)
                elif cell == LAMP and kind == "F":
                    out = 1.0
                elif cell == DOOR:
                    out = 1.0 if (kind == "B" and holding) else 0.0
                elif cell != FLOOR:
                    out = -COST
            pending = (out, i == len(cells) - 1)
    if pending is not None:  # deliver the last outcome
        brain.step(observe(FLOOR, False, True), reward=[pending[0]], done=[pending[1]])


def test_fed(path, seed):
    """Full task, greedy, no learning, on a fresh loaded copy. Returns fraction of trips fed."""
    b = cd.Brain.load(path)
    rng = np.random.default_rng(99_000 + seed)
    clean = 0
    for _ in range(TEST_TRIPS):
        holding, got, wrong = False, 0, 0
        for cell in corridor(DELAY, LENGTH, JITTER, rng):
            a = int(b.act(observe(cell, holding, True), greedy=True)[0])
            if a == INTERACT:
                if cell == CHEST and not holding:
                    holding = True
                elif cell == DOOR and holding:
                    got = 1
                elif cell != FLOOR:
                    wrong += 1
        clean += int(got and wrong == 0)   # fed with zero wasted presses (no spam-everything pass)
        b.reset()
    return clean / TEST_TRIPS


def interleave(x, y):
    out = []
    for p, q in zip(x, y):
        out += [p, q]
    return out


COALITIONS = {
    "null": interleave("0" * N, "0" * N),
    "A":    interleave("A" * N, "0" * N),
    "B":    interleave("0" * N, "B" * N),
    "AB":   interleave("A" * N, "B" * N),
    "F":    interleave("F" * N, "0" * N),
    "FB":   interleave("F" * N, "B" * N),
}


def run_seed(seed):
    out = {}
    for name, kinds in COALITIONS.items():
        brain = make_brain(POINT, seed, None, True)          # identical founder per seed (twins)
        teach(brain, kinds, np.random.default_rng(2000 + seed))  # identical corridors per seed
        path = brain.save(os.path.join(TMP, f"{name}_{seed}.npz"))
        out[name] = test_fed(path, seed)
    return out


def main():
    t0 = time.time()
    rows = []
    for s in SEEDS:
        r = run_seed(s)
        rows.append(r)
        print(f"seed {s}  " + "  ".join(f"{k} {v:.2f}" for k, v in r.items())
              + f"   ({time.time()-t0:.0f}s)", flush=True)
    n = len(rows)
    v = {k: np.array([r[k] - r["null"] for r in rows]) for k in COALITIONS}
    m = {k: v[k].mean() for k in v}
    se = {k: v[k].std(ddof=1) / n ** .5 for k in v}
    print("-" * 72)
    print(f"EXP-19 keydoor teamwork  delay={DELAY} N={N} trips/teacher  test={TEST_TRIPS}  seeds={n}")
    print(f"  null-twin fed (raw) {np.mean([r['null'] for r in rows]):.3f}")
    for k in ("A", "B", "AB", "F", "FB"):
        print(f"  v({k:2s}) = {m[k]:+.3f}  (SEM {se[k]:.3f})")
    syn = v["AB"] - v["A"] - v["B"]
    print(f"  synergy v(AB)-v(A)-v(B) = {syn.mean():+.3f} (SEM {syn.std(ddof=1)/n**.5:.3f})")
    for label, a, b, ab in (("genuine", "A", "B", "AB"), ("fake key", "F", "B", "FB")):
        print(f"credits ({label}):")
        print(f"  solo   key {m[a]:+.3f}  door {m[b]:+.3f}")
        print(f"  LOO    key {m[ab]-m[b]:+.3f}  door {m[ab]-m[a]:+.3f}  sum {2*m[ab]-m[a]-m[b]:+.3f}")
        print(f"  shap   key {.5*m[a]+.5*(m[ab]-m[b]):+.3f}  door {.5*m[b]+.5*(m[ab]-m[a]):+.3f}"
              f"  sum {m[ab]:+.3f}")


if __name__ == "__main__":
    main()
