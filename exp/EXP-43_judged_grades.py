"""
EXP-43: grades that judge the guess. Does a teacher's judgement, instead of the world's right/wrong, let a Cadence
brain learn text from grades alone? (EXP-42 levers 1 + 2: more passes, richer grades.)

EXP-42: hearing only +1 (right) / -1 (wrong), a Cadence brain reached .225 on held-out Alice; told-the-answer counts
reach .291 (bigram) / .502 (4-gram). Part of why: the right/wrong grade is NOISY. Even the best next character is
wrong most of the time, so the best guess and a bad guess both mostly hear -1. A teacher who knows the language can
grade the guess itself ("a good guess here") instead of its luck. The student still never hears which character came.

Teacher: reads the book alongside the student. After grading each guess it is told the character (online counts of
order k with backoff to shorter contexts it has not seen), and it scores a guess by how often that character has
followed this context: the teacher's best = +1, never seen here = -1, linear in between. The score depends only on
the text before the guess, never on the character that came. The teacher's own accuracy (its best guess, prequential)
is the ceiling for a student that learns its judgement exactly.

Grades (all on the student's own guess; never the answer):
  outcome : +1 right, -1 wrong (EXP-42)
  judged  : the teacher's score
  partial : the mean of the two (half for being right, half for a good guess)
Cadence arms (modules MODULES, every step its own episode, seeds as EXP-42):
  <grade>-w1 : input = the last character; teacher order 2 (bigram)
  <grade>-w3 : input = the last 3 characters; teacher order 4
  plain name : Brain.live with arousal on (EXP-42's protocol: learns only while aroused)
  -always    : Brain.step without arousal, learns from every outcome (EXP-39's protocol). Added after the pilot: under
               live, a deterministic grade let the brain go calm (aroused 1-3% of moments) and stop learning while
               wrong ("the calm trap"), so the grade comparison runs on an always-learning brain.
Every arm also runs its order-(n+1) teacher as an observer, so "agree" (the student's guess = the teacher's best) is
printed for every arm: the chain is grade -> reward -> agree -> accuracy.
Baselines: majority; the teachers' own accuracy (ceilings); a tabular epsilon-greedy learner on the same grades
(optimistic start q0 = 1, so a first decent judged score does not freeze it); EXP-42's numbers for continuity.
Protocol: PASSES passes through Alice ch.1, greedy held-out accuracy on ch.2 from a saved copy (no learning) after
the passes in PROBES, then ch.2 with learning on (prequential, the teacher keeps grading). Sample after "alice was ".
PREDICTION: experiments/EXP-43.md (written before the run).

    SEEDS=3 PASSES=6 PROBES=1,3,6 WORKERS=8 TAG=full python -u EXP-43_judged_grades.py     (always-learning arms)
    SEEDS=3 PASSES=3 PROBES=1,3 WORKERS=6 TAG=live ARMS=outcome-w1,partial-w1,judged-w1,judged-w3 python -u ...
    SEEDS=1 PASSES=1 PROBES=1 WORKERS=4 TAG=pilot python -u EXP-43_judged_grades.py       (pilot)
"""
import importlib.util, json, os, tempfile, time
from collections import Counter, defaultdict
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("exp42", os.path.join(HERE, "EXP-42_char_language.py"))
E42 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E42)
ALPHA, V, IDX, PROMPT, SAMPLE = E42.ALPHA, E42.V, E42.IDX, E42.PROMPT, E42.SAMPLE
window, corpus, majority = E42.window, E42.corpus, E42.majority

SEEDS = int(os.environ.get("SEEDS", 3))
PASSES = int(os.environ.get("PASSES", 6))
PROBES = sorted({int(p) for p in os.environ.get("PROBES", "1,3,6").split(",") if int(p) <= PASSES})
TAG = os.environ.get("TAG", "full")
ARMS = os.environ.get("ARMS", "outcome-w1-always,partial-w1-always,judged-w1-always,outcome-w3-always,"
                               "judged-w3-always").split(",")
WORKERS = int(os.environ.get("WORKERS", 8))
MODULES = tuple(int(m) for m in os.environ.get("MODULES", "32x16").split("x"))


