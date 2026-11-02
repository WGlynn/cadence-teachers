"""EXP-07d: can the brain learn EXP-07b's 8-cue task when all cues are trained mixed from birth?

Pre-registered in experiments/EXP-07d.md before any data. Run: TAG=<sha> python -u exp/EXP-07d_joint.py
Rule type fixed by construction: seeds 0-9 SUM rules (A cues 0 and 1 share an action, a sum of input weights solves
all 8), seeds 10-19 COMBINATION rules (no sum of input weights gets more than 6 of 8; checked below by brute force).
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

SEEDS = int(os.environ.get("SEEDS", "20"))
BASE = 7_074_000
CHECKS = (200, 400, 800, 1600)
PRIMARY = 800
SUM_RULES = [(0, 0, 1, 1), (1, 1, 0, 0)]
COMB_RULES = [(0, 1, 0, 1), (0, 1, 1, 0), (1, 0, 0, 1), (1, 0, 1, 0)]


def _two_hot(i, ctx):
    v = np.zeros(6)
    v[i] = 1.0
    v[ctx] = 1.0
    return v


# EXP-07b's cues. Rows 0-3 are A (cue i = {i, 4 if i < 2 else 5}), rows 4-7 are B (the other context).
CUES = np.array([_two_hot(i, 4 if i < 2 else 5) for i in range(4)] + [_two_hot(i, 5 if i < 2 else 4) for i in range(4)])


def targets(rule_a):
    """Right action for each of the 8 cues: A cue i wants rule_a[i], B cue i the opposite."""
    return [rule_a[i] for i in range(4)] + [1 - rule_a[i] for i in range(4)]


def best_linear(t):
    """Most cues a linear threshold on the 6 inputs (integer weights and bias in -3..3) gets right."""
    grid = np.array(list(itertools.product(range(-3, 4), repeat=7)), dtype=float)   # 6 weights + bias
    act = (grid[:, :6] @ CUES.T + grid[:, 6:7]) > 0
    return int((act == np.array(t, dtype=bool)).sum(axis=1).max())


def rule_of(s):
    return SUM_RULES[s % 2] if s < 10 else COMB_RULES[s % 4]


def live(brain, cue, reward=None):
    """One `live` call under the documented refusal contract (docs/start.md, Qualification and refusal)."""
    obs = CUES[[cue]]
    for _ in range(5):
        try:
            if reward is None:
                return int(brain.live(obs)[0])
            return int(brain.live(obs, reward=np.array([float(reward)]))[0])
        except RuntimeError:
            if not brain.pending_feedback:
                reward = None
    raise RuntimeError("no settled answer in 5 tries")


def answers(brain, pending_reward):
    """The brain's answer to each of the 8 cues, each from a fresh copy that first gets the true pending outcome."""
    return [live(copy.deepcopy(brain), c, pending_reward) for c in range(8)]


def run(s):
    rule = rule_of(s)
    t = targets(rule)
    rng = np.random.default_rng(BASE + s)
    brain = Brain.compose(inputs=6, actions=2, arousal=True, seed=BASE + s)
    owed, exams = None, {}
    for k in range(1, CHECKS[-1] + 1):
        c = int(rng.integers(8))
        a = live(brain, c, owed)
        owed = 1.0 if a == t[c] else -1.0
        if k in CHECKS:
            ans = answers(brain, owed)
            exams[k] = dict(score=sum(int(x == y) for x, y in zip(ans, t)) / 8, ans=ans)
    return dict(seed=BASE + s, kind="sum" if s < 10 else "comb", rule=list(rule), exams=exams)


def verdict(sum_scores, comb_scores):
    n_full = int(sum(1 for x in comb_scores if x == 1.0))
    if np.mean(sum_scores) < 0.85:
        return "VOID", n_full
    if np.mean(comb_scores) <= 0.80 and n_full <= 2:
        return "LIMIT", n_full
    if np.mean(comb_scores) >= 0.90 or n_full >= 7:
        return "LEARNABLE", n_full
    return "INCONCLUSIVE", n_full


def main():
    t0 = time.time()
    ceil_sum = sorted({best_linear(targets(r)) for r in SUM_RULES})
    ceil_comb = sorted({best_linear(targets(r)) for r in COMB_RULES})
    print(f"EXP-07d joint training on cadence {cadence.__version__}: {SEEDS} seeds, all 8 cues mixed from birth, "
          f"exams at {CHECKS}", flush=True)
    print(f"linear ceiling (cues right of 8): SUM rules {ceil_sum}, COMBINATION rules {ceil_comb}", flush=True)
    rows = []
    for s in range(SEEDS):
        r = run(s)
        rows.append(r)
        curve = "  ".join(f"{k}:{r['exams'][k]['score']:.3f}" for k in CHECKS)
        print(f"  seed {r['seed']} {r['kind']:<4} rule {r['rule']}  {curve}  ans@{PRIMARY} {r['exams'][PRIMARY]['ans']}",
              flush=True)
    out = {}
    for k in CHECKS:
        su = np.array([r["exams"][k]["score"] for r in rows if r["kind"] == "sum"])
        co = np.array([r["exams"][k]["score"] for r in rows if r["kind"] == "comb"])
        v, n_full = verdict(su, co)
        # paired by nothing: two independent groups, so the SEM of the difference combines both groups' SEMs
        sem = float(np.sqrt(su.var(ddof=1) / len(su) + co.var(ddof=1) / len(co))) if len(su) > 1 and len(co) > 1 else float("nan")
        beat = int(sum(1 for x in co if x > 0.75))
        collapse = int(sum(1 for r in rows if r["kind"] == "comb" and len(set(r["exams"][k]["ans"])) == 1))
        out[k] = dict(sum_mean=float(su.mean()), comb_mean=float(co.mean()), diff=float(su.mean() - co.mean()),
                      diff_sem=sem, comb_full=n_full, comb_beat_linear=beat, comb_collapse=collapse, verdict=v)
        print(f"@{k}: SUM {su.mean():.3f}  COMB {co.mean():.3f}  diff {su.mean() - co.mean():+.3f} (SEM {sem:.3f})  "
              f"COMB 8/8 {n_full}/10  beat 6/8 ceiling {beat}/10  one answer {collapse}/10  -> {v}", flush=True)
    print(f"VERDICT (primary, {PRIMARY} moments): {out[PRIMARY]['verdict']}  |  secondary at {CHECKS[-1]}: "
          f"{out[CHECKS[-1]]['verdict']}  ({round(time.time() - t0)} s)")
    tag = os.environ.get("TAG", "run")
    json.dump(dict(version=cadence.__version__, ceilings=dict(sum=ceil_sum, comb=ceil_comb), checks=out, rows=rows),
              open(os.path.join(os.path.dirname(__file__), f"EXP-07d-{tag}.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    sys.exit(main())
