"""
EXP-33 — why do peer networks plateau (~0.78-0.84) and what fixes it?

World = EXP-31 PEER (random pairs, both ways, specialist rule). Each brain keeps NOTES: for every context
in its known set, the answer it had when it learned it (own slice: the true answer it mastered; taught
items: the teacher's answer). Notes are an external record (like a notebook), not inside the brain.
Variants:
  base      : EXP-31 PEER
  rehearse  : after each lesson the student does M/2 self-practice steps on random items of its known set,
              graded against its own notes
  drift     : a teacher only teaches items where its CURRENT answer still matches its notes
  both      : rehearse + drift
  big       : base with a brain twice as large (modules (32,16))
Also logged: forgetting = share of a student's previously-correct known items it gets wrong after a lesson.
PREDICTION (before running): rehearse+drift lifts the plateau toward 0.95; if only `big` helps, the limit was
capacity, not forgetting.
"""
import os, sys, json, time, importlib.util
import numpy as np
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
N, K = 8, 32
M = int(os.environ.get("M", 16))
ROUNDS = int(os.environ.get("ROUNDS", 16))
SEEDS = int(os.environ.get("SEEDS", 6))
VARIANTS = os.environ.get("VARIANTS", "base,rehearse,drift,both,big").split(",")


def e31():
    spec = importlib.util.spec_from_file_location("e31", os.path.join(HERE, "EXP-31_peer_exchange.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def run(args):
    var, seed = args
    m = e31()
    from cadence import Brain, ArousalConfig
    RULE = m.RULE
    if var == "big":
        orig = m.Peer.__init__

        def big_init(self, seed_, slice_):
            self.b = Brain.compose(inputs=K, actions=2, modules=(32, 16), seed=seed_, arousal=ArousalConfig())
            self.reward = None
            self.known = set(slice_)
            for t in range(len(slice_) * 400):
                c = slice_[t % len(slice_)]
                self._live(c, lambda a, c=c: 1.0 if a == RULE[c] else -1.0)
        m.Peer.__init__ = big_init
    rng = np.random.default_rng(1000 + seed)
    perm = rng.permutation(K)
    peers = [m.Peer(10_000 * (seed + 1) + i, list(perm[i * K // N:(i + 1) * K // N])) for i in range(N)]
    notes = [{int(c): int(RULE[c]) for c in p.known} for p in peers]
    rehearse = var in ("rehearse", "both")
    drift = var in ("drift", "both")
    ans = [p.answers() for p in peers]
    acc = [float(np.mean([np.mean(a == RULE) for a in ans]))]
    forget = []
    for r in range(ROUNDS):
        o = rng.permutation(N)
        pairs = []
        for j in range(0, N, 2):
            pairs += [(o[j], o[j + 1]), (o[j + 1], o[j])]
        for t, s in pairs:
            T, S = peers[t], peers[s]
            pool = sorted(c for c in T.known if (not drift or ans[t][c] == notes[t][c]))
            if not pool:
                continue
            before_ok = [c for c in S.known if ans[s][c] == notes[s][c]]
            tans = ans[t]
            for _ in range(M):
                c = int(rng.choice(pool))
                S._live(c, lambda a, c=c: 1.0 if a == tans[c] else -1.0)
            if rehearse and S.known:
                own = sorted(S.known)
                for _ in range(M // 2):
                    c = int(rng.choice(own))
                    S._live(c, lambda a, c=c: 1.0 if a == notes[s][c] else -1.0)
            after = S.answers()
            ans[s] = after
            if before_ok:
                forget.append(float(np.mean([after[c] != notes[s][c] for c in before_ok])))
            for c in pool:
                if after[c] == tans[c] and c not in S.known:
                    S.known.add(c)
                    notes[s][c] = int(tans[c])
        acc.append(float(np.mean([np.mean(a == RULE) for a in ans])))
    return var, seed, acc, float(np.mean(forget)) if forget else 0.0


def main():
    t0 = time.time()
    jobs = [(v, s) for v in VARIANTS for s in range(SEEDS)]
    with get_context("spawn").Pool(int(os.environ.get("WORKERS", 3))) as pool:
        res = pool.map(run, jobs)
    print(f"EXP-33 forgetting fix  N={N} K={K} M={M} rounds={ROUNDS} seeds={SEEDS}  ({time.time()-t0:.0f}s)")
    for v in VARIANTS:
        rs = [r for r in res if r[0] == v]
        curves = np.array([r[2] for r in rs])
        fin = curves[:, -1]
        print(f"  {v:9s} final {fin.mean():.3f} (SEM {fin.std(ddof=1)/len(fin)**.5:.3f})  forgetting/lesson "
              f"{np.mean([r[3] for r in rs]):.3f}  curve " + " ".join(f"{x:.2f}" for x in curves.mean(0)[::2]))
    json.dump(res, open(os.path.join(HERE, "EXP-33.json"), "w"))


if __name__ == "__main__":
    main()
