"""
EXP-53: does the content of a teacher's labels matter at all, and at what lesson length?

EXP-52: at 40-attempt lessons a teacher that knows all four stages (know-4) was worth no more than one labelling at
random (accuracy .661 vs .648; untaught .46): the student learned from being corrected, not from what it was told. EXP-46's
caregiver (the same know-4 labels) reached .94 at 120 attempts, without a random-label control. Here, paired twins from
the same student seed and world draws: taught by know-4, taught by random labels, untaught; lessons of 40, 120 and 240
attempts; then 20 attempts alone through `live`; per-state greedy accuracy on unseen weather (EXP-48's chamber).
PREDICTION: experiments/EXP-53.md (written before the pilot).

    STUDENTS=24 WORKERS=4 TAG=full python -u EXP-53_does_content_matter.py
"""
import importlib.util, json, os, time
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("EPISODES", "120")
_spec = importlib.util.spec_from_file_location("e52", os.path.join(HERE, "EXP-52_noesis_lite_null_counterfactual.py"))
E52 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E52)
compose, live_world, per_state, UNSEEN, labeller = E52.compose, E52.live_world, E52.per_state, E52.UNSEEN, E52.labeller

STUDENTS = int(os.environ.get("STUDENTS", 24))
WORKERS = int(os.environ.get("WORKERS", 4))
TAG = os.environ.get("TAG", "full")
LENGTHS = [int(x) for x in os.environ.get("LENGTHS", "40,120,240").split(",")]
VEST = 20


def run(job):
    lesson, k = job
    t0 = time.time()
    seed = 5_000_000 + 1000 * lesson + k
    out = dict(lesson=lesson, student=k)
    for arm, kind in (("know4", "know-4"), ("random", "random"), ("untaught", None)):
        rng = np.random.default_rng(seed)
        s = compose(seed)
        lab = labeller(kind, np.random.default_rng(seed + 1)) if kind else None
        live_world(s, lesson, rng, label=lab)
        live_world(s, VEST, rng, call="live")
        out[arm] = per_state(s, UNSEEN)
    out["content"] = out["know4"] - out["random"]
    out["secs"] = round(time.time() - t0, 1)
    print(f"  L{lesson:3d} st{k}: know4 {out['know4']:.2f} random {out['random']:.2f} untaught {out['untaught']:.2f} "
          f"content {out['content']:+.2f} ({out['secs']}s)", flush=True)
    return out


def main():
    t0 = time.time()
    ckpt = os.path.join(HERE, f"EXP-53-{TAG}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["lesson"], r["student"]) for r in rows}
    jobs = [(L, k) for k in range(STUDENTS) for L in LENGTHS if (L, k) not in done]
    print(f"EXP-53: {len(jobs)} students to go ({len(done)} done); lengths {LENGTHS}", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as f:
                    f.write(json.dumps(r) + "\n")
    sem = lambda x: float(np.std(x, ddof=1) / np.sqrt(len(x))) if len(x) > 1 else 0.0
    print(f"\nEXP-53 summary: {STUDENTS} students per length ({time.time() - t0:.0f}s); per-state accuracy on unseen weather")
    summary = {}
    for L in LENGTHS:
        rs = [r for r in rows if r["lesson"] == L and r["student"] < STUDENTS]
        if not rs:
            continue
        o = {a: float(np.mean([r[a] for r in rs])) for a in ("know4", "random", "untaught")}
        c = [r["content"] for r in rs]
        o.update(content=float(np.mean(c)), content_sem=sem(c), n=len(rs))
        summary[str(L)] = o
        print(f"  lesson {L:3d} n={o['n']:2d}  know-4 {o['know4']:.3f}  random {o['random']:.3f}  untaught {o['untaught']:.3f}  "
              f"content (know-4 - random) {o['content']:+.3f} (SEM {o['content_sem']:.3f})")
    json.dump(dict(rows=rows, summary=summary), open(os.path.join(HERE, f"EXP-53-{TAG}.json"), "w"))


if __name__ == "__main__":
    main()
