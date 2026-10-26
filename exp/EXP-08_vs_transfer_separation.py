"""
EXP-08 — v(S) via measurable transfer: does twin-brain ablation separate genuine
from a matched-fake where INTERIOR scoring scored 0.0%?

Context. The V(S) value-measurement paper (unpublished draft) proves interior
(graph/content-structural) scoring is worth-blind: a genuine 4-mind collaboration and a
matched acyclic fake score IDENTICALLY (0.0% separation, wash_sim.rs). Angle 3 of the paper:
if nodes are LEARNING AGENTS, an edge a->b can mean "b ingested a and b's measurable behavior
changed by delta on a held-out task", verified by twin-brain ablation. Transfer is not
worth-blind the way citation is: the consequence is a measured behavioral fact inside b.

This experiment instantiates angle 3 on real Cadence brains and asks the only question that
matters: does the measured transfer delta SEPARATE genuine from matched-fake, i.e. produce
non-zero separation where interior scoring produced zero?

Method (per seed):
  1. compose brain b; snapshot it (byte-identical common ancestor via save/load).
  2. three witnesses, ALL matched on surface stats (step count, context marginals, reward rate):
       genuine      -> experience that teaches the held-out task T (real task info)
       fake_random  -> reward decoupled from (ctx,action), same reward rate (zero task info)
       fake_wrong   -> teaches a DIFFERENT fixed rule T' (coordinated-but-wrong prior)
  3. each witness is ingested by a fresh reload of the SAME snapshot (true twins).
  4. evaluate each resulting twin on T greedily via a save/load clone (held-out, no learning).
  5. transfer_X = acc_X(on T) - acc_baseline(on T);  separation = transfer_genuine - transfer_fake.

Honest limit (stated in the paper, not hidden): this works only because T is EXOGENOUS and
informationally-disjoint from the adversary. A fake that transfers to T had to carry real
T-information -> "faking" collapses into "contributing". We do NOT claim to have built the
exogenous-task oracle; we test whether, GIVEN one, transfer measurement separates.

Insight is the number, pass or fail. A flat "no separation" is a real result (cf. EXP-01).
"""
import os, tempfile, numpy as np
from cadence import Brain, ArousalConfig

K = 8                      # contexts (iter2: raised from 4 -> finer metric, 0.125 quantization)
A = 2                      # actions
MODULES = (16, 8)
WITNESS_STEPS = 1600       # iter2: raised with K so each context is still well-sampled
SEEDS = range(16)          # iter2: 8 -> 16 for a tighter mean
TMP = tempfile.mkdtemp(prefix="exp08_")  # per-process dir: concurrent runs shared exp08_anc_{seed} (fixed 2026-10-25)

onehot = lambda c: np.eye(K)[[c]]


def make_rule(rng):
    """A fixed context->action map. Reject the all-same map (degenerate)."""
    while True:
        r = rng.integers(0, A, size=K)
        if len(set(r.tolist())) > 1:
            return r


def eval_on(brain, rule, tag=None):
    """Held-out greedy accuracy on `rule`. greedy act() with no reward is PURE (probed 2026-10-07:
    clone==direct, stable across passes), so we eval directly — no save/load clone needed."""
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
    """Run a continuing-stream witness of `steps`. reward_fn(ctx, action)->+1/-1.
    Returns the realized +1 rate (so a fake can be matched to it)."""
    reward, pos = None, 0
    for t in range(steps):
        ctx = t % K
        a = brain.live(onehot(ctx)) if reward is None else brain.live(
            onehot(ctx), reward=reward, done=np.array([True]))
        a = int(np.asarray(a).reshape(-1)[0])
        r = reward_fn(ctx, a)
        pos += int(r > 0)
        reward = np.array([float(r)])
    return pos / steps


