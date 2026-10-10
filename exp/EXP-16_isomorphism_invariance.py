"""
EXP-16 — isomorphism-invariance of the transfer measure (program M3).

M3: v(S) = v(phi(S)) for any structure-preserving relabeling phi of everything v may see. Here phi
relabels the CONTEXTS (a permutation of the K sensor indices) and/or the ACTIONS (swap 0<->1),
applied consistently to the witness rule AND the held-out task T. The instrument (the measuring
brain, its random init) is NOT relabeled: it is part of v, not part of S.

Expected honest shape: a single instrument has asymmetric random weights, so v_1(phi S) != v_1(S)
per instance. Invariance can only hold for the instrument-AVERAGED measure v_n (mean over n
instrument seeds). We measure max_phi |v_n(phi S) - v_n(S)| as n grows: if it shrinks ~1/sqrt(n)
the measure is invariant in expectation and the residual is instrument noise; if it plateaus,
something in v reads labels (a real M3 failure).

Usage: python EXP-16_isomorphism_invariance.py <task_index>   (run task indices in parallel)
Insight is the number, pass or fail.
"""
import os, sys, tempfile, numpy as np
from cadence import Brain, ArousalConfig

K, A = 8, 2
MODULES = (16, 8)
WITNESS_STEPS = 1600
INSTRUMENTS = range(8)
TMP = tempfile.gettempdir()
onehot = lambda c: np.eye(K)[[c]]


def make_rule(rng):
    while True:
        r = rng.integers(0, A, size=K)
        if len(set(r.tolist())) > 1:
            return r


def relabel(rule, perm, swap):
    """phi(rule): context k of the new world is context perm[k] of the old; actions optionally swapped."""
    r = rule[perm].copy()
    return (A - 1) - r if swap else r


def eval_on(brain, rule):
    hits = 0
    for ctx in range(K):
        brain.reset()   # #164
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


def transfer(seed, T, W):
    b0 = Brain.compose(inputs=K, actions=A, modules=MODULES, seed=seed, arousal=ArousalConfig())
    snap = b0.save(os.path.join(TMP, f"exp16_{os.getpid()}_{seed}"))
    base = eval_on(b0, T)
    b = Brain.load(snap)
    ingest(b, W)
    return eval_on(b, T) - base


def main(task_idx):
    rng = np.random.default_rng(80_000 + task_idx)
    T = make_rule(rng)
    fake = T.copy()
    fake[rng.permutation(K)[: K // 2]] ^= 1          # agrees with T on exactly half
    perm = np.random.default_rng(90_000 + task_idx).permutation(K)
    PHIS = {"identity": (np.arange(K), False), "ctx-perm": (perm, False),
            "act-swap": (np.arange(K), True), "both": (perm, True)}
    print(f"EXP-16 task {task_idx}  T={T.tolist()}  perm={perm.tolist()}  "
          f"instruments={len(list(INSTRUMENTS))}", flush=True)
    for wname, W in (("genuine", T), ("fake", fake)):
        v = {}
        for pname, (p, sw) in PHIS.items():
            v[pname] = np.array([transfer(s, relabel(T, p, sw), relabel(W, p, sw))
                                 for s in INSTRUMENTS], float)
            print(f"  {wname:8} {pname:9} per-instrument {v[pname].round(3).tolist()}  "
                  f"mean {v[pname].mean():+.3f}", flush=True)
        print(f"  {wname}: max_phi |v_n(phi S) - v_n(S)| by ensemble size n", flush=True)
        for n in (1, 2, 4, 8):
            gaps = [abs(v[p][:n].mean() - v['identity'][:n].mean()) for p in PHIS if p != "identity"]
            print(f"    n={n}: {max(gaps):.3f}", flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
