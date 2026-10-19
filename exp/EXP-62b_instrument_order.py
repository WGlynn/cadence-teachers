"""
EXP-62b: does the order of worth among genuine teachers depend on which brain measures it?
EXP-62's harness; teachers know-early-2 (stages 1-2), know-late-2 (stages 3-4), know-4, null (random labels, the zero),
untaught. Three instruments fixed before any data: A = EXP-58's delayed-credit brain, B = EXP-61's default memory brain
with only the actor step at .1 / bias .01 (EXP-64), C = A with modules (64,) and critic 2.0.
Primary: D_I = acc(know-early-2) - acc(know-late-2), paired by student, per instrument that takes in content.
PRE-REGISTRATION: experiments/EXP-62b.md (written before any data).

    TAG=pilot STUDENTS=3 WORKERS=4 python -u EXP-62b_instrument_order.py
    TAG=full STUDENTS=48 LESSON=<80 or 160 per the pilot rule> WORKERS=4 python -u EXP-62b_instrument_order.py
"""
import importlib.util, json, os, time
from dataclasses import replace
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("ARMS", "pilot")                 # E62's teacher list is not used here
_spec = importlib.util.spec_from_file_location("e62", os.path.join(HERE, "EXP-62_content_market_committed_null.py"))
E62 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E62)
E58, E52, RIGHTS = E62.E58, E62.E52, E62.RIGHTS

TAG = os.environ.get("TAG", "full")
STUDENTS = int(os.environ.get("STUDENTS", 48))
WORKERS = int(os.environ.get("WORKERS", 4))
LESSON = int(os.environ.get("LESSON", 80))
SEED_BASE = 7_090_000 if TAG == "pilot" else 7_000_000
INSTRUMENTS = ("A", "B", "C")
TEACHERS = ("know-early-2", "know-late-2", "know-4")
KNOWN = {"know-early-2": {RIGHTS[0], RIGHTS[1]}, "know-late-2": {RIGHTS[2], RIGHTS[3]}}


def compose_for(inst):
    import cadence as cd
    if inst == "A":
        return E58.compose
    if inst == "B":
        def b(seed):
            br = cd.Brain.compose(10, 5, modules=(48, 24), seed=int(seed), arousal=True, memory_choice=True)
            br.basal_ganglia.config = replace(br.basal_ganglia.config, eta=0.1, eta_bias=0.01)
            return br
        return b
    if inst == "C":
        O = dict(E58.OURS, modules=(64,), eta_critic=2.0)

        def c(seed):
            br = cd.Brain.compose(10, 5, modules=O["modules"], seed=int(seed), consolidation=O["consolidation"],
                                  working_memory_amplitude=O["working_memory_amplitude"],
                                  working_memory_scale=12.0, working_memory_decay=0.2)
            br.basal_ganglia.config = replace(br.basal_ganglia.config, **{k: O[k] for k in ("eta", "eta_bias", "lam", "gamma", "eta_critic")})
            return br
        return c
    raise ValueError(inst)


_base_labeller = E62.labeller


def labeller(kind, rng):
    if kind in KNOWN:
        known = KNOWN[kind]
        return lambda c, a: c.right() if c.right() in known else int(rng.integers(5))
    return _base_labeller(kind, rng)


E62.labeller = labeller


def run(job):
    inst, k = job
    import cadence as cd
    E62.compose = compose_for(inst)                     # E62.twin builds every twin through this name
    t0 = time.time()
    seed = SEED_BASE + k
    arms = {"null": E62.twin(seed, LESSON, "random", seed + 2), "untaught": E62.twin(seed, LESSON, None, None)}
    for kind in TEACHERS:
        arms[kind] = E62.twin(seed, LESSON, kind, seed + 1)
    out = dict(instrument=inst, student=k, seed=seed, lesson=LESSON, arms=arms, secs=round(time.time() - t0, 1),
               cadence=cd.__version__)
    print(f"  {inst} st{k:2d}: null {arms['null']['acc']:.2f} untaught {arms['untaught']['acc']:.2f} | "
          + " ".join(f"{t} {arms[t]['acc']:.2f}" for t in TEACHERS) + f" ({out['secs']}s)", flush=True)
    return out


def sem(x):
    return float(np.std(x, ddof=1) / np.sqrt(len(x))) if len(x) > 1 else float("nan")


