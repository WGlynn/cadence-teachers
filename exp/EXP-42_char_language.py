"""
EXP-42: can a Cadence brain learn text one character at a time from grades alone?

Will (2026-10-10): "can we make an llm style chat bot with cadence brains" -> the pure-Cadence option: text learned
one character at a time by grading. Cadence's own MANIFESTO makes language a dedicated goal and says "the world
supplies problems, never answers"; grading is exactly that: the brain says a character and hears +1 (right) or
-1 (wrong), never which character was right.

World: Alice's Adventures in Wonderland (Project Gutenberg #11, public domain): chapter 1 to live through, chapter 2
held out. Lowercase a-z, space and period (V = 28); other punctuation becomes a period or a space.
Cadence arms (modules MODULES, arousal on, as teachers.core builds brains):
  w1  : input = the last character (one-hot), every step its own episode (done=True)
  w3  : input = the last 3 characters (3 x 28 multi-hot), every step its own episode
  seq : input = the last character, the life runs on through the text (done=False; an episode ends after a
        period), so the brain's own working trace and memory may carry context past its input
Baselines (same text, same order):
  majority    : always the most common character of chapter 1
  bandit-w1/3 : a tabular epsilon-greedy learner on the same grades (+1/-1 for its own guess only)
  ngram-k     : an online count model over the last k-1 characters that is TOLD the right character after every
                guess (next-character supervision, the LLM training signal): an upper reference, not a fair rival
Protocol: PASSES passes through chapter 1, then one pass through chapter 2 with learning on (a continuing brain does
not stop learning; every character is said before it is graded, so this is prequential accuracy). Also for the
episodic arms: greedy accuracy on chapter 2 from a saved copy (no learning, reset per probe, as Learner.answers).
Sample: 160 greedy characters after the prompt "alice was ".
PREDICTION: experiments/EXP-42.md (written before the run).

    SEEDS=3 PASSES=2 WORKERS=4 TAG=full python -u EXP-42_char_language.py      (LIMIT=600 TAG=smoke for a smoke run)
"""
import json, os, re, sys, tempfile, time, urllib.request
from collections import Counter, defaultdict
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SEEDS = int(os.environ.get("SEEDS", 3))
PASSES = int(os.environ.get("PASSES", 2))
TAG = os.environ.get("TAG", "full")
ARMS = os.environ.get("ARMS", "w1,w3,seq").split(",")
WORKERS = int(os.environ.get("WORKERS", 4))
MODULES = tuple(int(m) for m in os.environ.get("MODULES", "32x16").split("x"))
LIMIT = int(os.environ.get("LIMIT", 0))                # cap characters per chapter (smoke runs)
ALPHA = "abcdefghijklmnopqrstuvwxyz ."
V, IDX = len(ALPHA), {c: i for i, c in enumerate(ALPHA)}
PROMPT, SAMPLE = "alice was ", 160
URL = "https://www.gutenberg.org/cache/epub/11/pg11.txt"


# ---------------- the text ----------------
def clean(t: str) -> str:
    t = t.lower().replace("’", "").replace("‘", "").replace("'", "")
    t = re.sub(r"[!?;:]", ".", t)
    t = re.sub(r"[^a-z. ]+", " ", t)
    t = re.sub(r"\s*\.[\s.]*", ". ", t)
    return re.sub(r" +", " ", t).strip()