def run_seed(seed):
    rng = np.random.default_rng(10_000 + seed)
    T = make_rule(rng)                       # exogenous held-out task
    Tp = (A - 1) - T                         # iter2: MAXIMALLY anti-correlated wrong rule
    #                                          (A=2 -> every context disagrees; T'/T overlap = 0,
    #                                           kills the chance-overlap artifact from iter1)

    brain0 = Brain.compose(inputs=K, actions=A, modules=MODULES, seed=seed,
                           arousal=ArousalConfig())
    snap = brain0.save(os.path.join(TMP, f"exp08_anc_{seed}"))
    acc0 = eval_on(brain0, T, f"base_{seed}")      # baseline on the held-out task T

    # genuine: teaches T. record its realized +1 rate to match the fakes.
    bG = Brain.load(snap)
    rateG = ingest(bG, WITNESS_STEPS, lambda c, a: 1.0 if a == int(T[c]) else -1.0)
    accG = eval_on(bG, T, f"gen_{seed}")
    accG_own = eval_on(bG, Tp, f"gen_own_{seed}")  # genuine on T' (should be LOW: it learned T)

    # fake_random: reward independent of (ctx, action), Bernoulli matched to rateG.
    frng = np.random.default_rng(20_000 + seed)
    bFr = Brain.load(snap)
    ingest(bFr, WITNESS_STEPS, lambda c, a: 1.0 if frng.random() < rateG else -1.0)
    accFr = eval_on(bFr, T, f"fr_{seed}")

    # fake_wrong: teaches T' (structured but wrong prior). Evaluated on T (should NOT transfer)
    # AND on its own T' (own-task diagnostic: proves it DID learn, just not T-worth).
    bFw = Brain.load(snap)
    ingest(bFw, WITNESS_STEPS, lambda c, a: 1.0 if a == int(Tp[c]) else -1.0)
    accFw = eval_on(bFw, T, f"fw_{seed}")
    accFw_own = eval_on(bFw, Tp, f"fw_own_{seed}")

    return dict(seed=seed, acc0=acc0, accG=accG, accFr=accFr, accFw=accFw,
                accFw_own=accFw_own, accG_own=accG_own,
                tG=accG - acc0, tFr=accFr - acc0, tFw=accFw - acc0, rateG=rateG)


def main():
    rows = [run_seed(s) for s in SEEDS]
    def col(k): return np.array([r[k] for r in rows], float)
    print(f"EXP-08  v(S) transfer separation   K={K} A={A} modules={MODULES} "
          f"witness={WITNESS_STEPS} seeds={len(rows)}")
    print(f"{'seed':>4} {'acc0':>6} {'accG':>6} {'accFr':>6} {'accFw':>6} "
          f"{'tG':>6} {'tFr':>6} {'tFw':>6} {'Fw_own':>7} {'G_own':>6}")
    for r in rows:
        print(f"{r['seed']:>4} {r['acc0']:>6.2f} {r['accG']:>6.2f} {r['accFr']:>6.2f} "
              f"{r['accFw']:>6.2f} {r['tG']:>+6.2f} {r['tFr']:>+6.2f} {r['tFw']:>+6.2f} "
              f"{r['accFw_own']:>7.2f} {r['accG_own']:>6.2f}")
    tG, tFr, tFw = col('tG'), col('tFr'), col('tFw')
    print("-" * 72)
    print(f"mean transfer  genuine={tG.mean():+.3f} (+-{tG.std()/len(tG)**.5:.3f})  "
          f"fake_random={tFr.mean():+.3f}  fake_wrong={tFw.mean():+.3f}")
    print(f"mean separation  genuine-fake_random={tG.mean()-tFr.mean():+.3f}  "
          f"genuine-fake_wrong={tG.mean()-tFw.mean():+.3f}")
    print(f"baseline acc on T (chance {1/A:.2f}): {col('acc0').mean():.3f}")
    print(f"own-task diagnostic  fake_wrong on T' (its own task)={col('accFw_own').mean():.3f}  "
          f"genuine on T' (not its task)={col('accG_own').mean():.3f}")
    print("  -> if fake_wrong learned T' (high) but gives ~0 transfer to T, worth is TASK-SPECIFIC:")
    print("     learning the wrong thing registers as no worth on the exogenous task. That is the point.")
    # verdict
    fake_leak = max(tFr.mean(), tFw.mean())
    sep = tG.mean() - fake_leak
    print("-" * 72)
    if tG.mean() > 0.15 and sep > 0.15 and fake_leak < 0.10:
        print(f"VERDICT: SEPARATES. genuine transfers (+{tG.mean():.2f}), fakes do not "
              f"(max +{fake_leak:.2f}). Non-zero separation where interior scored 0.0%.")
    elif tG.mean() <= 0.15:
        print(f"VERDICT: INCONCLUSIVE — genuine itself didn't transfer (+{tG.mean():.2f}); "
              f"task not learned in {WITNESS_STEPS} steps. Raise steps/modules or lower K.")
    else:
        print(f"VERDICT: NO CLEAN SEPARATION — fake leaks +{fake_leak:.2f} "
              f"(generic warmup transfers). Measure contaminated; needs tighter control.")


if __name__ == "__main__":
    main()
