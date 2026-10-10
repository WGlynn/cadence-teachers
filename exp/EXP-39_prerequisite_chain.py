"""
EXP-39: teaching a prerequisite chain (the "Stone Age COLD" problem).

A developer benchmarking Cadence 0.80 reported that a brain collapses onto one action (CRAFT_FIRE) instead of learning
the chain gather wood -> gather stone -> craft fire -> warm up, under sparse reward, reduced action spaces and a forward
(prefix) curriculum. Our reply advised: (1) put the inventory in the observation, (2) teach the chain BACKWARDS, one
graded step at a time, (3) grade, do not label. That advice rested on a 2-step chain (key-door, EXP-19/22). This tests
it on a 4-step chain.

World: inventory state (wood, stone, fire). Actions: 0 GATHER_WOOD, 1 GATHER_STONE, 2 CRAFT_FIRE, 3 WARM_UP.
CRAFT_FIRE turns wood+stone into fire (otherwise nothing happens); WARM_UP with fire = success, the episode ends.
Gathering what you hold changes nothing. At most MAX_STEPS moves per episode. Optimal moves per state: {} -> wood or
stone, {wood} -> stone, {stone} -> wood, {wood, stone} -> craft, {fire} -> warm.
Brain: Cadence Brain.compose(4 inputs = 3 inventory flags + constant, 4 actions) at the key-door protocol-3 operating
point (Cadence's own delayed-credit configuration: traces, consolidation, actor genes), living through `step` (learns
every outcome; the teaching API used in EXP-19). Same brain, same API, same budget of B episodes in every arm.
Arms:
  SPARSE-FWD  : world reward only (+1 on success, else 0), every episode starts empty. The reported failing setup.
  SPARSE-BWD  : world reward only, reverse-curriculum starts (fire first, then wood+stone, then one item, then empty).
  GRADE-FWD   : a teacher grades every move (+1 if optimal in that state, else -1), every episode starts empty.
  GRADE-BWD   : grading + reverse-curriculum starts. Our advice.
  GRADE-BWD-BLIND : GRADE-BWD with the inventory hidden (observation is the constant only). Tests advice (1).
Test (frozen, held-out): a saved copy acts greedily from empty for TEST_STEPS moves; success = warmed up. Also policy
accuracy: share of the 5 reachable states whose greedy move is optimal.

PREDICTION (2026-10-10, written before any run): GRADE-BWD solves the chain on most students (>= 10/12) at a budget
where SPARSE-FWD mostly fails (<= 3/12, often collapsing onto one action); GRADE-FWD close to GRADE-BWD (dense grading
already gives every visited state a signal; forward starts visit late states only once early ones work, so it may lag
at small budgets); SPARSE-BWD above SPARSE-FWD (the curriculum shortens credit paths) but below the graded arms;
GRADE-BWD-BLIND fails (identical observations cannot map to four different moves without memory).
The budget B is chosen by a pilot (RUN GATE line 2) before the full run.
PILOT (4 seeds, B = 40 / 150 / 500 / 1500; solved counts): SPARSE-FWD 0,0,0,3; SPARSE-BWD 0,0,0,0; GRADE-FWD 4,4,4,4;
GRADE-BWD 2,4,4,4; GRADE-BWD-BLIND 0,0,0,0. Every chain link printed (per-move reward -> policy accuracy -> rollout).
PREDICTION REVISED after the pilot (before the full run): the window is the budget itself, so the full run sweeps B.
GRADE-FWD >= GRADE-BWD at B=40 (dense grading makes backward starts unnecessary); both graded arms solve >= 11/12 from
B=150. SPARSE-BWD stays near 0/12 at every budget and collapses onto WARM/CRAFT (the reported failure mode, caused by
the reverse curriculum under sparse reward); SPARSE-FWD rises only at the largest budget (6-11/12 at B=1500).
BLIND 0/12 everywhere.
"""
import json, os, sys, tempfile, time
from dataclasses import replace
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cadence_src import KEYDOOR  # noqa: E402

POINT = json.load(open(os.path.join(KEYDOOR, "protocol-3.json")))["operating_point"]
WOOD, STONE, CRAFT, WARM = range(4)
NAMES = ["wood", "stone", "craft", "warm"]
EMPTY = (0, 0, 0)
STATES = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0), (0, 0, 1)]
DEPTH = {(0, 0, 1): 0, (1, 1, 0): 1, (1, 0, 0): 2, (0, 1, 0): 2, (0, 0, 0): 3}   # moves left to success - 1
MAX_STEPS = int(os.environ.get("MAX_STEPS", 8))
TEST_STEPS = 6
B = int(os.environ.get("B", 150))
SEEDS = int(os.environ.get("SEEDS", 12))
ARMS = os.environ.get("ARMS", "SPARSE-FWD,SPARSE-BWD,GRADE-FWD,GRADE-BWD,GRADE-BWD-BLIND").split(",")
TAG = os.environ.get("TAG", "full")


def optimal(s):
    w, st, f = s
    if f:
        return {WARM}
    if w and st:
        return {CRAFT}
    if w:
        return {STONE}
    if st:
        return {WOOD}
    return {WOOD, STONE}


def transition(s, a):
    """-> (next state, success)"""
    w, st, f = s
    if a == WOOD:
        return (1, st, f), False
    if a == STONE:
        return (w, 1, f), False
    if a == CRAFT:
        return ((0, 0, 1) if (w and st) else s), False
    return s, bool(f)          # WARM_UP


def obs(s, blind):
    return np.array([[0.0, 0.0, 0.0, 1.0]]) if blind else np.array([[float(s[0]), float(s[1]), float(s[2]), 1.0]])


