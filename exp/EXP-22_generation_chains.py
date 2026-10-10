"""
EXP-22 — generations: does key-door skill pass down brain-to-brain, and does DOING != TEACHING?

Gen 0 (founder) is trained one of two ways on the real key-door corridor (protocol-3 point):
  route L : key + door lessons, N=300 each, interleaved (EXP-19/21 recipe)
  route E : end-to-end, 600 full-task trips, +1 only for opening the door holding the key
Gen g+1 is a FRESH brain taught ONLY by gen g: the child walks M corridor trips choosing its own
actions (`step`, so it explores), and at every cell the parent labels the child's current
observation with the parent's own greedy action (`step(obs, teacher=[label])`). No rewards.

Per generation we record:
  do     : clean full-task score (EXP-19 test_fed: fed with zero wrong presses, 30 greedy trips)
  on     : parent-label correctness on the ON-PATH states a solver visits
  off    : correctness on OFF-PATH states a solver never visits but an exploring child does
           (holding at chest, holding at lamp/levers, empty at levers ...)
Ideal policy: interact at chest when empty, interact at door when holding, pass at lamp/levers,
pass at chest when holding. Floor and empty-door are free (no cost either way) and not scored.

Usage: SEED0=s python EXP-22_generation_chains.py <count>   (each seed runs route L and route E)
"""
import os, sys, json, time, importlib.util
import numpy as np
import cadence as cd

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("e20", os.path.join(HERE, "EXP-20_learning_teachers.py"))
e20 = importlib.util.module_from_spec(spec); spec.loader.exec_module(e20)
e19 = e20.e19
from key_door import corridor, observe, INTERACT, PASS, FLOOR, CHEST, LAMP, DOOR  # noqa
LEVER = 3

GENS = int(os.environ.get("GENS", 4))
M = int(os.environ.get("M", 300))
SEED0 = int(os.environ.get("SEED0", 0))
COUNT = int(sys.argv[1]) if len(sys.argv) > 1 else 1
TMP = e19.TMP

IDEAL = {(CHEST, False): INTERACT, (DOOR, True): INTERACT,
         (LAMP, False): PASS, (LEVER, False): PASS,
         (LAMP, True): PASS, (LEVER, True): PASS, (CHEST, True): PASS}
# a solver takes the key at the chest, so it meets lamp and levers HOLDING; empty lamp/levers and
# holding-at-chest are states only a mistaken / exploring brain reaches.
ON = [(CHEST, False), (LAMP, True), (LEVER, True), (DOOR, True)]
OFF = [(LAMP, False), (LEVER, False), (CHEST, True)]


def train_end_to_end(brain, trips, rng):
    pending = None
    for _ in range(trips):
        cells = corridor(e19.DELAY, e19.LENGTH, e19.JITTER, rng)
        holding = False
        for i, cell in enumerate(cells):
            fb = {} if pending is None else {"reward": [pending[0]], "done": [pending[1]]}
            a = int(brain.step(observe(cell, holding, True), **fb)[0])
            out = 0.0
            if a == INTERACT:
                if cell == CHEST and not holding:
                    holding = True
                elif cell == DOOR:
                    out = 1.0 if holding else 0.0
                elif cell != FLOOR:
                    out = -e19.COST
            pending = (out, i == len(cells) - 1)
    brain.step(observe(FLOOR, False, True), reward=[pending[0]], done=[pending[1]])


def labels(path):
    """Greedy action of a saved brain on every scored state (fresh copy, reset per probe)."""
    b = cd.Brain.load(path)
    out = {}
    for s in ON + OFF:
        b.reset()
        out[s] = int(b.act(observe(s[0], s[1], True), greedy=True)[0])
    return out


def teach_by_labels(child, parent_path, trips, rng):
    parent = cd.Brain.load(parent_path)
    for _ in range(trips):
        holding = False
        parent.reset()
        for cell in corridor(e19.DELAY, e19.LENGTH, e19.JITTER, rng):
            x = observe(cell, holding, True)
            lab = int(parent.act(x, greedy=True)[0])
            a = int(child.step(x, teacher=np.array([lab]))[0])
            if a == INTERACT and cell == CHEST and not holding:
                holding = True


def teach_by_grading(child, parent_path, trips, rng):
    """Parent GRADES the child's own moves: +1 when the child's action matches what the parent
    would do in that observation, -COST when it does not. Reward-only, so it reaches the actor
    (the label route did not: EXP-22 run 1). No task script: the parent brain is the only judge."""
    parent = cd.Brain.load(parent_path)
    pending = None
    for _ in range(trips):
        holding = False
        parent.reset()
        cells = corridor(e19.DELAY, e19.LENGTH, e19.JITTER, rng)
        for i, cell in enumerate(cells):
            x = observe(cell, holding, True)
            lab = int(parent.act(x, greedy=True)[0])
            fb = {} if pending is None else {"reward": [pending[0]], "done": [pending[1]]}
            a = int(child.step(x, **fb)[0])
            pending = (1.0 if a == lab else -e19.COST, i == len(cells) - 1)
            if a == INTERACT and cell == CHEST and not holding:
                holding = True
    child.step(observe(FLOOR, False, True), reward=[pending[0]], done=[pending[1]])


TEACH = teach_by_grading if os.environ.get("MODE", "grade") == "grade" else teach_by_labels


def record(path, sseed, gen):
    lab = labels(path)
    on = np.mean([lab[s] == IDEAL[s] for s in ON])
    off = np.mean([lab[s] == IDEAL[s] for s in OFF])
    return dict(gen=gen, do=e19.test_fed(path, sseed), on=float(on), off=float(off),
                labels={f"{k[0]}{int(k[1])}": v for k, v in lab.items()})


def chain(route, seed):
    rows = []
    f = e19.make_brain(e19.POINT, 60_000 + seed, None, True)
    rng = np.random.default_rng(3000 + seed)
    if route == "L":
        e20.teach(f, e19.interleave("A" * 300, "B" * 300), rng)
    else:
        train_end_to_end(f, 600, rng)
    path = f.save(os.path.join(TMP, f"e22_{route}_{seed}_g0.npz"))
    rows.append(record(path, 60_000 + seed, 0))
    for g in range(1, GENS + 1):
        child = e19.make_brain(e19.POINT, 70_000 + 100 * seed + g, None, True)
        TEACH(child, path, M, np.random.default_rng(4000 + 100 * seed + g))
        path = child.save(os.path.join(TMP, f"e22_{route}_{seed}_g{g}.npz"))
        rows.append(record(path, 70_000 + 100 * seed + g, g))
    return rows


def main():
    out = {}
    t0 = time.time()
    for seed in range(SEED0, SEED0 + COUNT):
        for route in ("L", "E"):
            rows = chain(route, seed)
            out[f"{route}{seed}"] = rows
            print(f"{route}{seed}  " + "  ".join(f"g{r['gen']} do {r['do']:.2f} on {r['on']:.2f} off {r['off']:.2f}"
                                               for r in rows) + f"  ({time.time()-t0:.0f}s)", flush=True)
            json.dump(out, open(os.path.join(HERE, f"EXP-22-{os.environ.get('MODE', 'grade')}-s{SEED0}.json"), "w"))


if __name__ == "__main__":
    main()
