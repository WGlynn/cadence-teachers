"""
EXP-58: does EXP-45's delayed-credit brain take in what a teacher says (know-4 vs random labels), where the default
memory brain does not (EXP-52..55)? EXP-53's chamber, corrective schedule, seeds, world draws and readings; the brain is
EXP-45's key-door protocol-3 operating point built for 10 inputs. Lessons of 40 and 120 attempts, 24 students per length.
PREDICTION: experiments/EXP-58.md (written before the pilot).

    STUDENTS=3 TAG=pilot python -u EXP-58_content_delayed_credit_brain.py
    STUDENTS=24 WORKERS=4 TAG=full python -u EXP-58_content_delayed_credit_brain.py
"""
import importlib.util, json, os, time
from dataclasses import replace
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("EPISODES", "120")
_spec = importlib.util.spec_from_file_location("e52", os.path.join(HERE, "EXP-52_noesis_lite_null_counterfactual.py"))
E52 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E52)
live_world, per_state, UNSEEN, labeller = E52.live_world, E52.per_state, E52.UNSEEN, E52.labeller

STUDENTS = int(os.environ.get("STUDENTS", 24))
WORKERS = int(os.environ.get("WORKERS", 4))
TAG = os.environ.get("TAG", "full")
LENGTHS = [int(x) for x in os.environ.get("LENGTHS", "40,120").split(",")]
VEST = 20
OURS = dict(modules=(32,), eta=0.1, eta_bias=0.01, lam=0.95, gamma=0.95, eta_critic=5.0,
            working_memory_amplitude=0.3, consolidation=0.25)            # EXP-45's delayed-credit brain


def compose(seed):
    import cadence as cd
    b = cd.Brain.compose(10, 5, modules=OURS["modules"], seed=int(seed), consolidation=OURS["consolidation"],
                         working_memory_amplitude=OURS["working_memory_amplitude"],
                         working_memory_scale=12.0, working_memory_decay=0.2)   # EXP-45's (0.81) composition
    b.basal_ganglia.config = replace(b.basal_ganglia.config, **{k: OURS[k] for k in ("eta", "eta_bias", "lam", "gamma", "eta_critic")})
    return b


def run(job):
    lesson, k = job
    t0 = time.time()
    seed = 5_000_000 + 1000 * lesson + k                     # EXP-53's seed for this student
    out = dict(lesson=lesson, student=k)
    for arm, kind in (("know4", "know-4"), ("random", "random"), ("untaught", None)):
        rng = np.random.default_rng(seed)
        s = compose(seed)
        lab = labeller(kind, np.random.default_rng(seed + 1)) if kind else None
        live_world(s, lesson, rng, label=lab)
        live_world(s, VEST, rng)                             # alone: no arousal genes, so `step` without labels, not `live`
        out[arm] = per_state(s, UNSEEN)
    out["content"] = out["know4"] - out["random"]
    out["secs"] = round(time.time() - t0, 1)
    print(f"  L{lesson:3d} st{k}: know4 {out['know4']:.2f} random {out['random']:.2f} untaught {out['untaught']:.2f} "
          f"content {out['content']:+.2f} ({out['secs']}s)", flush=True)
    return out


def main():
    t0 = time.time()
    ckpt = os.path.join(HERE, f"EXP-58-{TAG}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["lesson"], r["student"]) for r in rows}
    jobs = [(L, k) for k in range(STUDENTS) for L in LENGTHS if (L, k) not in done]
    print(f"EXP-58: {len(jobs)} students to go ({len(done)} done); lengths {LENGTHS}", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as fh:
                    fh.write(json.dumps(r) + "\n")
    sem = lambda x: float(np.std(x, ddof=1) / np.sqrt(len(x))) if len(x) > 1 else 0.0
    print(f"\nEXP-58 summary: {STUDENTS} students per length ({time.time() - t0:.0f}s); per-state accuracy on unseen weather")
    summary = {}
    for L in LENGTHS:
        rs = [r for r in rows if r["lesson"] == L and r["student"] < STUDENTS]
        if not rs:
            continue
        o = {a: float(np.mean([r[a] for r in rs])) for a in ("know4", "random", "untaught")}
        c = [r["content"] for r in rs]
        ku = [r["know4"] - r["untaught"] for r in rs]
        ru = [r["random"] - r["untaught"] for r in rs]
        o.update(n=len(rs), content=float(np.mean(c)), content_sem=sem(c), know4_minus_untaught=float(np.mean(ku)),
                 know4_minus_untaught_sem=sem(ku), random_minus_untaught=float(np.mean(ru)), random_minus_untaught_sem=sem(ru))
        summary[str(L)] = o
        print(f"  lesson {L:3d} n={o['n']:2d}  know-4 {o['know4']:.3f}  random {o['random']:.3f}  untaught {o['untaught']:.3f} | "
              f"content {o['content']:+.3f} (SEM {o['content_sem']:.3f}) | know-4 - untaught {o['know4_minus_untaught']:+.3f} "
              f"(SEM {o['know4_minus_untaught_sem']:.3f}) | random - untaught {o['random_minus_untaught']:+.3f} "
              f"(SEM {o['random_minus_untaught_sem']:.3f})")
    json.dump(dict(rows=rows, summary=summary), open(os.path.join(HERE, f"EXP-58-{TAG}.json"), "w"))


if __name__ == "__main__":
    main()
