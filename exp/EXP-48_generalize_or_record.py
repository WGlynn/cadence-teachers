"""
EXP-48: does 0.83's episodic memory GENERALIZE the Stone Age chain to situations it was never taught, or RECORD the
taught ones?

EXP-46 taught and tested on the same four chain states, so a brain that records the caregiver's answers scores the same as
one that learned the rule (the Noesis "answer key" condition: transfer is not teaching when the test overlaps the lesson).
Here every observation also carries three weather bits that have nothing to do with the chain, fixed for an attempt.
Teaching attempts draw the weather from 4 of the 8 combinations; the test reads all four chain states under the other 4,
never seen in teaching. Every single bit value is seen in teaching; only the combinations are new. A brain that learned
"inventory -> action" ignores the weather; a brain that keyed records on the whole situation meets four new situations.

Chamber: EXP-45's V5 replica (strict order, 5 actions, 10 decisions, +2 / -1), observation = V5's 7 inputs + 3 weather
bits (10 inputs). Brain: Brain.compose(10, 5, modules=(48, 24), arousal=True), with and without memory_choice=True.
Signals: corrective (V5's caregiver) and natural (world reward only). 120 teaching attempts (EXP-46). Readings on frozen
copies: per-state greedy accuracy under the 4 SEEN weathers and under the 4 UNSEEN weathers (16 situations each), and
sampled full-chain success over 100 attempts under unseen weather.
PREDICTION: experiments/EXP-48.md (written before the pilot).

    SEEDS=12 WORKERS=2 TAG=full python -u EXP-48_generalize_or_record.py
"""
import importlib.util, json, os, time
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("EPISODES", "120")
_spec = importlib.util.spec_from_file_location("e45", os.path.join(HERE, "EXP-45_stone_age_2x2.py"))
E45 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E45)
WOOD, STONE, FIRE, WARM = E45.WOOD, E45.STONE, E45.FIRE, E45.WARM
GUIDED, AUTONOMOUS = E45.GUIDED, E45.AUTONOMOUS

SEEDS = int(os.environ.get("SEEDS", 12))
EPISODES = int(os.environ.get("EPISODES", 120))
WORKERS = int(os.environ.get("WORKERS", 2))
TAG = os.environ.get("TAG", "full")
EVAL = int(os.environ.get("EVAL", 100))
MEMORY = [m == "1" for m in os.environ.get("MEMORY", "0,1").split(",")]
SIGNALS = os.environ.get("SIGNALS", "corrective,natural").split(",")
SEEN = [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)]       # even parity: every bit value appears, combos differ
UNSEEN = [(0, 0, 1), (0, 1, 0), (1, 0, 0), (1, 1, 1)]
STATES = E45.STATES
RIGHTS = [WOOD, STONE, FIRE, WARM]


class WeatherChamber(E45.Chamber):
    def __init__(self, weather):
        super().__init__()
        self.weather = weather

    def x(self):
        return np.concatenate([E45.obs(self.w, self.s, self.f, self.warmth), np.array([self.weather], dtype=float)], axis=1)


def x_of(state, weather):
    w, s, f = state
    return np.concatenate([E45.obs(w, s, f), np.array([weather], dtype=float)], axis=1)


def train(brain, signal, rng):
    """EXP-45's continuing-life loop (V5's event order) with a weather drawn from SEEN for every attempt."""
    c, g = WeatherChamber(SEEN[rng.integers(4)]), 0
    a = int(brain.step(c.x())[0])
    wins = 0
    for _ in range(EPISODES):
        while True:
            guided = (g % (GUIDED + AUTONOMOUS)) < GUIDED
            right = c.right()
            ok, world = c.execute(a)
            r = world
            teacher = np.array([right]) if (signal == "corrective" and guided and not ok and not c.done) else None
            g += 1
            if c.done:
                wins += c.success
                c = WeatherChamber(SEEN[rng.integers(4)])
                a = int(brain.step(c.x(), reward=np.array([r]), done=np.array([True]))[0])
                break
            a = int(brain.step(c.x(), reward=np.array([r]), done=np.array([False]), teacher=teacher)[0])
    brain.reset()
    return wins / EPISODES


