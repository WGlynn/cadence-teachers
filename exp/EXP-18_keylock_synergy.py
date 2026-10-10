"""
EXP-18 — M2-SYNERGY via a key/lock (secret-share) witness pair.

Why this design. iter7 (EXP-12/14) found the Cadence creature does not learn XOR on factored inputs
(RL or supervised, shallow or deep). Pure synergy (v(A)=v(B)=0, v(AB)>0) needs an XOR-like
interaction SOMEWHERE. If the learner cannot host it, it must live in the data channel. The
canonical PID synergy object is a two-share secret: neither share carries information, the pair
carries all of it.

Construction (per seed, K contexts, held-out task T, per-step random pad s_t in {+1,-1}):
  A (lock)  contributes masked rewards  m_t = r_t * s_t      (r_t = +1 if action == T[ctx] else -1)
  B (key)   contributes the pad         s_t
  pipeline: a coalition's reward stream is the product of whatever shares it holds:
      {}   -> no witness (transfer 0 by definition)
      {A}  -> reward m_t            (pad unknown; uniform-sign noise wrt r)
      {B}  -> reward s_t            (pure noise)
      {AB} -> reward m_t * s_t = r_t  (the real lesson)
  fake key B' : independent pad s'_t.  {AB'} -> r_t s_t s'_t = noise.
  partial key B_p : pad correct w.p. p, else flipped.  {AB_p} -> r_t with sign-noise, corr = 2p-1.

What is measured. v(S) = greedy acc on T after ingesting S's stream - acc of a twin fed an equal-length
pure-noise stream (reference zero point; the untouched twin's prior is biased, see EXP-16).
Then three credit rules on the 2-player game:
  solo     phi_A = v(A) - v({})                   (single-witness ablation: under-credits)
  LOO      phi_A = v(AB) - v(B)                   (leave-one-out twin ablation: over-credits, sums 2x)
  Shapley  phi_A = 1/2[v(A)] + 1/2[v(AB)-v(B)]     (efficient: phi_A + phi_B = v(AB))

Honest scope: the synergy is BUILT INTO THE DATA, not composed by the learner. This tests the
attribution machinery on a super-additive game with real learners; it does NOT show a Cadence brain
composing two skills (that is Cadence #115 / the XOR wall, still open).
"""
import os, sys, tempfile, numpy as np
from cadence import Brain, ArousalConfig

K = 8
A = 2
MODULES = (16, 8)
WITNESS_STEPS = 1600
SEEDS = range(int(sys.argv[1]) if len(sys.argv) > 1 else 12)
P_SWEEP = (0.5, 0.625, 0.75, 0.875)
TMP = tempfile.gettempdir()

onehot = lambda c: np.eye(K)[[c]]


def make_rule(rng):
    while True:
        r = rng.integers(0, A, size=K)
        if len(set(r.tolist())) > 1:
            return r


def eval_on(brain, rule):
    # #164: reset before every probe and once after.
    hits = 0
    for ctx in range(K):
        brain.reset()
        hits += int(np.asarray(brain.act(onehot(ctx), greedy=True)).reshape(-1)[0]) == int(rule[ctx])
    brain.reset()
    return hits / K


def ingest(brain, reward_fn):
    """reward_fn(t, ctx, action) -> +1/-1. Continuing stream, 1-step episodes."""
    reward = None
    for t in range(WITNESS_STEPS):
        ctx = t % K
        a = brain.live(onehot(ctx)) if reward is None else brain.live(
            onehot(ctx), reward=reward, done=np.array([True]))
        a = int(np.asarray(a).reshape(-1)[0])
        reward = np.array([float(reward_fn(t, ctx, a))])