def corpus():
    p1, p2 = os.path.join(DATA, "alice-ch1.txt"), os.path.join(DATA, "alice-ch2.txt")
    if not (os.path.exists(p1) and os.path.exists(p2)):
        raw = urllib.request.urlopen(URL, timeout=60).read().decode("utf-8").replace("\r\n", "\n")
        body = raw[re.search(r"CHAPTER I\.\s*\n\s*Down the Rabbit-Hole", raw).start():]
        chapters = re.split(r"CHAPTER [IVXL]+\.", body)[1:]
        os.makedirs(DATA, exist_ok=True)
        for p, ch in ((p1, chapters[0]), (p2, chapters[1])):
            with open(p, "w", encoding="utf-8") as f:
                f.write(clean(ch.split("\n", 2)[-1]) + "\n")      # drop the chapter title line
    a = open(p1, encoding="utf-8").read().strip()
    b = open(p2, encoding="utf-8").read().strip()
    return (a[:LIMIT], b[:max(1, LIMIT // 2)]) if LIMIT else (a, b)


def window(text: str, i: int, n: int) -> np.ndarray:
    """The n characters before position i (spaces before the start), as n stacked one-hots."""
    x = np.zeros((1, n * V))
    for k in range(n):
        j = i - n + k
        x[0, k * V + IDX[text[j] if j >= 0 else " "]] = 1.0
    return x


# ---------------- Cadence ----------------
def run_cadence(job):
    arm, seed, a, b = job
    from cadence import ArousalConfig, Brain
    n, episodic = (3 if arm == "w3" else 1), arm != "seq"
    brain = Brain.compose(inputs=n * V, actions=V, modules=MODULES, seed=10_000 * (seed + 1) + 42,
                          arousal=ArousalConfig())
    reward, done, t0 = None, True, time.time()

    def read(text):
        nonlocal reward, done
        hits = 0
        for i in range(len(text)):
            x = window(text, i, n)
            act = brain.live(x) if reward is None else brain.live(x, reward=reward, done=np.array([done]))
            act = int(np.asarray(act).reshape(-1)[0])
            hits += act == IDX[text[i]]
            reward = np.array([1.0 if act == IDX[text[i]] else -1.0])
            done = episodic or text[i] == "."
        return hits / len(text)

    by_pass = [read(a) for _ in range(PASSES)]
    steps = PASSES * len(a)
    held_live = read(b)
    with tempfile.TemporaryDirectory() as d:
        path = brain.save(os.path.join(d, "b.npz"))
        cp = Brain.load(path)
        greedy = None
        if episodic:
            hits = 0
            for i in range(len(b)):
                cp.reset()
                hits += int(np.asarray(cp.act(window(b, i, n), greedy=True)).reshape(-1)[0]) == IDX[b[i]]
            greedy = hits / len(b)
        cp = Brain.load(path)
        text = PROMPT
        for _ in range(SAMPLE):
            if episodic:
                cp.reset()
                act = cp.act(window(text, len(text), n), greedy=True)
            else:
                act = cp.act(window(text, len(text), n), greedy=True)   # the trace carries on, no reset
            text += ALPHA[int(np.asarray(act).reshape(-1)[0])]
    return dict(arm=arm, seed=seed, modules="x".join(map(str, MODULES)), passes=PASSES, by_pass=by_pass,
                held_live=held_live, held_greedy=greedy, sample=text, train_chars=len(a), held_chars=len(b),
                ms_per_step=round(1000 * (time.time() - t0) / (steps + 2 * len(b)), 2),
                cadence=__import__("cadence").__version__)


# ---------------- baselines ----------------
def majority(a, b):
    top = Counter(a).most_common(1)[0][0]
    return sum(c == top for c in b) / len(b), top


def bandit(n, seed, a, b, eps=0.1, lr=0.3):
    """Tabular epsilon-greedy on the same grades: Q[context][char], +1/-1 for its own guess only."""
    rng, Q = np.random.default_rng(seed), defaultdict(lambda: np.zeros(V))

    def read(text):
        hits = 0
        for i in range(len(text)):
            q = Q[text[max(0, i - n):i].rjust(n)]
            act = int(rng.integers(V)) if rng.random() < eps else int(rng.choice(np.flatnonzero(q == q.max())))
            r = 1.0 if act == IDX[text[i]] else -1.0
            hits += r > 0
            q[act] += lr * (r - q[act])
        return hits / len(text)
    return [read(a) for _ in range(PASSES)], read(b)


def ngram(k, a, b):
    """Online counts over the last k-1 characters, told the right character after each guess (supervised)."""
    counts, glob = defaultdict(Counter), Counter()

    def read(text):
        hits = 0
        for i in range(len(text)):
            c = counts[text[max(0, i - k + 1):i] if k > 1 else ""]
            guess = c.most_common(1)[0][0] if c else (glob.most_common(1)[0][0] if glob else " ")
            hits += guess == text[i]
            c[text[i]] += 1
            glob[text[i]] += 1
        return hits / len(text)
    return [read(a) for _ in range(PASSES)], read(b)


def main():
    t0 = time.time()
    a, b = corpus()
    ckpt = os.path.join(HERE, f"EXP-42-{TAG}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["arm"], r["seed"]) for r in rows}
    jobs = [(arm, s, a, b) for arm in ARMS for s in range(SEEDS) if (arm, s) not in done]
    print(f"EXP-42 text: {len(a)} train / {len(b)} held-out chars; {len(jobs)} Cadence runs to go "
          f"({len(done)} done); modules {MODULES}, passes {PASSES}", flush=True)
    with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs) or 1))) as pool:
        for r in pool.imap_unordered(run_cadence, jobs):
            rows.append(r)
            with open(ckpt, "a") as f:
                f.write(json.dumps(r) + "\n")
            print(f"  {r['arm']:4s} seed {r['seed']}: passes {['%.3f' % x for x in r['by_pass']]} held-out "
                  f"{r['held_live']:.3f} greedy {r['held_greedy'] if r['held_greedy'] is None else round(r['held_greedy'], 3)}"
                  f"  {r['ms_per_step']} ms/step  sample: {r['sample'][len(PROMPT):len(PROMPT) + 60]!r}", flush=True)
    sem = lambda x: float(np.std(x, ddof=1) / np.sqrt(len(x))) if len(x) > 1 else 0.0
    base = dict(majority=majority(a, b)[0])
    for n in (1, 3):
        res = [bandit(n, s, a, b) for s in range(SEEDS)]
        base[f"bandit-w{n}"] = float(np.mean([h for _, h in res]))
    for k in (1, 2, 3, 4):
        base[f"ngram-{k} (supervised)"] = ngram(k, a, b)[1]
    print(f"\nheld-out accuracy (chapter 2, prequential), {SEEDS} seeds  ({time.time() - t0:.0f}s)")
    for arm in ARMS:
        rs = [r for r in rows if r["arm"] == arm and r["seed"] < SEEDS]
        if rs:
            h = [r["held_live"] for r in rs]
            g = [r["held_greedy"] for r in rs if r["held_greedy"] is not None]
            print(f"  cadence-{arm:4s} {np.mean(h):.3f} (SEM {sem(h):.3f})" + (f"   greedy {np.mean(g):.3f}" if g else "")
                  + f"   last train pass {np.mean([r['by_pass'][-1] for r in rs]):.3f}")
    for k, v in base.items():
        print(f"  {k:24s} {v:.3f}")
    for arm in ARMS:
        r = next((r for r in rows if r["arm"] == arm and r["seed"] == 0), None)
        if r:
            print(f"\n  sample cadence-{arm} seed 0: {r['sample']!r}")
    json.dump(dict(rows=rows, baselines=base, train_chars=len(a), held_chars=len(b)),
              open(os.path.join(HERE, f"EXP-42-{TAG}.json"), "w"))


if __name__ == "__main__":
    main()
