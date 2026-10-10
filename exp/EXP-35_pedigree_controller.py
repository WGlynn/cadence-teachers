"""
EXP-35 — the pedigree share as a control dial: fixed values vs a PI controller, with DISCOVERY.

World: K=48 bandit contexts. 8 brains each start knowing 4 (32 known to the network, 16 known to nobody).
Every brain keeps notes (EXP-33 fix: drift-check + rehearse). Each round every brain makes ONE move:
  TEACH    : teach its neediest peer (oracle partner choice, to isolate the share's effect). Pay = student's
             measured gain on the true rule, split over the newly learned items: the item's ORIGIN gets
             share ALPHA, the teacher keeps the rest (teacher == origin keeps all). Budget-balanced.
  DISCOVER : spend the round learning one context it does not know, from the world (D graded trials on the
             true rule); it becomes that item's ORIGIN. No pay up front: it pays later via the pedigree share.
Move choice: each brain keeps a running average of what each move paid it and picks the better one
(epsilon 0.15 exploration), so ALPHA changes behaviour only through pay.
Arms: ALPHA fixed 0 / 0.3 / 0.6 / 0.9, and PI: ALPHA adjusted each round so the share of brains discovering
tracks the share of contexts nobody knows yet (target rule = design choice, stated).
PREDICTION (before running): low ALPHA under-discovers (network stalls near 32/48 = 0.83 + chance on the rest);
high ALPHA over-discovers and spreads slowly; PI matches or beats the best fixed ALPHA.
"""
import os, sys, json, time, importlib.util
import numpy as np
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
N, K, SLICE = 8, 48, 4
M = int(os.environ.get("M", 16))
D = int(os.environ.get("D", 40))
ROUNDS = int(os.environ.get("ROUNDS", 20))
SEEDS = int(os.environ.get("SEEDS", 6))
ARMS = os.environ.get("ARMS", "0.0,0.3,0.6,0.9,PI").split(",")
EPS = 0.15
RULE = np.random.default_rng(4321).integers(0, 2, size=K)


def onehot(c):
    return np.eye(K)[[c]]


class Peer:
    def __init__(self, seed, slice_):
        from cadence import Brain, ArousalConfig
        self.b = Brain.compose(inputs=K, actions=2, modules=(16, 8), seed=seed, arousal=ArousalConfig())
        self.reward = None
        self.known = set(int(c) for c in slice_)
        self.notes = {int(c): int(RULE[c]) for c in slice_}
        self.origin = {int(c): None for c in slice_}          # None = founder knowledge (no pedigree)
        for t in range(len(slice_) * 400):
            c = int(slice_[t % len(slice_)])
            self.live(c, lambda a, c=c: 1.0 if a == RULE[c] else -1.0)

    def live(self, c, judge):
        a = self.b.live(onehot(c)) if self.reward is None else self.b.live(
            onehot(c), reward=self.reward, done=np.array([True]))
        a = int(np.asarray(a).reshape(-1)[0])
        self.reward = np.array([judge(a)])
        return a

    def answers(self):
        import tempfile
        from cadence import Brain
        with tempfile.TemporaryDirectory() as d:
            cp = Brain.load(self.b.save(os.path.join(d, "p.npz")))
        out = []
        for c in range(K):
            cp.reset()
            out.append(int(np.asarray(cp.act(onehot(c), greedy=True)).reshape(-1)[0]))
        return np.array(out)


