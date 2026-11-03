"""EXP-07e: where is EXP-07d's limit, the inputs, the brain's size, learning only when aroused, or the actor's step?

Pre-registered in experiments/EXP-07e.md before any data. Run: TAG=<sha> python -u exp/EXP-07e_locate.py
SMOKE=1 runs 30 moments of one seed per arm and prints only that each arm composes, trains and answers.
Every seed gets a COMBINATION rule (EXP-07d's four, s % 4): no sum of the 6 inputs gets more than 6 of 8.
Arms change one thing each against the founder control A0:
  A0 control   compose(inputs=6, actions=2, arousal=True), trained through live (EXP-07d's arm, fresh seeds, 0.93)
  A  inputs    the 6 inputs plus a one-hot of the cue (14 inputs), so a sum of input weights can solve all 8
  B  size      modules=(256,): four times the default association population (64)
  C  step      trained through step, which learns on every moment, instead of live
  D  recipe    actor_eta=0.1, actor_eta_bias=0.01, memory_choice=True (0.93.0 CHANGELOG, #208/#209), through live
Exam (all arms): per cue, a fresh deepcopy answers with act(greedy=True); the exam does not touch the brain or
the stream. Greedy answers make the 6-of-8 ceiling exact: a score of 7 or 8 means the brain combined the inputs.
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
ARMS = ("A0", "A", "B", "C", "D")


def _two_hot(i, ctx):
    v = np.zeros(6)
    v[i] = 1.0
    v[ctx] = 1.0
    return v


# EXP-07b's cues: rows 0-3 are A (cue i = {i, 4 if i < 2 else 5}), rows 4-7 are B (the other context).
CUES6 = np.array([_two_hot(i, 4 if i < 2 else 5) for i in range(4)] + [_two_hot(i, 5 if i < 2 else 4) for i in range(4)])
CUES14 = np.hstack([CUES6, np.eye(8)])


def cues_for(arm):
    return CUES14 if arm == "A" else CUES6


def targets(rule_a):
    return [rule_a[i] for i in range(4)] + [1 - rule_a[i] for i in range(4)]


def best_linear(cues, t):
    """Most cues a linear threshold gets right (integer weights and bias in -3..3, exhaustive for 6 inputs)."""
    n = cues.shape[1]
    if n > 6:  # one-hot cue units: one weight per cue solves every assignment
        return 8
    grid = np.array(list(itertools.product(range(-3, 4), repeat=n + 1)), dtype=float)
    act = (grid[:, :n] @ cues.T + grid[:, n:n + 1]) > 0
    return int((act == np.array(t, dtype=bool)).sum(axis=1).max())


def compose(arm, seed):
    n_in = 14 if arm == "A" else 6
    if arm == "B":
        return Brain.compose(inputs=n_in, actions=2, arousal=True, modules=(256,), seed=seed)
    if arm == "D":
        return Brain.compose(inputs=n_in, actions=2, arousal=True, seed=seed,
                             actor_eta=0.1, actor_eta_bias=0.01, memory_choice=True)
    return Brain.compose(inputs=n_in, actions=2, arousal=True, seed=seed)


def moment(brain, arm, obs, reward=None):
    """One training moment under the documented refusal contract (docs/start.md, Qualification and refusal)."""
    call = brain.step if arm == "C" else brain.live
    for _ in range(5):
        try:
            if reward is None:
                return int(call(obs)[0])
            return int(call(obs, reward=np.array([float(reward)]))[0])
        except RuntimeError:
            if not brain.pending_feedback:
                reward = None
    raise RuntimeError("no settled answer in 5 tries")


def exam(brain, cues):
    return [int(copy.deepcopy(brain).act(cues[[c]], greedy=True)[0]) for c in range(8)]


def run(arm, s):
    rule = COMB_RULES[s % 4]
    t = targets(rule)
    cues = cues_for(arm)
    rng = np.random.default_rng(BASE + s)          # same cue stream in every arm for a given seed
    brain = compose(arm, BASE + s)
    owed, exams = None, {}
    for k in range(1, CHECKS[-1] + 1):
        c = int(rng.integers(8))
        a = moment(brain, arm, cues[[c]], owed)
        owed = 1.0 if a == t[c] else -1.0
        if k in CHECKS:
            ans = exam(brain, cues)
            exams[k] = dict(score=sum(int(x == y) for x, y in zip(ans, t)) / 8, ans=ans)
    return dict(arm=arm, seed=BASE + s, rule=list(rule), exams=exams)


def verdict(scores):
    n_beat = int(sum(1 for x in scores if x > 0.75))
    v = "LEARNS" if n_beat >= 7 else ("PARTIAL" if n_beat >= 3 else "FAILS")
    return v, n_beat


def main():
    t0 = time.time()
    print(f"EXP-07e on cadence {cadence.__version__}: {SEEDS} seeds x arms {ARMS}, combination rules only, "
          f"exams at {CHECKS}{' (SMOKE)' if SMOKE else ''}", flush=True)
    ceil6 = sorted({best_linear(CUES6, targets(r)) for r in COMB_RULES})
    ceil14 = sorted({best_linear(CUES14, targets(r)) for r in COMB_RULES})
    print(f"linear ceiling (cues right of 8): 6 inputs {ceil6}, 14 inputs (arm A) {ceil14}", flush=True)
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
            print(f"  {arm:<2} seed {r['seed']} rule {r['rule']}  {curve}  ans@{PRIMARY} {r['exams'][PRIMARY]['ans']}  "
                  f"({time.time() - ts:.0f} s)", flush=True)
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
        print(f"{arm:<2} @{PRIMARY}: mean {o['mean']:.3f} (SEM {o['sem']:.3f})  above 6/8 {o['beat']}/{SEEDS}  "
              f"8/8 {o['full']}/{SEEDS}  one answer {o['one_answer']}/{SEEDS}  -> {o['verdict']}  | curve "
              + "  ".join(f"{k}:{out[arm][k]['mean']:.3f}" for k in CHECKS), flush=True)
    print(f"VERDICTS at {PRIMARY}: " + "  ".join(f"{a}={out[a][PRIMARY]['verdict']}" for a in ARMS)
          + f"  ({round(time.time() - t0)} s)")
    tag = os.environ.get("TAG", "run")
    json.dump(dict(version=cadence.__version__, ceilings=dict(six=ceil6, fourteen=ceil14), checks=out, rows=rows),
              open(os.path.join(os.path.dirname(__file__), f"EXP-07e-{tag}.json"), "w"), indent=1, default=float)
    return 0


if __name__ == "__main__":
    sys.exit(main())
