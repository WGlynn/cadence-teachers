"""
EXP-62g: EXP-62f on a task the cross-family brain cannot solve alone. EXP-62f's instruments, teachers, readings and
verdict (imported from its script, unchanged), plus one knob: the decision budget per attempt (EXP-45's
MAX_DECISIONS, 10 by default). A sweep over budgets on untaught students picks the budget by a rule fixed before it.
PRE-REGISTRATION: experiments/EXP-62g.md (written before any data).

    TAG=sweep WORKERS=4 python -u EXP-62g_budget_cross_family.py                      untaught D1 + A, budgets 10..4
    TAG=pilot BUDGET=<sweep pick> STUDENTS=3 WORKERS=4 python -u EXP-62g_budget_cross_family.py
    TAG=full BUDGET=<sweep pick> STUDENTS=48 LESSON=<80|160> WORKERS=4 python -u EXP-62g_budget_cross_family.py
"""
import importlib.util, json, os, time
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("e62f", os.path.join(HERE, "EXP-62f_cross_family_order.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)                           # also installs 62f's know-early / know-late labeller
E62 = F.E62
E45 = E62.E48.E45                                     # the chamber module whose MAX_DECISIONS every attempt reads
RIGHTS = F.RIGHTS
LATE = {RIGHTS[2], RIGHTS[3]}

TAG = os.environ.get("TAG", "full")
STUDENTS = int(os.environ.get("STUDENTS", 48))
WORKERS = int(os.environ.get("WORKERS", 4))
LESSON = int(os.environ.get("LESSON", 80))
BUDGET = int(os.environ.get("BUDGET", 10))
SEED_BASE = {"sweep": 7_280_000, "pilot": 7_290_000}.get(TAG, 7_200_000)
SWEEP_BUDGETS = (10, 8, 6, 5, 4)
SWEEP_STUDENTS = 6
SWEEP_BAR = 0.60                                      # pick: largest budget with untaught D1 mean <= this
CEILING = 0.90                                        # pilot: any instrument's untaught mean >= this -> stop


def set_budget(b):
    E45.MAX_DECISIONS = int(b)
    c = E62.E48.WeatherChamber(E62.E48.SEEN[0])     # self-check: b wrong actions end an attempt, not fewer
    wrong = next(a for a in range(5) if a != c.right())
    for i in range(b):
        assert not c.done, f"attempt ended after {i} of {b} decisions"
        c.execute(wrong)
    assert c.done, f"attempt still open after {b} decisions"


def late_labels(arm):
    return sum(1 for right, _, _ in arm["labels"] if right in LATE)


def run(job):
    inst, k, budget = job
    import cadence as cd
    set_budget(budget)
    E62.compose = F.compose_for(inst)
    t0 = time.time()
    seed = SEED_BASE + k
    if TAG == "sweep":
        arms = {"untaught": E62.twin(seed, LESSON, None, None)}
    else:
        arms = {"null": E62.twin(seed, LESSON, "random", seed + 2), "untaught": E62.twin(seed, LESSON, None, None)}
        for kind in F.TEACHERS:
            arms[kind] = E62.twin(seed, LESSON, kind, seed + 1)
    for a in arms.values():
        a["late_labels"] = late_labels(a)
    out = dict(instrument=inst, student=k, seed=seed, lesson=LESSON, budget=budget, arms=arms,
               secs=round(time.time() - t0, 1), cadence=cd.__version__)
    print(f"  B{budget:2d} {inst} st{k:2d}: " + " ".join(f"{t} {a['acc']:.2f}" for t, a in arms.items())
          + f" ({out['secs']}s)", flush=True)
    return out


def sweep_pick(rows):
    o = {}
    for b in SWEEP_BUDGETS:
        o[b] = {inst: float(np.mean([r["arms"]["untaught"]["acc"] for r in rows
                                     if r["budget"] == b and r["instrument"] == inst]))
                for inst in ("D1", "A")}
    ok = [b for b in SWEEP_BUDGETS if o[b]["D1"] <= SWEEP_BAR]
    return o, (max(ok) if ok else None)


def main():
    t0 = time.time()
    ckpt = os.path.join(HERE, f"EXP-62g-{TAG}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    if TAG == "sweep":
        want = [(i, k, b) for b in SWEEP_BUDGETS for k in range(SWEEP_STUDENTS) for i in ("D1", "A")]
    else:
        rows = [r for r in rows if r["lesson"] == LESSON and r["budget"] == BUDGET]
        want = [(i, k, BUDGET) for k in range(STUDENTS) for i in F.INSTRUMENTS]
    done = {(r["instrument"], r["student"], r["budget"]) for r in rows}
    jobs = [j for j in want if j not in done]
    print(f"EXP-62g [{TAG}]: lesson {LESSON}, budget {BUDGET if TAG != 'sweep' else SWEEP_BUDGETS}; {len(jobs)} jobs "
          f"to go ({len(done)} done); seeds {SEED_BASE}+", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as fh:
                    fh.write(json.dumps(r) + "\n")
    print(f"\nEXP-62g [{TAG}] summary ({time.time() - t0:.0f}s), lesson {LESSON}")
    if TAG == "sweep":
        means, pick = sweep_pick(rows)
        for b, m in means.items():
            print(f"  budget {b:2d}: untaught D1 {m['D1']:.3f} | untaught A {m['A']:.3f} (A not in the rule)")
        print(f"  sweep rule (largest budget with untaught D1 <= {SWEEP_BAR}): "
              + (f"BUDGET={pick}" if pick else "none -> EXP-62g stops after the sweep"))
        json.dump(dict(untaught_means=means, pick=pick), open(os.path.join(HERE, "EXP-62g-sweep.json"), "w"))
        return
    o = F.analyse(rows)
    F.report(o)
    by = {}
    for r in rows:
        for arm, a in r["arms"].items():
            by.setdefault(r["instrument"], {}).setdefault(arm, []).append(a["late_labels"])
    o["late_labels"] = {i: {arm: float(np.mean(v)) for arm, v in arms.items()} for i, arms in by.items()}
    o["untaught_acc"] = {i: float(np.mean([r["arms"]["untaught"]["acc"] for r in rows if r["instrument"] == i]))
                         for i in F.INSTRUMENTS}
    for i, arms in o["late_labels"].items():
        print(f"  [{i}] mean late labels (stages 3-4) per arm: "
              + "  ".join(f"{a} {v:.1f}" for a, v in arms.items()))
    print(f"  untaught accuracy: {o['untaught_acc']}")
    o["budget"] = BUDGET
    if TAG == "pilot":
        ceil = [i for i, v in o["untaught_acc"].items() if v >= CEILING]
        low = [i for i, v in o["instruments"].items() if v["worth"]["know-4"][0] < 0.05]
        if ceil:
            print(f"  pilot rule: untaught >= {CEILING} for {ceil} -> CEILING, full run not started")
            o["full_lesson"] = None
        else:
            print(f"  pilot rule: know-4 worth < .05 for {low} -> full run lesson {160 if low else 80}")
            o["full_lesson"] = 160 if low else 80
    json.dump(o, open(os.path.join(HERE, f"EXP-62g-{TAG}.json"), "w"))


if __name__ == "__main__":
    main()