def run(args):
    arm, seed = args
    rng = np.random.default_rng(2000 + seed)
    perm = rng.permutation(K)
    peers = [Peer(20_000 * (seed + 1) + i, perm[i * SLICE:(i + 1) * SLICE]) for i in range(N)]
    alpha = 0.3 if arm == "PI" else float(arm)
    integ = 0.0
    avg = [{"T": 0.05, "D": 0.05} for _ in range(N)]
    ans = [p.answers() for p in peers]
    acc, alphas, disc_share, net_known = [float(np.mean([np.mean(a == RULE) for a in ans]))], [], [], []
    for r in range(ROUNDS):
        known_any = set().union(*[p.known for p in peers])
        unknown_frac = 1 - len(known_any) / K
        moves = []
        for i in range(N):
            if rng.random() < EPS:
                moves.append("T" if rng.random() < .5 else "D")
            else:
                moves.append("T" if avg[i]["T"] >= avg[i]["D"] else "D")
        earned = [0.0] * N
        for i in range(N):
            P = peers[i]
            if moves[i] == "D":
                cand = [c for c in range(K) if c not in P.known]
                if not cand:
                    continue
                c = int(rng.choice(cand))
                for _ in range(D):
                    P.live(c, lambda a, c=c: 1.0 if a == RULE[c] else -1.0)
                ans[i] = P.answers()
                if ans[i][c] == RULE[c]:
                    P.known.add(c); P.notes[c] = int(RULE[c]); P.origin[c] = i
                continue
            pool = sorted(c for c in P.known if ans[i][c] == P.notes[c])
            if not pool:
                continue
            need = [len(set(pool) - peers[j].known) if j != i else -1 for j in range(N)]
            s = int(rng.choice(np.flatnonzero(np.array(need) == max(need))))
            S = peers[s]
            before = float(np.mean(ans[s] == RULE))
            tans = ans[i]
            for _ in range(M):
                c = int(rng.choice(pool))
                S.live(c, lambda a, c=c: 1.0 if a == tans[c] else -1.0)
            if S.known:
                own = sorted(S.known)
                for _ in range(M // 2):
                    c = int(rng.choice(own))
                    S.live(c, lambda a, c=c: 1.0 if a == S.notes[c] else -1.0)
            ans[s] = S.answers()
            gain = float(np.mean(ans[s] == RULE)) - before
            newly = [c for c in pool if ans[s][c] == tans[c] and c not in S.known]
            for c in newly:
                S.known.add(c); S.notes[c] = int(tans[c])
                S.origin[c] = P.origin.get(c) if P.origin.get(c) is not None else i
            if newly:
                per = gain / len(newly)
                for c in newly:
                    o = P.origin.get(c)
                    if o is None or o == i:
                        earned[i] += per
                    else:
                        earned[i] += (1 - alpha) * per
                        earned[o] += alpha * per
            else:
                earned[i] += gain
        for i in range(N):
            # each brain's estimate of what each move pays: credit this round's earnings to the move it made
            avg[i][moves[i]] = 0.7 * avg[i][moves[i]] + 0.3 * earned[i]
        dshare = moves.count("D") / N
        if arm == "PI":
            err = unknown_frac - dshare
            integ += err
            alpha = float(np.clip(alpha + 0.4 * err + 0.05 * integ, 0.0, 0.95))
        alphas.append(alpha); disc_share.append(dshare)
        net_known.append(len(set().union(*[p.known for p in peers])) / K)
        acc.append(float(np.mean([np.mean(a == RULE) for a in ans])))
    return dict(arm=arm, seed=seed, acc=acc, alpha=alphas, disc=disc_share, net_known=net_known)


def main():
    t0 = time.time()
    jobs = [(a, s) for a in ARMS for s in range(SEEDS)]
    with get_context("spawn").Pool(int(os.environ.get("WORKERS", 6))) as pool:
        res = pool.map(run, jobs)
    print(f"EXP-35 pedigree controller  N={N} K={K} rounds={ROUNDS} seeds={SEEDS} D={D}  ({time.time()-t0:.0f}s)")
    for a in ARMS:
        rs = [r for r in res if r["arm"] == a]
        curves = np.array([r["acc"] for r in rs])
        fin = curves[:, -1]
        auc = curves.mean(1)
        print(f"  alpha {a:4s} final {fin.mean():.3f} (SEM {fin.std(ddof=1)/len(fin)**.5:.3f})  mean-over-time {auc.mean():.3f}  "
              f"network-knows {np.mean([r['net_known'][-1] for r in rs]):.2f}  discovering {np.mean([np.mean(r['disc']) for r in rs]):.2f}"
              + (f"  alpha path {' '.join(f'{x:.2f}' for x in np.mean([r['alpha'] for r in rs], 0)[::4])}" if a == "PI" else ""))
    json.dump(res, open(os.path.join(HERE, "EXP-35.json"), "w"))


if __name__ == "__main__":
    main()
