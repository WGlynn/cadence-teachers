"""
EXP-46: does Cadence 0.83's episodic memory (Brain.compose(memory_choice=True)) make the default brain learn the
Stone Age chain, on an outside chamber and read state by state?

Upstream's 0.83 table (docs/episodic.md) reports, on its own four-step crafting chain, frozen full-chain success
38.1% -> 98.7% with a caregiver correcting executed mistakes, 9.0% -> 97.8% after 80 episodes alone through `live`, and
9.1% -> 73.2% from reward alone. EXP-45 found that on Stone Age V5's chamber full-chain success is mostly in-attempt search
(a no-knowledge never-repeat searcher finishes .304) and that the default brain learns the chain from no signal (per-state
greedy accuracy .33-.42). This tests the 0.83 claim on V5's chamber (EXP-45's replica, which reproduces V5 per seed) with
the per-state reading beside full-chain success.

Brain: the current default composition, Brain.compose(7, 5, modules=(48, 24), arousal=True) (V5's brain, 0.82's quiet
context), with and without memory_choice=True (its own defaults). Signals (EXP-45 / V5): natural (world reward only),
grade-v5 (V5's guided +-.5), corrective (V5's caregiver labels on executed mistakes). 120 teaching attempts (V5's budget),
then 80 attempts alone through `live` with world reward only (upstream's "alone through live").
Readings on frozen copies, after teaching and after the 80 alone: per-state greedy accuracy (primary), greedy full-chain,
sampled full-chain over 100 attempts. Chance: uniform .121, never-repeat searcher .304.
PREDICTION: experiments/EXP-46.md (written before the pilot).

    SEEDS=12 WORKERS=2 TAG=full python -u EXP-46_episodic_memory_stone_age.py
"""
import importlib.util, json, os, tempfile, time
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("EPISODES", "120")
_spec = importlib.util.spec_from_file_location("e45", os.path.join(HERE, "EXP-45_stone_age_2x2.py"))
E45 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E45)
Chamber, obs, train, attempt, STATES = E45.Chamber, E45.obs, E45.train, E45.attempt, E45.STATES
WOOD, STONE, FIRE, WARM = E45.WOOD, E45.STONE, E45.FIRE, E45.WARM

SEEDS = int(os.environ.get("SEEDS", 12))
WORKERS = int(os.environ.get("WORKERS", 2))
TAG = os.environ.get("TAG", "full")
EVAL = int(os.environ.get("EVAL", 100))
ALONE = int(os.environ.get("ALONE", 80))
MEMORY = [m == "1" for m in os.environ.get("MEMORY", "0,1").split(",")]
SIGNALS = os.environ.get("SIGNALS", "natural,grade-v5,corrective").split(",")


def alone(brain, episodes):
    """Episodes alone through `live`, world reward only, one continuing stream (V5's event order)."""
    c, wins = Chamber(), 0
    a = int(np.asarray(brain.live(c.x())).reshape(-1)[0])
    for _ in range(episodes):
        while True:
            _, r = c.execute(a)
            if c.done:
                wins += c.success
                c = Chamber()
                a = int(np.asarray(brain.live(c.x(), reward=np.array([r]), done=np.array([True]))).reshape(-1)[0])
                break
            a = int(np.asarray(brain.live(c.x(), reward=np.array([r]), done=np.array([False]))).reshape(-1)[0])
    brain.reset()
    return wins / episodes


def read(path):
    import cadence as cd
    b = cd.Brain.load(path)
    rights = [WOOD, STONE, FIRE, WARM]
    ans = []
    for (w, s, f) in STATES:
        b.reset()
        ans.append(int(b.act(obs(w, s, f), greedy=True)[0]))
    acc = float(np.mean([x == r for x, r in zip(ans, rights)]))
    greedy = attempt(cd.Brain.load(path), True, False)
    bs = cd.Brain.load(path)
    sampled = float(np.mean([attempt(bs, False, False) for _ in range(EVAL)]))
    return dict(acc=acc, answers=ans, greedy=bool(greedy), sampled=sampled)


