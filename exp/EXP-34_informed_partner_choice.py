"""
EXP-34 — can brains learn WHOM to teach when they can see who needs it?

EXP-32's chooser saw a constant input (blind), so it barely learned to pick needy peers (61% vs 58%).
World = EXP-32 market (pay = student's measured gain on the true rule, budget-balanced).
Each round every brain picks one student. Arms:
  RANDOM   : any peer
  ORACLE   : the peer lacking the most of the teacher's known set (upper reference)
  INFORMED : a Cadence chooser whose INPUT is, for each peer, the share of the teacher's known set that peer
             lacks (peers advertise what they know); it learns from its pay which signal to follow
PREDICTION (before running): ORACLE clearly beats RANDOM; INFORMED closes most of the gap.
"""
import os, sys, json, time, importlib.util
import numpy as np
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
N, K = 8, 32
M = int(os.environ.get("M", 16))
ROUNDS = int(os.environ.get("ROUNDS", 16))
SEEDS = int(os.environ.get("SEEDS", 6))
SCALE = 20.0


def e31():
    spec = importlib.util.spec_from_file_location("e31", os.path.join(HERE, "EXP-31_peer_exchange.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def run(args):
    arm, seed = args
    m = e31()
    from cadence import Brain
    RULE = m.RULE
    rng = np.random.default_rng(1000 + seed)
    perm = rng.permutation(K)
    peers = [m.Peer(10_000 * (seed + 1) + i, list(perm[i * K // N:(i + 1) * K // N])) for i in range(N)]
    choosers = [Brain.compose(N, N, modules=(16,), seed=8_000 + 100 * seed + i) for i in range(N)]
    rew = [None] * N
    FIX = os.environ.get("FIX") == "1"       # iter21 fix: notes + drift-check + rehearse (EXP-33 'both')
    notes = [{int(c): int(RULE[c]) for c in p.known} for p in peers]
    ans = [p.answers() for p in peers]
    acc = [float(np.mean([np.mean(a == RULE) for a in ans]))]
    needy_pick = []
    for r in range(ROUNDS):
        earned = [0.0] * N
        for t in range(N):
            T = peers[t]
            if not T.known:
                continue
            need = np.array([0.0 if j == t else len(T.known - peers[j].known) / len(T.known) for j in range(N)])
            if arm == "RANDOM":
                s = int(rng.choice([j for j in range(N) if j != t]))
            elif arm == "ORACLE":
                best = np.flatnonzero(need == need.max())
                s = int(rng.choice(best))
            else:
                fb = {} if rew[t] is None else {"reward": [rew[t]], "done": [True]}
                s = int(choosers[t].step(need[None, :], **fb)[0])
                if s == t:
                    continue
            needy_pick.append(float(need[s] >= need.max() - 1e-9))
            before = float(np.mean(ans[s] == RULE))
            tans = ans[t]
            pool = sorted(c for c in T.known if not FIX or tans[c] == notes[t][c])
            if not pool:
                continue
            for _ in range(M):
                c = int(rng.choice(pool))
                peers[s]._live(c, lambda a, c=c: 1.0 if a == tans[c] else -1.0)
            if FIX and peers[s].known:
                own = sorted(peers[s].known)
                for _ in range(M // 2):
                    c = int(rng.choice(own))
                    peers[s]._live(c, lambda a, c=c: 1.0 if a == notes[s][c] else -1.0)
            after = peers[s].answers()
            ans[s] = after
            earned[t] += float(np.mean(after == RULE)) - before
            for c in pool:
                if after[c] == tans[c] and c not in peers[s].known:
                    peers[s].known.add(c)
                    notes[s][c] = int(tans[c])
        rew = [SCALE * e for e in earned]
        acc.append(float(np.mean([np.mean(a == RULE) for a in ans])))
    return arm, seed, acc, float(np.mean(needy_pick)) if needy_pick else 0.0


def main():
    t0 = time.time()
    jobs = [(a, s) for a in ("RANDOM", "ORACLE", "INFORMED") for s in range(SEEDS)]
    with get_context("spawn").Pool(int(os.environ.get("WORKERS", 3))) as pool:
        res = pool.map(run, jobs)
    print(f"EXP-34 informed partner choice  N={N} K={K} M={M} rounds={ROUNDS} seeds={SEEDS}  ({time.time()-t0:.0f}s)")
    for a in ("RANDOM", "ORACLE", "INFORMED"):
        rs = [r for r in res if r[0] == a]
        curves = np.array([r[2] for r in rs])
        fin = curves[:, -1]
        print(f"  {a:8s} final {fin.mean():.3f} (SEM {fin.std(ddof=1)/len(fin)**.5:.3f})  picked-the-neediest "
              f"{np.mean([r[3] for r in rs]):.2f}  curve " + " ".join(f"{x:.2f}" for x in curves.mean(0)[::2]))
    json.dump(res, open(os.path.join(HERE, f"EXP-34{'-fix' if os.environ.get('FIX') == '1' else ''}.json"), "w"))


if __name__ == "__main__":
    main()
