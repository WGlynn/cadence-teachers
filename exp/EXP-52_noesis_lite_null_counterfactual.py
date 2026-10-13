"""
EXP-52: Noesis-lite v1.1. Priced against a NULL contribution of the same form (a random-label teacher) instead of no
teacher, does the market price fakes at zero and pay genuine teachers by how much they know?

EXP-49 (BOUNDARY): against an untaught twin, a random-label teacher earned +.18 (random labels knock a stuck student
loose), fakes took .285 of pay, and pay did not follow skill (Spearman .05; skill varied only loosely). Changes here:
(1) the counterfactual twin is taught by a random-label teacher at the same kind of moments (the form-matched null); the
untaught twin is also run, so EXP-49's measure is reproduced in the same runs; (2) skill is set directly: a know-k teacher
labels the right action at the k stages it knows (a random subset per lesson) and a random action elsewhere, k = 1..4;
(3) 12 students per teacher per seed block, each lesson replicated on an independent student.
Chamber, lesson, vesting and reading as EXP-49 (EXP-48's weather chamber, 40-attempt lessons under seen weather, 20
attempts alone through `live`, per-state greedy accuracy under unseen weather).
PREDICTION: experiments/EXP-52.md (written before the pilot).

    SEEDS=3 STUDENTS=12 WORKERS=4 TAG=full python -u EXP-52_noesis_lite_null_counterfactual.py
"""
import importlib.util, json, os, time
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("EPISODES", "120")
_spec = importlib.util.spec_from_file_location("e49", os.path.join(HERE, "EXP-49_noesis_lite_market.py"))
E49 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E49)
compose, live_world, per_state, UNSEEN = E49.compose, E49.live_world, E49.per_state, E49.UNSEEN

SEEDS = int(os.environ.get("SEEDS", 3))
STUDENTS = int(os.environ.get("STUDENTS", 12))
WORKERS = int(os.environ.get("WORKERS", 4))
TAG = os.environ.get("TAG", "full")
LESSON, VEST = E49.LESSON, E49.VEST
TEACHERS = ["know-1", "know-2", "know-3", "know-4", "random", "wrong-chain", "echo"]


def labeller(kind, rng):
    if kind.startswith("know-"):
        k = int(kind.split("-")[1])
        known = set(rng.choice(4, size=k, replace=False).tolist())
        return lambda c, a: c.right() if c.right() in known else int(rng.integers(5))
    if kind == "random":
        return lambda c, a: int(rng.integers(5))
    if kind == "wrong-chain":
        return lambda c, a: (c.right() + 1) % 4
    if kind == "echo":
        return lambda c, a: int(a)
    raise ValueError(kind)


def twins(kind, student_seed):
    """Three twins from the same student seed and world draws: taught by `kind`, by the random-label null, untaught."""
    out = {}
    for arm, lab_kind in (("taught", kind), ("null", "random"), ("untaught", None)):
        rng = np.random.default_rng(student_seed)
        s = compose(student_seed)
        lab = labeller(lab_kind, np.random.default_rng(student_seed + (1 if arm == "taught" else 2))) if lab_kind else None
        live_world(s, LESSON, rng, label=lab)
        live_world(s, VEST, rng, call="live")
        out[arm] = per_state(s, UNSEEN)
    out["vs_null"] = out["taught"] - out["null"]
    out["vs_none"] = out["taught"] - out["untaught"]
    return out


def run(job):
    seed_block, kind, k = job
    t0 = time.time()
    base = 3_000_000 * (seed_block + 1) + 1000 * TEACHERS.index(kind) + 10 * k
    a, b = twins(kind, base), twins(kind, base + 5)
    row = dict(seed_block=seed_block, teacher=kind, student=k, first=a, second=b, secs=round(time.time() - t0, 1))
    print(f"  b{seed_block} {kind:12s} st{k}: vs null {a['vs_null']:+.2f}/{b['vs_null']:+.2f}  vs none "
          f"{a['vs_none']:+.2f}/{b['vs_none']:+.2f} ({row['secs']}s)", flush=True)
    return row


def settle(rows, key, bar):
    """Pay per lesson under a counterfactual: finalized if both replicates exceed the bar; pay = mean worth."""
    pay = {}
    for r in rows:
        w1, w2 = r["first"][key], r["second"][key]
        pay.setdefault(r["teacher"], []).append(max(0.0, (w1 + w2) / 2) if (w1 > bar and w2 > bar) else 0.0)
    return pay


def main():
    t0 = time.time()
    ckpt = os.path.join(HERE, f"EXP-52-{TAG}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["seed_block"], r["teacher"], r["student"]) for r in rows}
    jobs = [(m, kind, k) for m in range(SEEDS) for k in range(STUDENTS) for kind in TEACHERS if (m, kind, k) not in done]
    print(f"EXP-52: {len(jobs)} lessons to go ({len(done)} done); lesson {LESSON}, vest {VEST}", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as f:
                    f.write(json.dumps(r) + "\n")
    rows = [r for r in rows if r["seed_block"] < SEEDS and r["student"] < STUDENTS]
    print(f"\nEXP-52 summary: {SEEDS} blocks x {STUDENTS} students x {len(TEACHERS)} teachers ({time.time() - t0:.0f}s)")
    summary = {}
    for key in ("vs_null", "vs_none"):
        pay = settle(rows, key, E49.FINAL_BAR)
        total = sum(sum(v) for v in pay.values()) or 1.0
        print(f"  counterfactual: {key}")
        summary[key] = {}
        for kind in TEACHERS:
            w = [x for r in rows if r["teacher"] == kind for x in (r["first"][key], r["second"][key])]
            o = dict(worth=float(np.mean(w)), sem=float(np.std(w, ddof=1) / np.sqrt(len(w))), n=len(w),
                     pay_share=float(sum(pay.get(kind, [])) / total))
            summary[key][kind] = o
            print(f"    {kind:12s} worth {o['worth']:+.3f} (SEM {o['sem']:.3f}, n={o['n']})  pay share {o['pay_share']:.3f}")
        kw = [(int(r["teacher"].split("-")[1]), x) for r in rows if r["teacher"].startswith("know-")
              for x in (r["first"][key], r["second"][key])]
        a, b = np.array(kw, dtype=float).T
        ra, rb = a.argsort().argsort(), b.argsort().argsort()
        rho = float(np.corrcoef(ra, rb)[0, 1])
        summary[key]["spearman_k"] = rho
        print(f"    Spearman(worth, k) over know-k lessons: {rho:.2f} (n={len(kw)})")
    json.dump(dict(rows=rows, summary=summary), open(os.path.join(HERE, f"EXP-52-{TAG}.json"), "w"))


if __name__ == "__main__":
    main()
