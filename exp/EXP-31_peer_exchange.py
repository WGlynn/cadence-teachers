"""
EXP-31 — peer-to-peer, bidirectional teaching vs one-way teaching (Will 2026-10-09: "teaching should be
peer to peer, bidirectional, otherwise it's not realistic or optimal").

N brains (plain Cadence Brain, K=32 bandit). Brain i starts knowing only its slice (K/N contexts), trained
to mastery on it. Each brain keeps a KNOWN set (starts = its slice; grows when a peer teaches it a context
and it ends up agreeing with that peer). A teacher only teaches contexts in its KNOWN set (specialist rule,
EXP-29). A session = M graded steps teacher -> student (+1 if the student's move matches the teacher's
greedy answer, -1 otherwise). Every brain is both student and teacher.
Arms (same number of sessions per round = N):
  RING : brain i teaches brain i+1 (one direction)
  PEER : random pairs, each pair teaches BOTH ways
Measured each round: mean accuracy of all brains on the true rule.
PREDICTION (written before running): PEER reaches high accuracy in clearly fewer rounds than RING
(two-way gossip spreads exponentially, a one-way ring linearly); copy errors may spread less in PEER.
"""
import os, sys, json, time, tempfile
import numpy as np
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
K, A = 32, 2
N = int(os.environ.get("N", 8))
M = int(os.environ.get("M", 16))
ROUNDS = int(os.environ.get("ROUNDS", 12))
SEEDS = int(os.environ.get("SEEDS", 6))
RULE = np.random.default_rng(1234).integers(0, 2, size=K)


def onehot(c):
    return np.eye(K)[[c]]


class Peer:
    def __init__(self, seed, slice_):
        from cadence import Brain, ArousalConfig
        self.b = Brain.compose(inputs=K, actions=A, modules=(16, 8), seed=seed, arousal=ArousalConfig())
        self.reward = None
        self.known = set(slice_)
        for t in range(len(slice_) * 400):
            c = slice_[t % len(slice_)]
            self._live(c, lambda a, c=c: 1.0 if a == RULE[c] else -1.0)

    def _live(self, c, judge):
        a = self.b.live(onehot(c)) if self.reward is None else self.b.live(
            onehot(c), reward=self.reward, done=np.array([True]))
        a = int(np.asarray(a).reshape(-1)[0])
        self.reward = np.array([judge(a)])
        return a

    def answers(self):
        """Greedy answers on all contexts, read from a saved copy (live stream untouched)."""
        from cadence import Brain
        with tempfile.TemporaryDirectory() as d:
            cp = Brain.load(self.b.save(os.path.join(d, "p.npz")))
        out = []
        for c in range(K):
            cp.reset()
            out.append(int(np.asarray(cp.act(onehot(c), greedy=True)).reshape(-1)[0]))
        return np.array(out)


def session(teacher, student, rng):
    if not teacher.known:
        return
    ans = teacher.answers()
    pool = sorted(teacher.known)
    for _ in range(M):
        c = int(rng.choice(pool))
        student._live(c, lambda a, c=c: 1.0 if a == ans[c] else -1.0)
    got = student.answers()
    student.known |= {c for c in pool if got[c] == ans[c]}


def run(args):
    arm, seed = args
    rng = np.random.default_rng(1000 + seed)
    perm = rng.permutation(K)
    peers = [Peer(10_000 * (seed + 1) + i, list(perm[i * K // N:(i + 1) * K // N])) for i in range(N)]
    acc = [float(np.mean([np.mean(p.answers() == RULE) for p in peers]))]
    for r in range(ROUNDS):
        if arm == "RING":
            pairs = [(peers[i], peers[(i + 1) % N]) for i in range(N)]
        else:
            o = rng.permutation(N)
            pairs = []
            for j in range(0, N, 2):
                a, b = peers[o[j]], peers[o[j + 1]]
                pairs += [(a, b), (b, a)]
        for t, s in pairs:
            session(t, s, rng)
        acc.append(float(np.mean([np.mean(p.answers() == RULE) for p in peers])))
    return arm, seed, acc


def main():
    t0 = time.time()
    jobs = [(arm, s) for arm in ("RING", "PEER") for s in range(SEEDS)]
    with get_context("spawn").Pool(int(os.environ.get("WORKERS", 6))) as pool:
        res = pool.map(run, jobs)
    print(f"EXP-31 peer exchange  N={N} K={K} M={M} rounds={ROUNDS} seeds={SEEDS}  ({time.time()-t0:.0f}s)")
    for arm in ("RING", "PEER"):
        curves = np.array([a for ar, s, a in res if ar == arm])
        m = curves.mean(0)
        hit = [next((r for r, v in enumerate(c) if v >= .9), None) for c in curves]
        print(f"  {arm}: mean acc by round " + " ".join(f"{v:.2f}" for v in m))
        print(f"        rounds to 0.90: {hit}")
    json.dump(res, open(os.path.join(HERE, f"EXP-31-M{M}.json"), "w"))


if __name__ == "__main__":
    main()