def run(job):
    memory, signal, seed = job
    import cadence as cd
    t0 = time.time()
    brain = cd.Brain.compose(7, 5, modules=(48, 24), seed=seed, arousal=True, memory_choice=memory)
    stats = train(brain, signal)
    with tempfile.TemporaryDirectory() as d:
        taught = read(brain.save(os.path.join(d, "taught.npz")))
        alone_success = alone(brain, ALONE)
        after = read(brain.save(os.path.join(d, "after.npz")))
    row = dict(memory=memory, signal=signal, seed=seed, **stats, taught=taught, alone_train_success=alone_success,
               after=after, secs=round(time.time() - t0, 1), cadence=cd.__version__)
    m = "mem" if memory else "off"
    print(f"  {m} {signal:10s} s{seed}: taught acc {taught['acc']:.2f} greedy {int(taught['greedy'])} sampled "
          f"{taught['sampled']:.2f} | after alone acc {after['acc']:.2f} greedy {int(after['greedy'])} sampled "
          f"{after['sampled']:.2f} | answers {taught['answers']} -> {after['answers']} ({row['secs']}s)", flush=True)
    return row


def main():
    t0 = time.time()
    ckpt = os.path.join(HERE, f"EXP-46-{TAG}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["memory"], r["signal"], r["seed"]) for r in rows}
    jobs = [(m, sg, 42 + s) for s in range(SEEDS) for m in MEMORY for sg in SIGNALS if (m, sg, 42 + s) not in done]
    print(f"EXP-46: {len(jobs)} runs to go ({len(done)} done); memory {MEMORY}; signals {SIGNALS}", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as f:
                    f.write(json.dumps(r) + "\n")
    sem = lambda x: float(np.std(x, ddof=1) / np.sqrt(len(x))) if len(x) > 1 else 0.0
    print(f"\nEXP-46 summary, {SEEDS} seeds ({time.time() - t0:.0f}s). Chance: uniform .121, never-repeat searcher .304")
    summary = {}
    for m in MEMORY:
        for sg in SIGNALS:
            rs = [r for r in rows if r["memory"] == m and r["signal"] == sg and r["seed"] < 42 + SEEDS]
            if not rs:
                continue
            out = {}
            for ph in ("taught", "after"):
                acc = [r[ph]["acc"] for r in rs]
                out[ph] = dict(acc=float(np.mean(acc)), acc_sem=sem(acc), all4=sum(a == 1.0 for a in acc),
                               greedy=sum(r[ph]["greedy"] for r in rs),
                               sampled=float(np.mean([r[ph]["sampled"] for r in rs])),
                               sampled_sem=sem([r[ph]["sampled"] for r in rs]))
            v5seeds = [r["taught"]["sampled"] for r in rs if r["seed"] <= 46]
            out["n"], out["v5_seeds_sampled"] = len(rs), float(np.mean(v5seeds)) if v5seeds else None
            summary[f"{'mem' if m else 'off'}/{sg}"] = out
            for ph in ("taught", "after"):
                o = out[ph]
                print(f"  {'mem' if m else 'off'} {sg:10s} {ph:6s} n={len(rs):2d}  acc {o['acc']:.2f} (SEM {o['acc_sem']:.2f}, "
                      f"all-4 {o['all4']})  greedy solves {o['greedy']}  sampled {o['sampled']:.3f} (SEM {o['sampled_sem']:.3f})")
            if out["v5_seeds_sampled"] is not None:
                print(f"  {'mem' if m else 'off'} {sg:10s} taught sampled on V5's seeds 42-46: {out['v5_seeds_sampled']:.3f}")
    json.dump(dict(rows=rows, summary=summary), open(os.path.join(HERE, f"EXP-46-{TAG}.json"), "w"))


if __name__ == "__main__":
    main()