def analyse(rows):
    o = {"instruments": {}, "pairs": {}}
    by = {(r["instrument"], r["student"]): r for r in rows}
    students = sorted({r["student"] for r in rows})
    D = {}
    for inst in INSTRUMENTS:
        rs = [by[(inst, k)] for k in students if (inst, k) in by]
        if not rs:
            continue
        acc = lambda a: np.array([r["arms"][a]["acc"] for r in rs])
        worth = {a: acc(a) - acc("null") for a in TEACHERS + ("untaught",)}
        k4 = worth["know-4"]
        valid = bool(np.mean(k4) >= 0.10 and np.mean(k4) / sem(k4) >= 2)
        d = acc("know-early-2") - acc("know-late-2")
        D[inst] = dict(zip([r["student"] for r in rs], d))
        rank = sorted(TEACHERS, key=lambda a: -np.mean(worth[a]))
        o["instruments"][inst] = dict(n=len(rs), valid=valid,
                                      worth={a: (float(np.mean(v)), sem(v)) for a, v in worth.items()},
                                      D=(float(np.mean(d)), sem(d)), rank=rank,
                                      secs=float(np.mean([r["secs"] for r in rs])))
    valid = [i for i in INSTRUMENTS if o["instruments"].get(i, {}).get("valid")]
    flip = magnitude = False
    for a in range(len(valid)):
        for b in range(a + 1, len(valid)):
            I, J = valid[a], valid[b]
            common = sorted(set(D[I]) & set(D[J]))
            diff = np.array([D[I][k] - D[J][k] for k in common])
            mI, sI = o["instruments"][I]["D"]
            mJ, sJ = o["instruments"][J]["D"]
            opp = (mI * mJ < 0) and abs(mI) >= 2 * sI and abs(mJ) >= 2 * sJ
            big = abs(np.mean(diff)) > 2 * sem(diff)
            flip |= opp
            magnitude |= big
            o["pairs"][f"{I}-{J}"] = dict(n=len(common), diff=(float(np.mean(diff)), sem(diff)), opposite_sign=bool(opp),
                                          diff_gt_2sem=bool(big))
    if len(valid) < 2:
        verdict = "INCONCLUSIVE (fewer than two instruments take in content)"
    elif flip:
        verdict = "ORDER DEPENDS ON THE INSTRUMENT"
    elif magnitude:
        verdict = "MAGNITUDE ONLY"
    else:
        verdict = "ORDER AGREES"
    o["valid"], o["verdict"] = valid, verdict
    return o


def report(o):
    for inst, v in o["instruments"].items():
        w = "  ".join(f"{a} {m:+.3f} ({s:.3f})" for a, (m, s) in v["worth"].items())
        print(f"  [{inst}] n={v['n']} takes in content: {v['valid']} | worth vs null: {w} | D = early - late "
              f"{v['D'][0]:+.3f} ({v['D'][1]:.3f}) | rank {' > '.join(v['rank'])} | {v['secs']:.0f}s per student")
    for p, q in o["pairs"].items():
        print(f"  pair {p}: n={q['n']} D diff {q['diff'][0]:+.3f} ({q['diff'][1]:.3f}) opposite sign at 2 SEM: "
              f"{q['opposite_sign']}; |diff| > 2 SEM: {q['diff_gt_2sem']}")
    print(f"  valid instruments: {o['valid']} -> {o['verdict']}")


def main():
    t0 = time.time()
    ckpt = os.path.join(HERE, f"EXP-62b-{TAG}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    rows = [r for r in rows if r["lesson"] == LESSON]
    done = {(r["instrument"], r["student"]) for r in rows}
    jobs = [(i, k) for k in range(STUDENTS) for i in INSTRUMENTS if (i, k) not in done]
    print(f"EXP-62b [{TAG}]: lesson {LESSON}; {len(jobs)} jobs to go ({len(done)} done); seeds {SEED_BASE}+", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as fh:
                    fh.write(json.dumps(r) + "\n")
    print(f"\nEXP-62b [{TAG}] summary ({time.time() - t0:.0f}s), lesson {LESSON}")
    o = analyse(rows)
    report(o)
    if TAG == "pilot":
        low = [i for i, v in o["instruments"].items() if v["worth"]["know-4"][0] < 0.05]
        print(f"  pilot rule: instruments with know-4 worth < .05: {low} -> full run lesson {160 if low else 80}")
        o["full_lesson"] = 160 if low else 80
    json.dump(o, open(os.path.join(HERE, f"EXP-62b-{TAG}.json"), "w"))


if __name__ == "__main__":
    main()
