"""EXP-07g: is the episodic memory's lift a per-situation lookup, and does the slower actor pair lift
EXP-07d's limit without the memory?

Pre-registered in experiments/EXP-07g.md before any data. Run: TAG=<sha> python -u exp/EXP-07g_split2.py
SMOKE=1 runs 30 moments of one seed per arm and prints only that each arm composes, trains and answers.
The harness is EXP-07f_split.py's (EXP-07e's), unchanged: the same 8 cues, the same 10 combination-rule
seeds and cue streams, 1600 moments through live, the same greedy exam and the same brute-forced 6-of-8
ceiling. Arms add settings to the founder compose(inputs=6, actions=2, arousal=True):
  MEM      control  memory_choice=True alone; EXP-07f's MEM arm, expected to repeat its answers exactly
  MEMCTX0  memory_choice=True, memory_context=0.0: the place records alone, keyed by the observation
           through the memory's fixed random separation, no context in the key
  PAIR     actor_eta=0.1, actor_eta_bias=0.01 without the memory: the one combination EXP-07f did not run
Reproduction check: MEM per-seed exam answers are compared with exp/EXP-07f-a4fcea0.json.
The JSON is written as .partial and renamed when the run finishes.
"""
import copy
import itertools
import json
import os
import sys
import time

import numpy as np

import cadence
from cadence import Brain

SEEDS = int(os.environ.get("SEEDS", "10"))
SMOKE = os.environ.get("SMOKE") == "1"
BASE = 7_075_000
CHECKS = (30,) if SMOKE else (400, 800, 1600)
PRIMARY = CHECKS[-1]
COMB_RULES = [(0, 1, 0, 1), (0, 1, 1, 0), (1, 0, 0, 1), (1, 0, 1, 0)]
ARMS = ("MEM", "MEMCTX0", "PAIR")
SETTINGS = {
    "MEM": dict(memory_choice=True),
    "MEMCTX0": dict(memory_choice=True, memory_context=0.0),
    "PAIR": dict(actor_eta=0.1, actor_eta_bias=0.01),
}
REPRO = {"MEM": "MEM"}  # our arm -> EXP-07f's arm
HERE = os.path.dirname(os.path.abspath(__file__))
EXP07F = os.path.join(HERE, "EXP-07f-a4fcea0.json")


def _two_hot(i, ctx):
    v = np.zeros(6)
    v[i] = 1.0
    v[ctx] = 1.0
    return v


# EXP-07b's cues: rows 0-3 are A (cue i = {i, 4 if i < 2 else 5}), rows 4-7 are B (the other context).
CUES6 = np.array([_two_hot(i, 4 if i < 2 else 5) for i in range(4)] + [_two_hot(i, 5 if i < 2 else 4) for i in range(4)])


def targets(rule_a):
    return [rule_a[i] for i in range(4)] + [1 - rule_a[i] for i in range(4)]


def best_linear(cues, t):
    """Most cues a linear threshold gets right (integer weights and bias in -3..3, exhaustive for 6 inputs)."""
    n = cues.shape[1]
    grid = np.array(list(itertools.product(range(-3, 4), repeat=n + 1)), dtype=float)
    act = (grid[:, :n] @ cues.T + grid[:, n:n + 1]) > 0
    return int((act == np.array(t, dtype=bool)).sum(axis=1).max())


def compose(arm, seed):
    return Brain.compose(inputs=6, actions=2, arousal=True, seed=seed, **SETTINGS[arm])


def _memory_context(b):
    """The memory's context weight as the composed brain reports it; None when no attribute names it."""
    for path in (("memory_context",), ("memories", "context"), ("memories", "config", "context"),
                 ("memory", "context"), ("memory", "config", "context")):
        obj = b
        for name in path:
            obj = getattr(obj, name, None)
            if obj is None:
                break
        if obj is not None and not callable(obj):
            try:
                return float(obj)
            except (TypeError, ValueError):
                return repr(obj)
    return None


def settings_read(arm):
    b = compose(arm, BASE)
    c = b.basal_ganglia.config
    return dict(actor_eta=float(c.eta), actor_eta_bias=float(c.eta_bias), memory_choice=bool(b.memory_choice),
                memory_context=_memory_context(b))


def moment(brain, obs, reward=None):
    """One training moment under the documented refusal contract (docs/start.md, Qualification and refusal)."""
    for _ in range(5):
        try:
            if reward is None:
                return int(brain.live(obs)[0])
            return int(brain.live(obs, reward=np.array([float(reward)]))[0])
        except RuntimeError:
            if not brain.pending_feedback:
                reward = None
    raise RuntimeError("no settled answer in 5 tries")


def exam(brain, cues):
    return [int(copy.deepcopy(brain).act(cues[[c]], greedy=True)[0]) for c in range(8)]