def run_seed(seed):
    rng = np.random.default_rng(30_000 + seed)
    T = make_rule(rng)
    pad = rng.choice([-1, 1], size=WITNESS_STEPS)          # B's key
    fake = rng.choice([-1, 1], size=WITNESS_STEPS)         # B' wrong key
    noise = rng.choice([-1, 1], size=WITNESS_STEPS)        # reference witness (zero point)
    flips = rng.random(WITNESS_STEPS)                      # for partial keys

    brain0 = Brain.compose(inputs=K, actions=A, modules=MODULES, seed=seed, arousal=ArousalConfig())
    snap = brain0.save(os.path.join(TMP, f"exp18_anc_{seed}"))
    acc0 = eval_on(brain0, T)
    # Zero point = twin that ingested an equal-length uninformative stream (EXP-16 lesson: the
    # untouched twin's prior is not a fair baseline; any training regresses it toward chance).
    bN = Brain.load(snap)
    ingest(bN, lambda t, c, a: noise[t])
    accN = eval_on(bN, T)

    r = lambda c, a: 1 if a == int(T[c]) else -1
    streams = {
        "A":   lambda t, c, a: r(c, a) * pad[t],                 # lock alone
        "B":   lambda t, c, a: pad[t],                           # key alone
        "AB":  lambda t, c, a: r(c, a) * pad[t] * pad[t],        # lock + key
        "Bf":  lambda t, c, a: fake[t],                          # fake key alone
        "ABf": lambda t, c, a: r(c, a) * pad[t] * fake[t],       # lock + fake key
    }
    for p in P_SWEEP:
        key_p = np.where(flips < p, pad, -pad)
        streams[f"AB_{p}"] = (lambda kp: lambda t, c, a: r(c, a) * pad[t] * kp[t])(key_p)

    v = {}
    for name, fn in streams.items():
        b = Brain.load(snap)
        ingest(b, fn)
        v[name] = eval_on(b, T) - accN
    v["acc0"] = acc0
    v["accN"] = accN
    return v


def credits(vA, vB, vAB):
    return dict(solo=(vA, vB), loo=(vAB - vB, vAB - vA),
                shap=(0.5 * vA + 0.5 * (vAB - vB), 0.5 * vB + 0.5 * (vAB - vA)))


def main():
    rows = []
    for s in SEEDS:
        rows.append(run_seed(s))
        v = rows[-1]
        print(f"seed {s:2d}  acc0 {v['acc0']:.3f}  accN {v['accN']:.3f}  v(A) {v['A']:+.3f}  v(B) {v['B']:+.3f}  "
              f"v(AB) {v['AB']:+.3f}  v(B') {v['Bf']:+.3f}  v(AB') {v['ABf']:+.3f}", flush=True)
    col = lambda k: np.array([r[k] for r in rows], float)
    m = lambda k: col(k).mean()
    se = lambda k: col(k).std(ddof=1) / len(rows) ** .5
    n = len(rows)
    print("-" * 72)
    print(f"EXP-18 key/lock synergy  K={K} modules={MODULES} witness={WITNESS_STEPS} seeds={n}")
    for k in ("A", "B", "AB", "Bf", "ABf"):
        print(f"  v({k:3s}) = {m(k):+.3f}  (SEM {se(k):.3f})")
    syn = col("AB") - col("A") - col("B")
    print(f"  synergy v(AB)-v(A)-v(B) = {syn.mean():+.3f} (SEM {syn.std(ddof=1)/n**.5:.3f})")
    print("credit rules (mean over seeds; genuine key):")
    c = credits(m("A"), m("B"), m("AB"))
    for rule, (pa, pb) in c.items():
        print(f"  {rule:5s} phi_A {pa:+.3f}  phi_B {pb:+.3f}  sum {pa+pb:+.3f}  vs v(AB) {m('AB'):+.3f}")
    cf = credits(m("A"), m("Bf"), m("ABf"))
    print("credit rules with FAKE key B':")
    for rule, (pa, pb) in cf.items():
        print(f"  {rule:5s} phi_A {pa:+.3f}  phi_B' {pb:+.3f}")
    print("partial key sweep (pad correct w.p. p; sign-correlation 2p-1):")
    for p in P_SWEEP:
        k = f"AB_{p}"
        print(f"  p={p:<5}  corr {2*p-1:+.2f}  v(AB_p) {m(k):+.3f} (SEM {se(k):.3f})")
    print(f"  p=1.0    corr +1.00  v(AB)   {m('AB'):+.3f}")


if __name__ == "__main__":
    main()
