"""
EXP-10 — v(S) program M2 step: PER-MIND worth attribution in a mixed multi-mind collaboration.

EXP-08 (M1) separated a genuine single witness from a surface-matched fake. EXP-09 (M4) swept an
aggregate coordinated prior. Neither tested a MULTI-MIND collaboration where some contributors are
genuine and some are fake, nor whether the transfer measure localizes worth to the SPECIFIC genuine
minds (the Shapley / per-contributor property Noesis needs).

Setup. Exogenous held-out task T over K=8 contexts, partitioned into N=4 disjoint BLOCKS (minds), 2
contexts each. A "collaboration" is N minds, each owning one block; mind_i teaches a consistent map
on its block. Interior structure (N nodes, acyclic, each a consistent novel sub-map, disjoint
coverage) is IDENTICAL whether a mind is genuine or fake — an interior scorer cannot tell them apart
(the paper's matched-fake condition at the collaboration level).

A student brain ingests the whole collaboration's interleaved witness, then we measure transfer to T
RESTRICTED TO EACH BLOCK: transfer_block_i = acc_after(block_i) - acc_baseline(block_i). The claim to
test: genuine minds' blocks show positive transfer, fake minds' blocks ~zero/negative, WITHIN THE
SAME collaboration => the measure attributes worth per-mind, not just in aggregate.

Also sweep genuine-fraction f (0..1) for the proportional-worth curve.

Honest scope: this tests ADDITIVE / per-node worth attribution. It does NOT test super-additive
SYNERGY (worth that exists only in the combination, e.g. XOR), which a small bandit brain cannot
cleanly represent — that remains open (M2-synergy). Insight is the number, pass or fail.
"""
import os, tempfile, numpy as np
from cadence import Brain, ArousalConfig

K = 8
A = 2
N_BLOCKS = 4
BLOCK = [list(range(i * 2, i * 2 + 2)) for i in range(N_BLOCKS)]   # [[0,1],[2,3],[4,5],[6,7]]
MODULES = (16, 8)
WITNESS_STEPS = 1200
SEEDS = range(12)
TMP = tempfile.gettempdir()
onehot = lambda c: np.eye(K)[[c]]


def make_rule(rng):
    while True:
        r = rng.integers(0, A, size=K)
        if len(set(r.tolist())) > 1:
            return r


def eval_block(brain, rule, ctxs):
    """Pure greedy accuracy on a subset of contexts (act() probed pure in EXP-08)."""
    # #164 fix (Bernhard): training is 1-step episodes (done=True), so reset before EVERY probe
    # and once after, so eval state never leaks into the next training step. reset() keeps
    # learned params + memory.
    hits = 0
    for c in ctxs:
        brain.reset()
        hits += int(np.asarray(brain.act(onehot(c), greedy=True)).reshape(-1)[0]) == int(rule[c])
    brain.reset()
    return hits / len(ctxs)


def ingest(brain, steps, comp_map):
    """Student lives the collaboration's composite witness: reward = +1 if action matches comp_map."""
    reward = None
    for t in range(steps):
        c = t % K
        a = brain.live(onehot(c)) if reward is None else brain.live(
            onehot(c), reward=reward, done=np.array([True]))
        a = int(np.asarray(a).reshape(-1)[0])
        reward = np.array([1.0 if a == int(comp_map[c]) else -1.0])


def composite_map(T, genuine_blocks):
    """Collaboration map: genuine blocks teach T; fake blocks teach flipped-T on their contexts."""
    M = T.copy()
    for bi in range(N_BLOCKS):
        if bi not in genuine_blocks:
            for c in BLOCK[bi]:
                M[c] = (A - 1) - T[c]
    return M


def run_seed_perblock(seed):
    """f=0.5 mixed collaboration: blocks 0,1 genuine; 2,3 fake. Per-block transfer to T."""
    rng = np.random.default_rng(50_000 + seed)
    T = make_rule(rng)
    b0 = Brain.compose(inputs=K, actions=A, modules=MODULES, seed=seed, arousal=ArousalConfig())
    snap = b0.save(os.path.join(TMP, f"exp10_anc_{seed}"))
    base = [eval_block(b0, T, BLOCK[i]) for i in range(N_BLOCKS)]
    genuine = {0, 1}
    b = Brain.load(snap)
    ingest(b, WITNESS_STEPS, composite_map(T, genuine))
    aft = [eval_block(b, T, BLOCK[i]) for i in range(N_BLOCKS)]
    return dict(seed=seed, genuine=genuine,
                transfer=[aft[i] - base[i] for i in range(N_BLOCKS)])


def run_seed_fsweep(seed, n_genuine):
    rng = np.random.default_rng(50_000 + seed)   # same T as per-block run for this seed
    T = make_rule(rng)
    b0 = Brain.compose(inputs=K, actions=A, modules=MODULES, seed=seed, arousal=ArousalConfig())
    snap = b0.save(os.path.join(TMP, f"exp10f_anc_{seed}"))
    base = eval_block(b0, T, list(range(K)))
    genuine = set(range(n_genuine))     # first n_genuine blocks genuine
    b = Brain.load(snap)
    ingest(b, WITNESS_STEPS, composite_map(T, genuine))
    return eval_block(b, T, list(range(K))) - base


def main():
    print(f"EXP-10  multi-mind worth attribution   K={K} blocks={N_BLOCKS} witness={WITNESS_STEPS} "
          f"seeds={len(list(SEEDS))}", flush=True)

    # --- Per-mind attribution: one mixed collaboration (blocks 0,1 genuine / 2,3 fake) ---
    rows = [run_seed_perblock(s) for s in SEEDS]
    tr = np.array([r["transfer"] for r in rows], float)   # (seeds, 4)
    mean = tr.mean(0); sem = tr.std(0) / len(rows) ** .5
    print("\n[per-mind attribution] collaboration = blocks 0,1 GENUINE, blocks 2,3 FAKE", flush=True)
    print(f"{'block':>6} {'kind':>8} {'mean_transfer':>14} {'SEM':>7}", flush=True)
    for i in range(N_BLOCKS):
        kind = "genuine" if i in {0, 1} else "fake"
        print(f"{i:>6} {kind:>8} {mean[i]:>+14.3f} {sem[i]:>7.3f}", flush=True)
    gen_mean = mean[:2].mean(); fake_mean = mean[2:].mean()
    print(f"  genuine-minds mean transfer = {gen_mean:+.3f} | fake-minds mean = {fake_mean:+.3f} "
          f"| attribution gap = {gen_mean - fake_mean:+.3f}", flush=True)

    # --- Proportional-worth curve: f = n_genuine/N ---
    print("\n[proportional worth] aggregate transfer to T vs #genuine minds", flush=True)
    print(f"{'n_gen':>6} {'f':>5} {'mean_transfer':>14} {'SEM':>7}", flush=True)
    for ng in range(N_BLOCKS + 1):
        v = np.array([run_seed_fsweep(s, ng) for s in SEEDS], float)
        print(f"{ng:>6} {ng/N_BLOCKS:>5.2f} {v.mean():>+14.3f} {v.std()/len(v)**.5:>7.3f}", flush=True)

    print("\nVERDICT key: if genuine-minds transfer >0 and fake-minds ~0/neg within the SAME "
          "collaboration, the measure attributes worth PER-MIND (Shapley-relevant). If the "
          "proportional curve rises with f, aggregate worth tracks genuine fraction.", flush=True)
    print("SCOPE: additive/per-node attribution only; super-additive synergy (XOR) still open.",
          flush=True)


if __name__ == "__main__":
    main()