# ---------------- the teacher and the grades ----------------
class Teacher:
    """Online counts of order k (told each character after grading), backing off to shorter seen contexts."""

    def __init__(self, k):
        self.k, self.counts = k, defaultdict(Counter)

    @staticmethod
    def _ctx(text, i, m):
        return text[max(0, i - m):i].rjust(m) if m else ""

    def dist(self, text, i):
        for m in range(self.k - 1, -1, -1):
            c = self.counts.get(self._ctx(text, i, m))
            if c:
                return c
        return None

    def best(self, text, i):
        c = self.dist(text, i)
        return IDX[c.most_common(1)[0][0]] if c else IDX[" "]

    def score(self, text, i, a):
        c = self.dist(text, i)
        return 2.0 * c[ALPHA[a]] / max(c.values()) - 1.0 if c else 0.0

    def tell(self, text, i):
        for m in range(self.k):
            self.counts[self._ctx(text, i, m)][text[i]] += 1


def grade(kind, teacher, text, i, act):
    right = 1.0 if act == IDX[text[i]] else -1.0
    if kind == "outcome":
        return right
    judged = teacher.score(text, i, act)
    return judged if kind == "judged" else (right + judged) / 2


def split(arm):
    """'judged-w3' -> ('judged', 3, False); a trailing '-always' learns from every outcome (step, no arousal)."""
    parts = arm.split("-")
    return parts[0], int(parts[1][1:]), parts[-1] == "always"


# ---------------- Cadence ----------------
def run_cadence(job):
    arm, seed, a, b = job
    from cadence import ArousalConfig, Brain
    kind, n, always = split(arm)
    brain = Brain.compose(inputs=n * V, actions=V, modules=MODULES, seed=10_000 * (seed + 1) + 42,
                          arousal=None if always else ArousalConfig())
    move = brain.step if always else brain.live
    teacher, reward, t0 = Teacher(n + 1), None, time.time()

    def read(text):
        nonlocal reward
        hits = agree = 0
        rsum = 0.0
        woke = 0 if always else brain.arousal.moments["aroused"]
        for i in range(len(text)):
            x = window(text, i, n)
            act = move(x) if reward is None else move(x, reward=reward, done=np.array([True]))
            act = int(np.asarray(act).reshape(-1)[0])
            hits += act == IDX[text[i]]
            agree += act == teacher.best(text, i)
            r = grade(kind, teacher, text, i, act)
            rsum += r
            reward = np.array([r])
            teacher.tell(text, i)
        aroused = 1.0 if always else (brain.arousal.moments["aroused"] - woke) / len(text)
        return dict(acc=hits / len(text), agree=agree / len(text), reward=rsum / len(text), aroused=aroused)

    def probe(text):
        with tempfile.TemporaryDirectory() as d:
            cp = Brain.load(brain.save(os.path.join(d, "b.npz")))
            hits = 0
            for i in range(len(text)):
                cp.reset()
                hits += int(np.asarray(cp.act(window(text, i, n), greedy=True)).reshape(-1)[0]) == IDX[text[i]]
            return hits / len(text)

    by_pass, greedy = [], {}
    for p in range(1, PASSES + 1):
        by_pass.append(read(a))
        if p in PROBES:
            greedy[p] = probe(b)
        s = by_pass[-1]
        print(f"    {arm} s{seed} pass {p:2d}: acc {s['acc']:.3f} agree {s['agree']:.3f} reward {s['reward']:+.3f} aroused {s['aroused']:.2f}"
              + (f"  greedy held-out {greedy[p]:.3f}" if p in greedy else ""), flush=True)
    held = read(b)
    with tempfile.TemporaryDirectory() as d:
        cp = Brain.load(brain.save(os.path.join(d, "b.npz")))
        text = PROMPT
        for _ in range(SAMPLE):
            cp.reset()
            text += ALPHA[int(np.asarray(cp.act(window(text, len(text), n), greedy=True)).reshape(-1)[0])]
    steps = PASSES * len(a) + len(b) * (1 + len(PROBES))
    return dict(arm=arm, seed=seed, modules="x".join(map(str, MODULES)), passes=PASSES, by_pass=by_pass,
                greedy={str(k): v for k, v in greedy.items()}, held_live=held["acc"], held_agree=held["agree"],
                sample=text, train_chars=len(a), held_chars=len(b),
                ms_per_step=round(1000 * (time.time() - t0) / steps, 2), cadence=__import__("cadence").__version__)


