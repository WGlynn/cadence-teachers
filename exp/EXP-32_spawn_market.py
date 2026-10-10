"""
EXP-32 — the full $SPAWN market, minimal: peer-to-peer, bidirectional, partner choice learned from pay,
pay along every teaching edge, pedigree share up the provenance chain, budget-balanced.

World = EXP-31 (N Cadence brains, K=32 bandit, each starts knowing one slice; specialist rule: a teacher
only teaches contexts in its KNOWN set; every brain is student AND teacher).
Each round every brain picks ONE student via its own CHOOSER (a Cadence Brain, 1 constant input,
N actions = peer index; choosing itself = abstain). A session = M graded steps on contexts from the
teacher's known set. Payment = the student's measured gain on the TRUE rule (acc after - acc before,
read from copies). Pay split along provenance: each taught context carries its ORIGIN brain; for the
contexts the student newly learned, a share ALPHA of their pay goes to the origin, the rest to the
teacher. Total paid == total measured gain (budget-balanced). Chooser reward = what that brain earned
this round (teaching pay + pedigree pay), scaled.
Arms (N sessions per round, same as EXP-31): CHOOSE (learned partner choice) vs PEER (random partner).
PREDICTION (written before running): CHOOSE spreads knowledge faster than PEER and at least as fast as
EXP-31 RING; choosers learn to pick students who lack their knowledge; payout == measured gain.
Honest scope: WHAT to teach is still random within the known set; only WHO to teach is learned.
"""
import os, sys, json, time, importlib.util
import numpy as np
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
N = int(os.environ.get("N", 8))
M = int(os.environ.get("M", 16))
ROUNDS = int(os.environ.get("ROUNDS", 12))
SEEDS = int(os.environ.get("SEEDS", 6))
ALPHA = float(os.environ.get("ALPHA", 0.3))
SCALE = 20.0


def e31():
    spec = importlib.util.spec_from_file_location("e31", os.path.join(HERE, "EXP-31_peer_exchange.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def run(args):
    arm, seed = args
    m = e31()
    from cadence import Brain
    K, RULE = m.K, m.RULE
    rng = np.random.default_rng(1000 + seed)
    perm = rng.permutation(K)
    peers = [m.Peer(10_000 * (seed + 1) + i, list(perm[i * K // N:(i + 1) * K // N])) for i in range(N)]
    origin = [{int(c): i for c in p.known} for i, p in enumerate(peers)]   # context -> origin brain
    choosers = [Brain.compose(1, N, modules=(16,), seed=7_000 + 100 * seed + i) for i in range(N)]
    ch_reward = [None] * N
    x = np.ones((1, 1))
    ans = [p.answers() for p in peers]
    acc = [float(np.mean([np.mean(a == RULE) for a in ans]))]
    earned_total, gain_total, lacks_hits, picks = 0.0, 0.0, 0, 0
    events, brain_acc, wallet = [], [[float(np.mean(a == RULE)) for a in ans]], [0.0] * N
    for r in range(ROUNDS):
        earned = [0.0] * N
        for t in range(N):
            if arm == "CHOOSE":
                fb = {} if ch_reward[t] is None else {"reward": [ch_reward[t]], "done": [True]}
                s = int(choosers[t].step(x, **fb)[0])
            else:
                s = int(rng.integers(N))
            if s == t or not peers[t].known:
                events.append(dict(round=r, teacher=t, student=None))
                continue
            picks += 1
            lacks_hits += int(len(peers[t].known - peers[s].known) > 0)
            before = ans[s]
            tans = ans[t]
            pool = sorted(peers[t].known)
            for _ in range(M):
                c = int(rng.choice(pool))
                peers[s]._live(c, lambda a, c=c: 1.0 if a == tans[c] else -1.0)
            after = peers[s].answers()
            ans[s] = after
            gain = float(np.mean(after == RULE) - np.mean(before == RULE))
            gain_total += gain
            newly = [c for c in pool if after[c] == tans[c] and c not in peers[s].known]
            peers[s].known |= set(newly)
            for c in newly:
                origin[s][c] = origin[t].get(c, t)
            # pay = measured gain, split teacher / origins (pedigree) over the newly learned contexts
            before_pay = list(earned)
            if newly and gain != 0:
                per = gain / len(newly)
                for c in newly:
                    o = origin[t].get(c, t)
                    if o == t:
                        earned[t] += per
                    else:
                        earned[t] += (1 - ALPHA) * per
                        earned[o] += ALPHA * per
            else:
                earned[t] += gain
            events.append(dict(round=r, teacher=t, student=s, gain=round(gain, 4), learned=len(newly),
                               pay={str(i): round(earned[i] - before_pay[i], 4) for i in range(N)
                                    if abs(earned[i] - before_pay[i]) > 1e-9}))
        earned_total += sum(earned)
        wallet = [w + e for w, e in zip(wallet, earned)]
        brain_acc.append([float(np.mean(a == RULE)) for a in ans])
        ch_reward = [SCALE * e for e in earned]
        acc.append(float(np.mean([np.mean(a == RULE) for a in ans])))
    return dict(arm=arm, seed=seed, acc=acc, paid=earned_total, gain=gain_total,
                lacks_rate=lacks_hits / max(1, picks), picks=picks, events=events,
                brain_acc=brain_acc, wallet=wallet, slices=[sorted(int(c) for c in perm[i * K // N:(i + 1) * K // N]) for i in range(N)])


def main():
    t0 = time.time()
    jobs = [(arm, s) for arm in ("CHOOSE", "PEER") for s in range(SEEDS)]
    with get_context("spawn").Pool(int(os.environ.get("WORKERS", 6))) as pool:
        res = pool.map(run, jobs)
    print(f"EXP-32 $SPAWN market  N={N} M={M} rounds={ROUNDS} seeds={SEEDS} alpha={ALPHA}  ({time.time()-t0:.0f}s)")
    for arm in ("CHOOSE", "PEER"):
        rs = [r for r in res if r["arm"] == arm]
        curves = np.array([r["acc"] for r in rs])
        hit = [next((i for i, v in enumerate(c) if v >= .9), None) for c in curves]
        print(f"  {arm}: mean acc by round " + " ".join(f"{v:.2f}" for v in curves.mean(0)))
        print(f"        rounds to 0.90 {hit}  sessions {np.mean([r['picks'] for r in rs]):.0f}  "
              f"taught-a-peer-who-lacked-something {np.mean([r['lacks_rate'] for r in rs]):.2f}  "
              f"paid/gain {sum(r['paid'] for r in rs):.3f}/{sum(r['gain'] for r in rs):.3f}")
    json.dump(res, open(os.path.join(HERE, "EXP-32.json"), "w"))


if __name__ == "__main__":
    main()
