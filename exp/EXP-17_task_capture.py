"""
EXP-17 — task-pool capture: how much does transfer break if the adversary influences T? (program M5)

Transfer's immunity (EXP-15) assumes the held-out task T is exogenous. Here the scoring task is drawn
from a pool where a fraction q of tasks is adversary-supplied (= the ring's own rule R, which the
adversary can always make its witness ace). We measure the 4 components per instrument seed:
  g_T = transfer(genuine witness T -> task T)   g_R = transfer(genuine -> task R)
  f_T = transfer(fake R -> task T)              f_R = transfer(fake -> task R)
and report expected paired worth E[v_genuine - v_fake] = (1-q)(g_T - f_T) + q(g_R - f_R) vs q.
The q* where it hits 0 is how much task-pool capture the measure tolerates.

Insight is the number, pass or fail.
"""
import os, tempfile, numpy as np
from cadence import Brain, ArousalConfig

K, A = 8, 2
MODULES = (16, 8)
WITNESS_STEPS = 1600
SEEDS = range(12)
TMP = tempfile.gettempdir()
onehot = lambda c: np.eye(K)[[c]]


def make_rule(rng):
    while True:
        r = rng.integers(0, A, size=K)
        if len(set(r.tolist())) > 1:
            return r


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


def main():
    rows = []
    for s in SEEDS:
        rng = np.random.default_rng(100_000 + s)
        T = make_rule(rng)
        R = T.copy()
        R[rng.permutation(K)[: K // 2]] ^= 1      # ring rule: agrees with T on exactly half
        b0 = Brain.compose(inputs=K, actions=A, modules=MODULES, seed=s, arousal=ArousalConfig())
        snap = b0.save(os.path.join(TMP, f"exp17_{s}"))
        bT, bR = eval_on(b0, T), eval_on(b0, R)
        g = Brain.load(snap); ingest(g, T)
        f = Brain.load(snap); ingest(f, R)
        row = (eval_on(g, T) - bT, eval_on(g, R) - bR, eval_on(f, T) - bT, eval_on(f, R) - bR)
        rows.append(row)
        print(f"seed {s:2d}  g_T {row[0]:+.3f} g_R {row[1]:+.3f} f_T {row[2]:+.3f} f_R {row[3]:+.3f}",
              flush=True)
    gT, gR, fT, fR = np.array(rows).T
    print(f"\nmeans  g_T {gT.mean():+.3f}  g_R {gR.mean():+.3f}  f_T {fT.mean():+.3f}  f_R {fR.mean():+.3f}")
    print(f"{'q':>5} {'E[genuine-fake]':>16}")
    qstar = None
    for q in np.linspace(0, 1, 11):
        v = (1 - q) * (gT - fT) + q * (gR - fR)
        print(f"{q:>5.1f} {v.mean():>+16.3f} (SEM {v.std()/len(v)**.5:.3f})")
        if qstar is None and v.mean() <= 0:
            qstar = q
    a, b = (gT - fT).mean(), (gR - fR).mean()
    print(f"exact crossover q* = {a/(a-b):.3f}" if a != b else "no crossover")


if __name__ == "__main__":
    main()
