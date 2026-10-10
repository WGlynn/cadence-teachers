"""
EXP-15 — MATCHED peer-prediction baseline vs transfer, same adversary (program M4).

Why: EXP-09 compared transfer against the Noesis peer-prediction crossover gamma*=0.70, but that
number lives on a DIFFERENT axis (noesis/node/examples/peer_prediction_sim.rs:130-141: gamma = the
fraction of the reference pool that is coordinated). EXP-09's gamma = how much a prior agrees with T.
Not comparable. This harness scores ONE adversary with BOTH mechanisms.

Adversary: a ring of witnesses that all teach the same rule R (agreeing with the true task T on a
fraction a_R of contexts). Genuine contributor teaches T. Reference pool for peer-prediction = P peers,
a fraction c of which are ring members (capital-independence violated); the rest are honest noisy
reporters of T (accuracy HONEST_ACC per context).

Scorers:
  - PP: Correlated-Agreement (same-task agreement minus cross-task agreement), Dasgupta-Ghosh /
    Shnayder spirit, same definition as peer_prediction_sim.rs::ca_score, over the K contexts.
  - Transfer: twin-brain ablation on exogenous T (EXP-08/09 harness, #164 per-probe reset).

Honest asymmetry (load-bearing): transfer CONSUMES an exogenous held-out task T; PP uses no ground
truth. Transfer's invariance to c is therefore partly by construction. The result is the price of that
assumption made visible, not a free win.

Insight is the number, pass or fail.
"""
import os, tempfile, numpy as np
from cadence import Brain, ArousalConfig

K, A = 8, 2
MODULES = (16, 8)
WITNESS_STEPS = 1600
SEEDS = range(12)
RING_AGREE = [0.5, 0.625, 0.75]        # how right the ring's shared rule is about T
COORD = [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]   # fraction of PP reference pool that is ring
P = 10                                  # PP reference pool size
HONEST_ACC = 0.9                        # honest reference reports T[k] w.p. 0.9
TMP = tempfile.gettempdir()
onehot = lambda c: np.eye(K)[[c]]


def make_rule(rng):
    while True:
        r = rng.integers(0, A, size=K)
        if len(set(r.tolist())) > 1:
            return r


def rule_with_agreement(T, agree, rng):
    """Exactly round(agree*K) contexts match T (exact, so a_R is not seed noise)."""
    R = T.copy()
    flip = rng.permutation(K)[: K - int(round(agree * K))]
    R[flip] = (A - 1) - R[flip]
    return R


# ---------------- peer prediction (Correlated Agreement) ----------------

def ca_score(report, refs):
    """mean over refs of [same-context agreement - cross-context agreement]."""
    s = []
    for r in refs:
        same = float((report == r).mean())
        cross = float(np.mean([report[k] == r[j] for k in range(K) for j in range(K) if j != k]))
        s.append(same - cross)
    return float(np.mean(s))


def pp_pool(T, R, c, rng):
    n_ring = int(round(c * P))
    refs = [R.copy() for _ in range(n_ring)]
    for _ in range(P - n_ring):
        noisy = T.copy()
        flip = rng.random(K) >= HONEST_ACC
        noisy[flip] = (A - 1) - noisy[flip]
        refs.append(noisy)
    return refs


# ---------------- transfer (twin-brain ablation) ----------------

def eval_on(brain, rule):
    hits = 0
    for ctx in range(K):
        brain.reset()   # #164: 1-step episodes -> reset before every probe
        hits += int(np.asarray(brain.act(onehot(ctx), greedy=True)).reshape(-1)[0]) == int(rule[ctx])
    brain.reset()
    return hits / K


def ingest(brain, rule):
    reward = None
    for t in range(WITNESS_STEPS):
        ctx = t % K
        a = brain.live(onehot(ctx)) if reward is None else brain.live(
            onehot(ctx), reward=reward, done=np.array([True]))
        a = int(np.asarray(a).reshape(-1)[0])
        reward = np.array([1.0 if a == int(rule[ctx]) else -1.0])


def transfer(seed, T, rule):
    b0 = Brain.compose(inputs=K, actions=A, modules=MODULES, seed=seed, arousal=ArousalConfig())
    snap = b0.save(os.path.join(TMP, f"exp15_{seed}"))
    base = eval_on(b0, T)
    b = Brain.load(snap)
    ingest(b, rule)
    return eval_on(b, T) - base


def main():
    print(f"EXP-15 matched PP vs transfer  K={K} P={P} honest_acc={HONEST_ACC} "
          f"witness={WITNESS_STEPS} seeds={len(list(SEEDS))}", flush=True)
    for aR in RING_AGREE:
        tr_g, tr_r = [], []
        pp_g = {c: [] for c in COORD}
        pp_r = {c: [] for c in COORD}
        for s in SEEDS:
            rng = np.random.default_rng(50_000 + s)
            T = make_rule(rng)
            R = rule_with_agreement(T, aR, np.random.default_rng(60_000 + s + int(aR * 1000)))
            tr_g.append(transfer(s, T, T))
            tr_r.append(transfer(s, T, R))
            for c in COORD:
                refs = pp_pool(T, R, c, np.random.default_rng(70_000 + s + int(c * 100)))
                pp_g[c].append(ca_score(T, refs))
                pp_r[c].append(ca_score(R, refs))
        tg, trr = np.array(tr_g), np.array(tr_r)
        sem = lambda v: np.std(v) / len(v) ** .5
        print(f"\n== ring rule agrees with T on {aR:.3f} of contexts ==", flush=True)
        print(f"transfer (invariant to c):  genuine {tg.mean():+.3f}({sem(tg):.3f})  "
              f"ring {trr.mean():+.3f}({sem(trr):.3f})  gap {tg.mean()-trr.mean():+.3f}", flush=True)
        print(f"{'c':>5} {'PP_genuine':>11} {'PP_ring':>9} {'PP_gap':>8}  winner", flush=True)
        cross = None
        for c in COORD:
            g, r = np.mean(pp_g[c]), np.mean(pp_r[c])
            if cross is None and r >= g:
                cross = c
            print(f"{c:>5.2f} {g:>+11.3f} {r:>+9.3f} {g-r:>+8.3f}  {'genuine' if g > r else 'RING'}",
                  flush=True)
        print(f"PP crossover (ring >= genuine): c* = {cross if cross is not None else 'none in sweep'}",
              flush=True)
    print("\nREAD: PP needs no ground truth but breaks once enough of its reference pool is ring.",
          flush=True)
    print("Transfer is unaffected by c because it reads a causal delta on exogenous T -- it pays for",
          flush=True)
    print("that with the assumption that T is exogenous and disjoint from the adversary (M5).", flush=True)


if __name__ == "__main__":
    main()