def per_state(b, weathers):
    hits = []
    for wx in weathers:
        for st, right in zip(STATES, RIGHTS):
            b.reset()
            hits.append(int(b.act(x_of(st, wx), greedy=True)[0]) == right)
    return float(np.mean(hits))


def sampled_unseen(b, rng):
    ok = 0
    for i in range(EVAL):
        b.reset()
        c = WeatherChamber(UNSEEN[i % 4])
        while not c.done:
            c.execute(int(b.act(c.x(), greedy=False)[0]))
        ok += c.success
    return ok / EVAL


def run(job):
    memory, signal, seed = job
    import cadence as cd
    t0 = time.time()
    rng = np.random.default_rng(1000 + seed)
    brain = cd.Brain.compose(10, 5, modules=(48, 24), seed=seed, arousal=True, memory_choice=memory)
    train_success = train(brain, signal, rng)
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        path = brain.save(os.path.join(d, "b.npz"))
        seen = per_state(cd.Brain.load(path), SEEN)
        unseen = per_state(cd.Brain.load(path), UNSEEN)
        sampled = sampled_unseen(cd.Brain.load(path), rng)
    row = dict(memory=memory, signal=signal, seed=seed, train_success=train_success, seen=seen, unseen=unseen,
               sampled_unseen=sampled, secs=round(time.time() - t0, 1), cadence=cd.__version__)
    print(f"  {'mem' if memory else 'off'} {signal:10s} s{seed}: seen {seen:.2f} unseen {unseen:.2f} "
          f"sampled-unseen {sampled:.2f} train {train_success:.2f} ({row['secs']}s)", flush=True)
    return row


def main():
    t0 = time.time()
    ckpt = os.path.join(HERE, f"EXP-48-{TAG}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["memory"], r["signal"], r["seed"]) for r in rows}
    jobs = [(m, sg, 42 + s) for s in range(SEEDS) for m in MEMORY for sg in SIGNALS if (m, sg, 42 + s) not in done]
    print(f"EXP-48: {len(jobs)} runs to go ({len(done)} done); memory {MEMORY}; signals {SIGNALS}", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as f:
                    f.write(json.dumps(r) + "\n")
    sem = lambda x: float(np.std(x, ddof=1) / np.sqrt(len(x))) if len(x) > 1 else 0.0
    print(f"\nEXP-48 summary, {SEEDS} seeds ({time.time() - t0:.0f}s). Per-state greedy accuracy under seen / unseen weather")
    summary = {}
    for m in MEMORY:
        for sg in SIGNALS:
            rs = [r for r in rows if r["memory"] == m and r["signal"] == sg and r["seed"] < 42 + SEEDS]
            if not rs:
                continue
            gap = [r["seen"] - r["unseen"] for r in rs]
            o = dict(n=len(rs), seen=float(np.mean([r["seen"] for r in rs])), seen_sem=sem([r["seen"] for r in rs]),
                     unseen=float(np.mean([r["unseen"] for r in rs])), unseen_sem=sem([r["unseen"] for r in rs]),
                     gap=float(np.mean(gap)), gap_sem=sem(gap),
                     sampled_unseen=float(np.mean([r["sampled_unseen"] for r in rs])))
            summary[f"{'mem' if m else 'off'}/{sg}"] = o
            print(f"  {'mem' if m else 'off'} {sg:10s} n={o['n']:2d}  seen {o['seen']:.2f} (SEM {o['seen_sem']:.2f})  "
                  f"unseen {o['unseen']:.2f} (SEM {o['unseen_sem']:.2f})  gap {o['gap']:+.2f} (SEM {o['gap_sem']:.2f})  "
                  f"sampled-unseen {o['sampled_unseen']:.3f}")
    json.dump(dict(rows=rows, summary=summary), open(os.path.join(HERE, f"EXP-48-{TAG}.json"), "w"))


if __name__ == "__main__":
    main()
