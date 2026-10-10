"""
EXP-01 — Does ANY arousal gene setting stabilize the fast reward-flip?

Baseline (v0.75, stock ArousalConfig) did NOT damp the oscillation / sub-1.0 post-flip cap.
Here we sweep arousal genes relative to their defaults and measure whether any region recovers and
HOLDS near 1.0 after the reward rule inverts. Same 4-ctx / 2-action bandit, continuing-stream
`brain.live`, +1/-1 reward. Metric per (config, seed): post-flip hold = mean of last 4 greedy evals.

Insight is the number, pass or fail. A flat "nothing stabilizes it" is a real result.
"""
import os, tempfile, dataclasses as dc, numpy as np
from cadence import Brain, ArousalConfig

RULE = np.array([0, 0, 1, 1])
onehot = lambda c: np.eye(4)[[c]]
DEF = {f.name: getattr(ArousalConfig(), f.name) for f in dc.fields(ArousalConfig)}


def mk(**scale):
    """ArousalConfig with named fields scaled from their defaults."""
    kw = {}
    for k, factor in scale.items():
        kw[k] = type(DEF[k])(DEF[k] * factor) if isinstance(DEF[k], (int, float)) else DEF[k]
    return ArousalConfig(**kw)


CONFIGS = {
    "default":          ArousalConfig(),
    "rouse-easy(thr/2)": mk(threshold=0.5),
    "rouse-hard(thr*2)": mk(threshold=2.0),
    "hot(heat*2)":       mk(heat=2.0),
    "young(youth*2)":    mk(youth=2.0),
    "slow-decay(dec/2)": mk(decay=0.5),
    "tol-tight(tol/2)":  mk(tolerance=0.5),
    "combo(thr/2,heat2)": mk(threshold=0.5, heat=2.0),
}


def clone_eval(brain, rule, tag):
    c2 = Brain.load(brain.save(os.path.join(tempfile.gettempdir(), f"exp01_{tag}")))
    # reset before EVERY cue: training uses done=True (1-step episodes), so each probe
    # must start from cleared state too. reset() keeps learned params + memory. (Bernhard, #164)
    hits = 0
    for c in range(4):
        c2.reset()
        hits += int(np.asarray(c2.act(onehot(c), greedy=True)).reshape(-1)[0]) == int(rule[c])
    return hits / 4


def run(cfg, seed, steps=2400, flip_at=1200):
    brain = Brain.compose(inputs=4, actions=2, modules=(16, 8), seed=seed, arousal=cfg)
    rule, reward, post = RULE.copy(), None, []
    for t in range(steps):
        if t == flip_at:
            rule = 1 - RULE
        c = t % 4
        a = brain.live(onehot(c)) if reward is None else brain.live(onehot(c), reward=reward, done=np.array([True]))
        a = int(np.asarray(a).reshape(-1)[0])
        reward = np.array([1.0 if a == int(rule[c]) else -1.0])
        if t > flip_at and t % 150 == 0:
            post.append(clone_eval(brain, rule, f"{seed}"))
    post.append(clone_eval(brain, rule, f"{seed}"))
    return np.mean(post[-4:])


def main(seeds=range(7, 13)):
    print(f"defaults: {DEF}")
    print(f"\n{'config':<20}{'post_hold_mean':<16}{'best_seed':<10}")
    rows = []
    for name, cfg in CONFIGS.items():
        holds = [run(cfg, s) for s in seeds]
        m, best = np.mean(holds), max(holds)
        print(f"{name:<20}{m:<16.3f}{best:<10.2f}")
        rows.append((name, m, best))
    rows.sort(key=lambda r: -r[1])
    print(f"\nBEST: {rows[0][0]} post_hold={rows[0][1]:.3f} (baseline step path was ~0.64)")
    print("STABILIZED" if rows[0][1] >= 0.90 else "NOT STABILIZED (no gene region holds >=0.90)")


if __name__ == "__main__":
    main()
