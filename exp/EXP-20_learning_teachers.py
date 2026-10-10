"""
EXP-20 — closing the loop: TEACHERS that learn from their own Shapley credit.

EXP-19 scored hand-written teachers. Here each teacher is itself a Cadence brain choosing which
lesson to give, and its only reward is the Shapley credit its lesson earns in a student.

Round r:
  1. teacher T1, T2 (Brain.compose, 1 constant input, |MENU| actions) each pick a lesson type.
  2. a fresh student founder (seed varies by round) is taught by each coalition {}, {T1}, {T2},
     {T1,T2} (missing slots = null trips; same corridors; interleaved), via EXP-19's `teach`.
  3. each student is tested on the full key-door task (EXP-19 `test_fed`: clean trips).
  4. v(S) = score(S) - score({}); Shapley phi_1, phi_2 (2 players).
  5. each teacher gets reward = phi_i (scaled), delivered with its next decision via `step`.

Menu: null, key (A), door (B), lamp (F, wrong object), spam (rewards any interaction).
Prediction if the loop works: teachers converge on complementary {key, door} and never on spam.
Honest risk: coordination game with 2 pure equilibria + noisy credit; may not converge in R rounds.
"""
import os, sys, time, json
import numpy as np
import cadence as cd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location("e19", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              "EXP-19_keydoor_teamwork.py"))
e19 = importlib.util.module_from_spec(spec); spec.loader.exec_module(e19)
from key_door import corridor, observe, INTERACT, FLOOR, CHEST, LAMP, DOOR  # noqa

MENU = ["0", "A", "B", "F", "S"]          # null, key, door, lamp, spam
NAMES = {"0": "null", "A": "key", "B": "door", "F": "lamp", "S": "spam"}
N = int(os.environ.get("N", 100))
ROUNDS = int(os.environ.get("ROUNDS", 40))
RUN = int(sys.argv[1]) if len(sys.argv) > 1 else 0
REWARD_SCALE = 2.0


def teach(brain, kinds, rng):
    """EXP-19 teach + the spam lesson ('S': +1 for any non-floor interaction, starts empty)."""
    pending = None
    for kind in kinds:
        cells = corridor(e19.DELAY, e19.LENGTH, e19.JITTER, rng)
        holding = kind == "B"
        for i, cell in enumerate(cells):
            fb = {} if pending is None else {"reward": [pending[0]], "done": [pending[1]]}
            a = int(brain.step(observe(cell, holding, True), **fb)[0])
            out = 0.0
            if a == INTERACT and kind != "0":
                if kind == "S":
                    if cell == CHEST and not holding:
                        holding = True
                    out = 1.0 if cell != FLOOR else 0.0
                elif cell == CHEST and not holding:
                    holding = True
                    out = 1.0 if kind == "A" else (-e19.COST if kind == "F" else 0.0)
                elif cell == LAMP and kind == "F":
                    out = 1.0
                elif cell == DOOR:
                    out = 1.0 if (kind == "B" and holding) else 0.0
                elif cell != FLOOR:
                    out = -e19.COST
            pending = (out, i == len(cells) - 1)
    if pending is not None:
        brain.step(observe(FLOOR, False, True), reward=[pending[0]], done=[pending[1]])


def student_score(kinds, sseed):
    b = e19.make_brain(e19.POINT, sseed, None, True)
    teach(b, kinds, np.random.default_rng(2000 + sseed))
    path = b.save(os.path.join(e19.TMP, f"e20_{RUN}_{sseed}_{abs(hash(''.join(kinds)))%10**8}.npz"))
    return e19.test_fed(path, sseed)


def main():
    t1 = cd.Brain.compose(1, len(MENU), modules=(16,), seed=500 + 2 * RUN)
    t2 = cd.Brain.compose(1, len(MENU), modules=(16,), seed=501 + 2 * RUN)
    x = np.ones((1, 1))
    r1 = r2 = None
    log = []
    t0 = time.time()
    for rnd in range(ROUNDS):
        fb1 = {} if r1 is None else {"reward": [r1], "done": [True]}
        fb2 = {} if r2 is None else {"reward": [r2], "done": [True]}
        c1 = MENU[int(t1.step(x, **fb1)[0])]
        c2 = MENU[int(t2.step(x, **fb2)[0])]
        sseed = 10_000 * (RUN + 1) + rnd
        s = {k: student_score(e19.interleave(a * N, b * N), sseed)
             for k, (a, b) in {"0": ("0", "0"), "1": (c1, "0"), "2": ("0", c2), "12": (c1, c2)}.items()}
        v1, v2, v12 = s["1"] - s["0"], s["2"] - s["0"], s["12"] - s["0"]
        phi1 = 0.5 * v1 + 0.5 * (v12 - v2)
        phi2 = 0.5 * v2 + 0.5 * (v12 - v1)
        r1, r2 = REWARD_SCALE * phi1, REWARD_SCALE * phi2
        log.append(dict(round=rnd, t1=NAMES[c1], t2=NAMES[c2], v12=v12, phi1=phi1, phi2=phi2, base=s["0"]))
        print(f"run {RUN} round {rnd:2d}  T1 {NAMES[c1]:5s} T2 {NAMES[c2]:5s}  base {s['0']:.2f}  "
              f"v12 {v12:+.2f}  phi {phi1:+.2f}/{phi2:+.2f}   ({time.time()-t0:.0f}s)", flush=True)
    t1.step(x, reward=[r1], done=[True]); t2.step(x, reward=[r2], done=[True])
    # greedy end policy of each teacher
    end = (NAMES[MENU[int(t1.act(x, greedy=True)[0])]], NAMES[MENU[int(t2.act(x, greedy=True)[0])]])
    print(f"run {RUN} END greedy teachers: T1 {end[0]}  T2 {end[1]}")
    last = log[-10:]
    pairs = {}
    for e in last:
        k = "/".join(sorted((e["t1"], e["t2"])))
        pairs[k] = pairs.get(k, 0) + 1
    print(f"run {RUN} last-10 lesson pairs: {pairs}")
    json.dump(dict(run=RUN, N=N, rounds=ROUNDS, end=end, log=log),
              open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"EXP-20-run{RUN}.json"), "w"))


if __name__ == "__main__":
    main()
