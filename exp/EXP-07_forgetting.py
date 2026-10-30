"""EXP-07: does reward-learning an unrelated skill B on new cues erase a learned skill A?

Pre-registered in experiments/EXP-07.md before any data. Run: python -u exp/EXP-07_forgetting.py
"""
import copy
import json
import os
import sys
import time

import numpy as np

import cadence
from cadence import Brain

SEEDS = int(os.environ.get("SEEDS", "20"))
BASE = 7_070_000
N_A, N_B = 200, 200
CUES = np.eye(8)
A_CUES, B_CUES = [0, 1, 2, 3], [4, 5, 6, 7]


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


def rule_for(rng):
    """Two cues per action, assignment permuted: rule[i] is the right action for the i-th cue of the skill."""
    return {int(c): a for c, a in zip(rng.permutation(4), [0, 0, 1, 1])}


def exam(brain, cues, rule, pending_reward):
    """Score fresh copies, one answer per cue. Each copy first receives the TRUE outcome of the action the brain
    still has pending (None if nothing is pending), exactly as the next real moment would, then answers."""
    right = 0
    for i, c in enumerate(cues):
        twin = copy.deepcopy(brain)
        right += int(live(twin, c, pending_reward) == rule[i])
    return right / len(cues)


def train(brain, rng, cues, rule, n, pending_reward):
    """n moments on random cues of one skill. Returns the outcome still owed for the last action."""
    for _ in range(n):
        i = int(rng.integers(len(cues)))
        a = live(brain, cues[i], pending_reward)
        pending_reward = 1.0 if a == rule[i] else -1.0
    return pending_reward


def run(s):
    rng = np.random.default_rng(BASE + s)
    rule_a, rule_b = rule_for(rng), rule_for(rng)
    brain = Brain.compose(inputs=8, actions=2, arousal=True, seed=BASE + s)
    b_before = exam(brain, B_CUES, rule_b, None)
    owed = train(brain, rng, A_CUES, rule_a, N_A, None)
    a_before = exam(brain, A_CUES, rule_a, owed)          # CONTROL arm: the brain stops here
    learner = copy.deepcopy(brain)                          # LEARN-B arm: A's last outcome arrives with the first B cue
    owed_b = train(learner, rng, B_CUES, rule_b, N_B, owed)
    return dict(seed=BASE + s, a_before=a_before, a_after=exam(learner, A_CUES, rule_a, owed_b),
                b_after=exam(learner, B_CUES, rule_b, owed_b), b_before=b_before,
                age=int(learner.arousal.age), aroused=bool(learner.arousal.aroused))


def main():
    t0 = time.time()
    print(f"EXP-07 forgetting on cadence {cadence.__version__}: {SEEDS} seeds, A {N_A} then B {N_B} moments", flush=True)
    rows = []
    for s in range(SEEDS):
        r = run(s)
        rows.append(r)
        print(f"  seed {r['seed']}: A before {r['a_before']:.2f}  A after B {r['a_after']:.2f}  "
              f"B after {r['b_after']:.2f}  (B at birth {r['b_before']:.2f})", flush=True)
    a0 = np.array([r["a_before"] for r in rows]); a1 = np.array([r["a_after"] for r in rows])
    b1 = np.array([r["b_after"] for r in rows]); drop = a0 - a1
    sem = drop.std(ddof=1) / np.sqrt(len(drop))
    if a0.mean() < 0.75 or b1.mean() < 0.75:
        verdict = "VOID"
    elif drop.mean() <= 0.10 and a1.mean() >= 0.75:
        verdict = "SUPPORTIVE"
    elif drop.mean() >= 0.25 or a1.mean() <= 0.60:
        verdict = "FORGETTING"
    else:
        verdict = "INCONCLUSIVE"
    summary = dict(version=cadence.__version__, seeds=SEEDS, a_before=a0.mean(), a_after=a1.mean(),
                   b_after=b1.mean(), drop=drop.mean(), drop_sem=sem, seeds_lost_any_a=int((drop > 0).sum()),
                   verdict=verdict, seconds=round(time.time() - t0))
    print(f"MEANS: A before {a0.mean():.3f}  A after B {a1.mean():.3f}  drop {drop.mean():+.3f} (SEM {sem:.3f})  "
          f"B after {b1.mean():.3f}  seeds that lost any A {summary['seeds_lost_any_a']}/{SEEDS}")
    print(f"VERDICT: {verdict}  ({summary['seconds']} s)")
    tag = os.environ.get("TAG", "run")
    json.dump(dict(summary=summary, rows=rows), open(os.path.join(os.path.dirname(__file__), f"EXP-07-{tag}.json"), "w"),
              indent=1, default=float)


if __name__ == "__main__":
    sys.exit(main())