# ---------------- baselines ----------------
def teacher_accuracy(k, a, b):
    """The teacher's own best guess, prequential: the ceiling for a student that learns its judgement exactly."""
    t = Teacher(k)

    def read(text):
        hits = 0
        for i in range(len(text)):
            hits += t.best(text, i) == IDX[text[i]]
            t.tell(text, i)
        return hits / len(text)
    return [read(a) for _ in range(PASSES)], read(b)


def bandit(kind, n, seed, a, b, eps=0.1, lr=0.3, q0=1.0):
    """Tabular epsilon-greedy on the same grades: Q[context][char], graded for its own guess only."""
    rng, Q, teacher = np.random.default_rng(seed), defaultdict(lambda: np.full(V, q0)), Teacher(n + 1)

    def read(text):
        hits = 0
        for i in range(len(text)):
            q = Q[text[max(0, i - n):i].rjust(n)]
            act = int(rng.integers(V)) if rng.random() < eps else int(rng.choice(np.flatnonzero(q == q.max())))
            hits += act == IDX[text[i]]
            q[act] += lr * (grade(kind, teacher, text, i, act) - q[act])
            teacher.tell(text, i)
        return hits / len(text)
    return [read(a) for _ in range(PASSES)], read(b)


def main():
    t0 = time.time()
    a, b = corpus()
    ckpt = os.path.join(HERE, f"EXP-43-{TAG}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["arm"], r["seed"]) for r in rows}
    jobs = [(arm, s, a, b) for s in range(SEEDS) for arm in ARMS if (arm, s) not in done]
    print(f"EXP-43 text: {len(a)} train / {len(b)} held-out chars; {len(jobs)} Cadence runs to go ({len(done)} done); "
          f"modules {MODULES}, passes {PASSES}, probes {PROBES}", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run_cadence, jobs):
                rows.append(r)
                with open(ckpt, "a") as f:
                    f.write(json.dumps(r) + "\n")
                print(f"  {r['arm']:10s} seed {r['seed']}: held-out {r['held_live']:.3f} greedy {r['greedy']}  "
                      f"{r['ms_per_step']} ms/step  sample: {r['sample'][len(PROMPT):len(PROMPT) + 60]!r}", flush=True)
    sem = lambda x: float(np.std(x, ddof=1) / np.sqrt(len(x))) if len(x) > 1 else 0.0
    base = {"majority": majority(a, b)[0]}
    for k in (2, 4):
        base[f"teacher-{k} (told the answer)"] = teacher_accuracy(k, a, b)[1]
    for kind, n in dict.fromkeys(split(arm)[:2] for arm in ARMS):
        base[f"bandit {kind}-w{n}"] = float(np.mean([bandit(kind, n, s, a, b)[1] for s in range(SEEDS)]))
    print(f"\nheld-out accuracy (Alice ch.2), {SEEDS} seeds, {PASSES} passes  ({time.time() - t0:.0f}s)")
    for arm in ARMS:
        rs = [r for r in rows if r["arm"] == arm and r["seed"] < SEEDS and r["passes"] == PASSES]
        if rs:
            h = [r["held_live"] for r in rs]
            g = {p: np.mean([r["greedy"][str(p)] for r in rs]) for p in PROBES}
            print(f"  cadence {arm:10s} live {np.mean(h):.3f} (SEM {sem(h):.3f})  greedy by pass "
                  + " ".join(f"{p}:{v:.3f}" for p, v in g.items())
                  + f"  agree {np.mean([r['held_agree'] for r in rs]):.3f}"
                  + f"  last pass acc {np.mean([r['by_pass'][-1]['acc'] for r in rs]):.3f}")
    for k, v in base.items():
        print(f"  {k:30s} {v:.3f}")
    for arm in ARMS:
        r = next((r for r in rows if r["arm"] == arm and r["seed"] == 0), None)
        if r:
            print(f"\n  sample {arm} seed 0: {r['sample']!r}")
    json.dump(dict(rows=rows, baselines=base, train_chars=len(a), held_chars=len(b), passes=PASSES),
              open(os.path.join(HERE, f"EXP-43-{TAG}.json"), "w"))


if __name__ == "__main__":
    main()
