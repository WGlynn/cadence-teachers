"""
EXP-26 — a teaching skill invisible to doing: FOCUS on the student's current mistakes.

Task: K-context bandit (EXP-08 harness, plain Cadence Brain), A=2, a fixed rule T.
Teacher: a Cadence brain that has learned T (passes 100%). Every teacher can DO the task equally.
Teaching: M graded steps. Each step the teacher picks a context; the student acts (`live`, so it
explores and learns); the teacher pays +1 if the student's action matches the teacher's own
greedy answer, -1 otherwise.
Strategy gene `focus` in [0,1]: with prob focus, pick among contexts the student currently gets
WRONG (teacher re-checks the student every CHECK steps); otherwise uniform random.
Pilot question: does child accuracy after M steps depend on focus? (If not, no teaching trait.)
"""
import os, sys, json, time
import numpy as np
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
K, A = int(os.environ.get("K", 32)), 2
MODULES = (16, 8)
M = int(os.environ.get("M", 128))
CHECK = 8
FOCI = [float(f) for f in os.environ.get("FOCI", "0,0.25,0.5,0.75,1").split(",")]
STUDENTS = int(os.environ.get("STUDENTS", 8))


def onehot(c):
    return np.eye(K)[[c]]


def greedy_all(b):
    out = []
    for c in range(K):
        b.reset()
        out.append(int(np.asarray(b.act(onehot(c), greedy=True)).reshape(-1)[0]))
    b.reset()
    return np.array(out)


def make(seed):
    from cadence import Brain, ArousalConfig
    return Brain.compose(inputs=K, actions=A, modules=MODULES, seed=seed, arousal=ArousalConfig())


def train_teacher(seed, rule):
    b = make(seed)
    reward = None
    for t in range(K * 200):
        c = t % K
        a = b.live(onehot(c)) if reward is None else b.live(onehot(c), reward=reward, done=np.array([True]))
        a = int(np.asarray(a).reshape(-1)[0])
        reward = np.array([1.0 if a == rule[c] else -1.0])
    return b


def teach(student, answers, focus, rng):
    reward = None
    wrong = list(range(K))
    for t in range(M):
        if t % CHECK == 0:          # check a saved COPY so the live student's pending feedback survives
            import tempfile
            from cadence import Brain
            with tempfile.TemporaryDirectory() as d:
                g = greedy_all(Brain.load(student.save(os.path.join(d, "s.npz"))))
            wrong = [c for c in range(K) if g[c] != answers[c]]
        if wrong and rng.random() < focus:
            c = int(rng.choice(wrong))
        else:
            c = int(rng.integers(K))
        a = student.live(onehot(c)) if reward is None else student.live(
            onehot(c), reward=reward, done=np.array([True]))
        a = int(np.asarray(a).reshape(-1)[0])
        reward = np.array([1.0 if a == answers[c] else -1.0])


def job(args):
    focus, s = args
    rng = np.random.default_rng(1234)
    rule = rng.integers(0, A, size=K)
    if os.environ.get("TEACHER"):          # pilot under the real run's conditions (EXP-27 founders)
        from cadence import Brain
        teacher = Brain.load(os.environ["TEACHER"])
    else:
        teacher = train_teacher(777, rule)
    answers = greedy_all(teacher)
    tacc = float(np.mean(answers == rule))
    st = make(40_000 + s)
    base = float(np.mean(greedy_all(st) == rule))
    teach(st, answers, focus, np.random.default_rng(50_000 + s))
    return focus, s, tacc, base, float(np.mean(greedy_all(st) == rule))


def main():
    t0 = time.time()
    jobs = [(f, s) for f in FOCI for s in range(STUDENTS)]
    with get_context("spawn").Pool(int(os.environ.get("WORKERS", 6))) as pool:
        res = pool.map(job, jobs)
    print(f"EXP-26 tutor focus  K={K} M={M} students={STUDENTS}  teacher acc {res[0][2]:.2f}  ({time.time()-t0:.0f}s)")
    for f in FOCI:
        r = [x for x in res if x[0] == f]
        acc = np.array([x[4] for x in r]); base = np.array([x[3] for x in r])
        print(f"  focus {f:.2f}: child acc {acc.mean():.3f} (SEM {acc.std(ddof=1)/len(acc)**.5:.3f})  base {base.mean():.3f}")
    json.dump(dict(K=K, M=M, res=res), open(os.path.join(HERE, f"EXP-26-K{K}-M{M}{'-T' if os.environ.get('TEACHER') else ''}.json"), "w"))


if __name__ == "__main__":
    main()
