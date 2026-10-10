"""
EXP-29 — can a student beat each of its teachers? (knowledge GROWS, not just copies)

K=32 bandit (EXP-26 harness). Teacher A trained only on contexts 0..15, teacher B only on 16..31:
each is right on its half, ~chance on the other (full-rule acc ~0.75).
A student gets M graded steps from EACH teacher (interleaved, focus 0 = random contexts).
  (a) SPECIALISTS  : each teacher only teaches contexts in its own half
  (b) OVERCONFIDENT: each teacher teaches any context, incl. the half it only guesses
  (c) solo-A       : only teacher A, its own half  (reference: one teacher's ceiling)
PREDICTION (written before running): (a) student ~1.0 > each teacher (~0.75); (b) no better than a
teacher (contradictions on the unknown halves); (c) ~0.75. If (a) >> (b), knowing the limits of your
own knowledge is a teaching skill.
WINDOW: M swept 32/64/128 per teacher.
"""
import os, sys, json, time, importlib.util
import numpy as np
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
STUDENTS = int(os.environ.get("STUDENTS", 8))
BUDGETS = [int(x) for x in os.environ.get("BUDGETS", "32,64,128").split(",")]


def e26():
    spec = importlib.util.spec_from_file_location("e26", os.path.join(HERE, "EXP-26_tutor_focus.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


RULE = np.random.default_rng(1234).integers(0, 2, size=32)
HALF = {"A": list(range(0, 16)), "B": list(range(16, 32))}


def train_half(m, seed, ctxs):
    b = m.make(seed)
    reward = None
    for t in range(len(ctxs) * 600):
        c = ctxs[t % len(ctxs)]
        a = b.live(m.onehot(c)) if reward is None else b.live(m.onehot(c), reward=reward, done=np.array([True]))
        a = int(np.asarray(a).reshape(-1)[0])
        reward = np.array([1.0 if a == RULE[c] else -1.0])
    return b


def teachers_job(_):
    m = e26()
    out = {}
    for name, seed in (("A", 811), ("B", 812)):
        b = train_half(m, seed, HALF[name])
        g = m.greedy_all(b)
        out[name] = dict(answers=g.tolist(), own=float(np.mean(g[HALF[name]] == RULE[HALF[name]])),
                         full=float(np.mean(g == RULE)))
    return out


def student_job(args):
    arm, M, s, T = args
    m = e26()
    rng = np.random.default_rng(60_000 + s)
    st = m.make(70_000 + s)
    plan = [("A", c) for c in range(M)] + ([("B", c) for c in range(M)] if arm != "soloA" else [])
    order = rng.permutation(len(plan))
    reward = None
    for i in order:
        who = plan[i][0]
        pool = HALF[who] if arm in ("spec", "soloA") else list(range(32))
        c = int(rng.choice(pool))
        a = st.live(m.onehot(c)) if reward is None else st.live(m.onehot(c), reward=reward, done=np.array([True]))
        a = int(np.asarray(a).reshape(-1)[0])
        reward = np.array([1.0 if a == T[who]["answers"][c] else -1.0])
    st.live(m.onehot(0), reward=reward, done=np.array([True]))
    return arm, M, s, float(np.mean(m.greedy_all(st) == RULE))


def main():
    t0 = time.time()
    with get_context("spawn").Pool(int(os.environ.get("WORKERS", 3))) as pool:
        T = pool.map(teachers_job, [0])[0]
        print(f"teachers: A own-half {T['A']['own']:.2f} full {T['A']['full']:.2f} | "
              f"B own-half {T['B']['own']:.2f} full {T['B']['full']:.2f}  ({time.time()-t0:.0f}s)", flush=True)
        jobs = [(arm, M, s, T) for M in BUDGETS for arm in ("spec", "over", "soloA") for s in range(STUDENTS)]
        res = pool.map(student_job, jobs)
    print(f"EXP-29 two partial teachers  students={STUDENTS}  ({time.time()-t0:.0f}s)")
    for M in BUDGETS:
        row = []
        for arm in ("spec", "over", "soloA"):
            v = np.array([r[3] for r in res if r[0] == arm and r[1] == M])
            row.append(f"{arm} {v.mean():.3f} (SEM {v.std(ddof=1)/len(v)**.5:.3f})")
        print(f"  M={M:3d}/teacher   " + "   ".join(row))
    json.dump(dict(teachers={k: {kk: vv for kk, vv in v.items()} for k, v in T.items()}, res=res),
              open(os.path.join(HERE, "EXP-29.json"), "w"))


if __name__ == "__main__":
    main()
