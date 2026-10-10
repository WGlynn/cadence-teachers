"""
EXP-09 — v(S) transfer vs a COORDINATED-BUT-WRONG prior (program milestone M4).

M1 (EXP-08) showed measured transfer separates genuine from a surface-matched fake. The sharper
adversary (paper section 6, angle 1): a coordinated prior that AGREES with the true task on a
tunable fraction gamma of contexts. Peer-prediction / correlated-agreement breaks down past about
gamma* = 0.70 (a coordinated prior wins). Question: does TRANSFER measurement degrade at the same
crossover, or does reading a causal behavioral delta push the crossover higher (transfer is harder
to coordinate-fake than agreement)?

Setup reuses EXP-08's twin-brain ablation. The witness teaches a rule R_gamma that matches the
exogenous T on a gamma fraction of contexts (gamma=1.0 is genuine; gamma=0.5 is chance-correlated;
gamma=0.0 is the anti-correlated fake_wrong from EXP-08). We sweep gamma and measure transfer to T.

Honest read we are looking for: transfer should rise monotonically with gamma and cross zero near
the point where the prior stops being better-than-chance about T. The useful number is WHERE the
transfer crosses a worth threshold, compared to peer-prediction's 0.70. A fake only pays off if it
already carries most of the real T-information -> which is contributing, not faking.

Insight is the number, pass or fail.
"""
import os, tempfile, numpy as np
from cadence import Brain, ArousalConfig

K = 8
A = 2
MODULES = (16, 8)
WITNESS_STEPS = 1600
SEEDS = range(12)        # iter4b: crossover band only (low-gamma half done at 20 seeds in iter4a)
GAMMAS = [0.625, 0.75, 0.875, 1.0]
TMP = tempfile.gettempdir()

onehot = lambda c: np.eye(K)[[c]]


def make_rule(rng):
    while True:
        r = rng.integers(0, A, size=K)
        if len(set(r.tolist())) > 1:
            return r


def rule_at_gamma(T, gamma, rng):
    """A rule that agrees with T on ~gamma of contexts (A=2: disagree => the other action)."""
    R = T.copy()
    flip = rng.random(K) >= gamma     # flip ~ (1-gamma) of the contexts away from T
    R[flip] = (A - 1) - R[flip]
    return R


def eval_on(brain, rule, tag=None):
    # greedy act() with no reward is PURE (probed 2026-10-07: clone==direct, stable across passes),
    # so we eval directly instead of save/load-cloning — removes the dominant disk-I/O bottleneck.
    # #164 fix (Bernhard): training is 1-step episodes (done=True), so reset before EVERY probe
    # and once after, so eval state never leaks into the next training step. reset() keeps
    # learned params + memory.
    hits = 0
    for ctx in range(K):
        brain.reset()
        hits += int(np.asarray(brain.act(onehot(ctx), greedy=True)).reshape(-1)[0]) == int(rule[ctx])
    brain.reset()
    return hits / K


def ingest(brain, steps, reward_fn):
    reward = None
    for t in range(steps):
        ctx = t % K
        a = brain.live(onehot(ctx)) if reward is None else brain.live(
            onehot(ctx), reward=reward, done=np.array([True]))
        a = int(np.asarray(a).reshape(-1)[0])
        reward = np.array([float(reward_fn(ctx, a))])


def transfer_at(seed, g):
    """Transfer to exogenous T from a witness teaching a rule that agrees with T on ~g of contexts."""
    rng = np.random.default_rng(30_000 + seed)
    T = make_rule(rng)
    brain0 = Brain.compose(inputs=K, actions=A, modules=MODULES, seed=seed, arousal=ArousalConfig())
    snap = brain0.save(os.path.join(TMP, f"exp09_anc_{seed}"))
    acc0 = eval_on(brain0, T, f"base_{seed}")
    R = rule_at_gamma(T, g, np.random.default_rng(40_000 + seed + int(g * 1000)))
    b = Brain.load(snap)
    ingest(b, WITNESS_STEPS, lambda c, a: 1.0 if a == int(R[c]) else -1.0)
    return eval_on(b, T, f"g{int(g*1000)}_{seed}") - acc0


def main():
    # gamma-OUTER so each row prints as soon as it is computed: partial output survives a timeout,
    # and progress is visible. (iter3 buffered everything to the end and a timeout lost it.)
    print(f"EXP-09  v(S) transfer vs coordinated prior   K={K} A={A} witness={WITNESS_STEPS} "
          f"seeds={len(list(SEEDS))}", flush=True)
    print("gamma = fraction of contexts the prior agrees with T on (1.0=genuine, 0.5=chance)",
          flush=True)
    print(f"{'gamma':>6} {'mean_transfer':>14} {'SEM':>7} {'frac>0.15':>10}", flush=True)
    means, prev, crossing = {}, None, None
    for g in GAMMAS:
        v = np.array([transfer_at(s, g) for s in SEEDS], float)
        means[g] = v.mean()
        print(f"{g:>6.3f} {v.mean():>+14.3f} {v.std()/len(v)**.5:>7.3f} {float((v>0.15).mean()):>10.2f}",
              flush=True)
        if prev is not None and prev[1] <= 0.10 < v.mean():
            crossing = (prev[0], g)
        prev = (g, v.mean())
    print("-" * 42, flush=True)
    if crossing:
        print(f"worth-threshold (transfer>0.10) crossed between gamma={crossing[0]:.3f} and "
              f"{crossing[1]:.3f}.", flush=True)
    print("CONCEPTUAL compare (NOT a matched baseline): peer-prediction/correlated-agreement crossover",
          flush=True)
    print("~ gamma*=0.70 (paper 6.1). A real in-harness PP scorer is still queued (M4-harden item 2).",
          flush=True)
    print("If transfer only pays at a HIGH gamma, the coordinated fake must already carry most of the",
          flush=True)
    print("real T-information to win -> faking collapses into contributing. That is the result.",
          flush=True)


if __name__ == "__main__":
    main()