def make_brain(seed):
    """Brain.compose at the key-door protocol-3 operating point, generalised to 4 inputs and 4 actions
    (same option mapping as benchmarks/keydoor/key_door.py make_brain, no arousal: the `step` brain)."""
    import cadence as cd
    opts = {}
    if "trace_amplitude" in POINT:
        opts["working_memory_amplitude"] = POINT["trace_amplitude"]
    if "trace_decay" in POINT:
        opts["working_memory_decay"] = POINT["trace_decay"]
    if "consolidation" in POINT:
        opts["consolidation"] = POINT["consolidation"]
    brain = cd.Brain.compose(4, 4, modules=tuple(POINT.get("modules", (32,))), seed=seed, **opts)
    names = type(brain.basal_ganglia.config).__slots__
    actor = {k: POINT[k] for k in names if k in POINT}
    if "eta" in actor and "eta_bias" not in actor:
        actor["eta_bias"] = actor["eta"] / 10.0
    if actor:
        brain.basal_ganglia.config = replace(brain.basal_ganglia.config, **actor)
    if POINT.get("learner"):
        brain.learner.config = replace(brain.learner.config, **POINT["learner"])
    return brain


def start_state(arm, e, rng):
    if not arm.endswith("BWD") and "BWD-" not in arm:
        return EMPTY
    stage = min(3, e * 4 // B)                    # 4 equal stages: depth <= 0, <= 1, <= 2, <= 3
    pool = [s for s in STATES if DEPTH[s] <= stage]
    return pool[int(rng.integers(len(pool)))]


def train(brain, arm, rng):
    blind = arm.endswith("BLIND")
    graded = arm.startswith("GRADE")
    pending, successes, moves = None, 0, np.zeros(4)
    for e in range(B):
        s = start_state(arm, e, rng)
        for t in range(MAX_STEPS):
            fb = {} if pending is None else {"reward": [pending[0]], "done": [pending[1]]}
            a = int(brain.step(obs(s, blind), **fb)[0])
            moves[a] += 1
            s2, success = transition(s, a)
            r = (1.0 if a in optimal(s) else -1.0) if graded else (1.0 if success else 0.0)
            pending = (r, success or t == MAX_STEPS - 1)
            s = s2
            if success:
                successes += 1
                break
    if pending is not None:
        brain.step(obs(EMPTY, blind), reward=[pending[0]], done=[pending[1]])
    return successes / B, (moves / max(1, moves.sum())).tolist()


def test(path, blind):
    import cadence as cd
    b = cd.Brain.load(path)
    # policy accuracy: greedy move in each reachable state
    pol = []
    for s in STATES:
        b.reset()
        pol.append(int(b.act(obs(s, blind), greedy=True)[0]))
    acc = float(np.mean([pol[i] in optimal(s) for i, s in enumerate(STATES)]))
    # greedy rollout from empty
    b.reset()
    s, ok, path_moves = EMPTY, False, []
    for _ in range(TEST_STEPS):
        a = int(b.act(obs(s, blind), greedy=True)[0])
        path_moves.append(NAMES[a])
        s, success = transition(s, a)
        if success:
            ok = True
            break
    return ok, acc, pol, path_moves


def run(args):
    arm, seed = args
    import cadence as cd
    brain = make_brain(7000 + seed)
    rng = np.random.default_rng(3000 + seed)
    train_rate, move_share = train(brain, arm, rng)
    with tempfile.TemporaryDirectory() as d:
        ok, acc, pol, path_moves = test(brain.save(os.path.join(d, "b.npz")), arm.endswith("BLIND"))
    collapse = max(move_share)                     # share of training moves on the single most used action
    return dict(arm=arm, seed=seed, B=B, success=int(ok), policy_acc=acc, policy=[NAMES[a] for a in pol],
                path=path_moves, train_success=train_rate, move_share=move_share, collapse=collapse,
                cadence=getattr(cd, "__version__", "?"))


def main():
    t0 = time.time()
    ckpt = os.path.join(HERE, f"EXP-39-{TAG}-B{B}.jsonl")
    res = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["arm"], r["seed"]) for r in res}
    jobs = [(a, s) for a in ARMS for s in range(SEEDS) if (a, s) not in done]
    print(f"resuming: {len(done)} done, {len(jobs)} to run", flush=True)
    with get_context("spawn").Pool(int(os.environ.get("WORKERS", 3))) as pool:
        for r in pool.imap_unordered(run, jobs):
            res.append(r)
            with open(ckpt, "a") as f:
                f.write(json.dumps(r) + "\n")
    res = [r for r in res if r["arm"] in ARMS and r["seed"] < SEEDS]
    print(f"EXP-39 prerequisite chain  B={B} episodes  MAX_STEPS={MAX_STEPS}  seeds={SEEDS}  ({time.time()-t0:.0f}s)")
    for a in ARMS:
        rs = [r for r in res if r["arm"] == a]
        acc = np.array([r["policy_acc"] for r in rs])
        sem = acc.std(ddof=1) / len(acc) ** .5 if len(acc) > 1 else 0.0
        print(f"  {a:16s} solved {sum(r['success'] for r in rs):2d}/{len(rs)}  policy acc {acc.mean():.2f} (SEM {sem:.2f})"
              f"  train success {np.mean([r['train_success'] for r in rs]):.2f}  top-move share {np.mean([r['collapse'] for r in rs]):.2f}"
              f"  e.g. path {' > '.join(rs[0]['path'])}")
    json.dump(res, open(os.path.join(HERE, f"EXP-39-{TAG}-B{B}.json"), "w"))


if __name__ == "__main__":
    main()
