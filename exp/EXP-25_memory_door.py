"""
EXP-25 — a skill that is genuinely hard to TEACH: the memory door.

Blind key-door (no pouch sense). Each trip the chest is present with p=0.5 (else a floor cell).
Interact at chest -> take key. Door: interact WITH key +1, WITHOUT key -COST. Lamp/levers: -COST.
A memoryless policy can score at most 0.5 (it cannot tell at the door whether a chest was seen).
Score = fraction of test trips handled perfectly (chest trips: key + door, no wrong presses;
no-chest trips: no door press, no wrong presses).

Step 1 (STEP=found): can founders learn it? end-to-end reward, F trips, P founders.
Step 2 (STEP=teach): do grading STRATEGIES differ (curriculum on corridor delay etc.)?
"""
import os, sys, json, time
import numpy as np
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cadence_src import KEYDOOR  # noqa: E402
sys.path.insert(0, KEYDOOR)
OUT = os.path.join(HERE, "exp25_brains")
STEP = os.environ.get("STEP", "found")
F = int(os.environ.get("F", 1000))
DELAY = int(os.environ.get("DELAY", 2))
TEST_TRIPS = 40
COST = 0.25


def env():
    import json as _j
    from key_door import make_brain, observe, FLOOR, CHEST, LAMP, DOOR, INTERACT
    proto = _j.load(open(os.path.join(KEYDOOR, "protocol-3.json")))
    return proto["operating_point"], make_brain, observe, FLOOR, CHEST, LAMP, DOOR, INTERACT


def trip_cells(rng, delay, chest):
    LEVER = 3
    from key_door import FLOOR, CHEST, LAMP, DOOR
    levers = max(0, delay + int(rng.integers(-1, 2))) if delay else 0
    floors = 3
    return [*([FLOOR] * floors), CHEST if chest else FLOOR, LAMP, *([LEVER] * levers), DOOR]


def outcome(cell, a, holding, consts):
    FLOOR, CHEST, DOOR, INTERACT = consts
    if a != INTERACT:
        return 0.0, holding, 0
    if cell == CHEST and not holding:
        return 0.0, True, 0
    if cell == DOOR:
        return (1.0, holding, 0) if holding else (-COST, holding, 1)
    if cell == FLOOR:
        return 0.0, holding, 0
    return -COST, holding, 1


def train_e2e(brain, trips, rng, delay, observe, consts):
    pending = None
    for _ in range(trips):
        chest = bool(rng.random() < .5)
        holding = False
        cells = trip_cells(rng, delay, chest)
        for i, cell in enumerate(cells):
            fb = {} if pending is None else {"reward": [pending[0]], "done": [pending[1]]}
            a = int(brain.step(observe(cell, holding, False), **fb)[0])
            r, holding, _ = outcome(cell, a, holding, consts)
            pending = (r, i == len(cells) - 1)
    brain.step(observe(consts[0], False, False), reward=[pending[0]], done=[pending[1]])


def test(path, seed, delay, observe, consts):
    import cadence as cd
    b = cd.Brain.load(path)
    rng = np.random.default_rng(99_000 + seed)
    good = 0
    detail = {"chest": [0, 0], "nochest": [0, 0]}
    for t in range(TEST_TRIPS):
        chest = t % 2 == 0
        holding, wrong, fed = False, 0, 0
        for cell in trip_cells(rng, delay, chest):
            a = int(b.act(observe(cell, holding, False), greedy=True)[0])
            r, holding, w = outcome(cell, a, holding, consts)
            wrong += w
            fed |= r > 0
        ok = (fed and wrong == 0) if chest else (wrong == 0)
        good += ok
        k = "chest" if chest else "nochest"
        detail[k][0] += ok; detail[k][1] += 1
        b.reset()
    return good / TEST_TRIPS, {k: v[0] / v[1] for k, v in detail.items()}


def founder_job(i):
    point, make_brain, observe, FLOOR, CHEST, LAMP, DOOR, INTERACT = env()
    consts = (FLOOR, CHEST, DOOR, INTERACT)
    b = make_brain(point, 90_000 + i, None, False)
    train_e2e(b, F, np.random.default_rng(6000 + i), DELAY, observe, consts)
    path = b.save(os.path.join(OUT, f"founder_{i}_F{F}_d{DELAY}.npz"))
    s, d = test(path, 90_000 + i, DELAY, observe, consts)
    return i, s, d


def main():
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    n = int(os.environ.get("P", 6))
    with get_context("spawn").Pool(int(os.environ.get("WORKERS", 6))) as pool:
        res = pool.map(founder_job, range(n))
    print(f"EXP-25 found  blind memory door  delay={DELAY}  F={F} trips  ({time.time()-t0:.0f}s)")
    for i, s, d in res:
        print(f"  founder {i}: score {s:.2f}  chest-trips {d['chest']:.2f}  no-chest-trips {d['nochest']:.2f}")
    print(f"  mean {np.mean([s for _, s, _ in res]):.2f}   (memoryless ceiling 0.50)")


if __name__ == "__main__":
    main()