def run(arm, s):
    rule = COMB_RULES[s % 4]
    t = targets(rule)
    cues = CUES6
    rng = np.random.default_rng(BASE + s)          # same cue stream in every arm for a given seed
    brain = compose(arm, BASE + s)
    owed, exams = None, {}
    for k in range(1, CHECKS[-1] + 1):
        c = int(rng.integers(8))
        a = moment(brain, cues[[c]], owed)
        owed = 1.0 if a == t[c] else -1.0
        if k in CHECKS:
            ans = exam(brain, cues)
            exams[k] = dict(score=sum(int(x == y) for x, y in zip(ans, t)) / 8, ans=ans)
    return dict(arm=arm, seed=BASE + s, rule=list(rule), exams=exams)


def verdict(scores):
    n_beat = int(sum(1 for x in scores if x > 0.75))
    v = "LEARNS" if n_beat >= 7 else ("PARTIAL" if n_beat >= 3 else "FAILS")
    return v, n_beat


def reproduction(rows):
    """Per seed, are MEM's answers at every exam the same as EXP-07f's MEM arm?"""
    old = json.load(open(EXP07F, encoding="utf-8"))
    ref = {(r["arm"], r["seed"]): r for r in old["rows"]}
    out = {}
    for arm, old_arm in REPRO.items():
        same, n = 0, 0
        for r in rows:
            if r["arm"] != arm:
                continue
            n += 1
            o = ref.get((old_arm, r["seed"]))
            if o is not None and all(o["exams"][str(k)]["ans"] == r["exams"][k]["ans"] for k in CHECKS):
                same += 1
        out[arm] = dict(identical_seeds=same, seeds=n, exp07f_version=old["version"])
    return out


def main():
    t0 = time.time()
    print(f"EXP-07g on cadence {cadence.__version__}: {SEEDS} seeds x arms {ARMS}, combination rules only, "
          f"exams at {CHECKS}{' (SMOKE)' if SMOKE else ''}", flush=True)
    ceil6 = sorted({best_linear(CUES6, targets(r)) for r in COMB_RULES})
    print(f"linear ceiling (cues right of 8): 6 inputs {ceil6}", flush=True)
    rows = []
    for arm in ARMS:
        for s in range(1 if SMOKE else SEEDS):
            ts = time.time()
            r = run(arm, s)
            rows.append(r)
            if SMOKE:
                print(f"  smoke {arm}: composed, trained {CHECKS[-1]} moments, answered 8 cues ({time.time() - ts:.1f} s)", flush=True)
                continue
            curve = "  ".join(f"{k}:{r['exams'][k]['score']:.3f}" for k in CHECKS)
            print(f"  {arm:<7} seed {r['seed']} rule {r['rule']}  {curve}  ans@{PRIMARY} {r['exams'][PRIMARY]['ans']}  "
                  f"({time.time() - ts:.0f} s)", flush=True)
    # read back after the runs, so this extra compose cannot shift anything the runs see
    read = {arm: settings_read(arm) for arm in ARMS}
    for arm in ARMS:
        print(f"  settings {arm:<7} {read[arm]}", flush=True)
    if SMOKE:
        print(f"SMOKE ok ({round(time.time() - t0)} s)")
        return 0
    out = {}
    for arm in ARMS:
        out[arm] = {}
        for k in CHECKS:
            sc = np.array([r["exams"][k]["score"] for r in rows if r["arm"] == arm])
            v, n_beat = verdict(sc)
            one = int(sum(1 for r in rows if r["arm"] == arm and len(set(r["exams"][k]["ans"])) == 1))
            sem = float(sc.std(ddof=1) / np.sqrt(len(sc))) if len(sc) > 1 else float("nan")
            out[arm][k] = dict(mean=float(sc.mean()), sem=sem, beat=n_beat, full=int(sum(sc == 1.0)), one_answer=one,
                               verdict=v)
        o = out[arm][PRIMARY]
        print(f"{arm:<7} @{PRIMARY}: mean {o['mean']:.3f} (SEM {o['sem']:.3f})  above 6/8 {o['beat']}/{SEEDS}  "
              f"8/8 {o['full']}/{SEEDS}  one answer {o['one_answer']}/{SEEDS}  -> {o['verdict']}  | curve "
              + "  ".join(f"{k}:{out[arm][k]['mean']:.3f}" for k in CHECKS), flush=True)
    rep = reproduction(rows)
    for arm, x in rep.items():
        print(f"reproduction {arm} vs EXP-07f ({x['exp07f_version']}): answers identical at every exam on "
              f"{x['identical_seeds']}/{x['seeds']} seeds", flush=True)
    print(f"VERDICTS at {PRIMARY}: " + "  ".join(f"{a}={out[a][PRIMARY]['verdict']}" for a in ARMS)
          + f"  ({round(time.time() - t0)} s)")
    tag = os.environ.get("TAG", "run")
    path = os.path.join(HERE, f"EXP-07g-{tag}.json")
    with open(path + ".partial", "w", encoding="utf-8") as f:
        json.dump(dict(version=cadence.__version__, settings=read, ceilings=dict(six=ceil6), checks=out,
                       reproduction=rep, rows=rows), f, indent=1, default=float)
    os.replace(path + ".partial", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
