"""
EXP-54: does teaching only where the answer differs (upstream PR #197, `learning_surprise=True`) let a label's content
through, where EXP-53's every-row lessons did not?

EXP-53 exactly (same chamber, protocol, seeds and world draws), with the gene on, at the pinned PR head (CADENCE_SRC,
default ~/_cadence_197/src). The every-row arms are EXP-53's rows for the same seeds; MODE=check is the P0 gate
(gene off reproduces EXP-53 bit-identically). Lessons taught and dropped as agreeing are tallied per arm.
PREDICTION: experiments/EXP-54.md (written before any run).

    MODE=check python -u EXP-54_surprise_teaching.py
    STUDENTS=3 TAG=pilot python -u EXP-54_surprise_teaching.py
    STUDENTS=24 WORKERS=4 TAG=full python -u EXP-54_surprise_teaching.py
"""
import importlib.util, json, os, sys, time
from multiprocessing import get_context

CADENCE_SRC = os.path.expanduser(os.environ.get("CADENCE_SRC", "~/_cadence_197/src"))
sys.path.insert(0, CADENCE_SRC)
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("EPISODES", "120")
_spec = importlib.util.spec_from_file_location("e52", os.path.join(HERE, "EXP-52_noesis_lite_null_counterfactual.py"))
E52 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E52)
live_world, per_state, UNSEEN, labeller = E52.live_world, E52.per_state, E52.UNSEEN, E52.labeller

MODE = os.environ.get("MODE", "run")
STUDENTS = int(os.environ.get("STUDENTS", 24))
WORKERS = int(os.environ.get("WORKERS", 4))
TAG = os.environ.get("TAG", "full")
LENGTHS = [int(x) for x in os.environ.get("LENGTHS", "40,120,240").split(",")]
VEST = 20
ARMS = (("know4", "know-4"), ("random", "random"), ("untaught", None))


def compose(seed, surprise):
    import cadence as cd
    kw = dict(learning_surprise=True) if surprise else {}
    return cd.Brain.compose(10, 5, modules=(48, 24), seed=int(seed), arousal=True, memory_choice=True, **kw)


def tally(brain, counts):
    """Wrap this brain's step: after each lesson, add the rows taught and the rows dropped as agreeing."""
    inner = brain.step

    def step(*a, **kw):
        out = inner(*a, **kw)
        if kw.get("teacher") is not None:
            ll = brain.last_learning
            counts["lessons"] += 1
            counts["taught"] += int(ll.get("demonstration_accepted_presentations", 1))
            counts["agreed"] += int(ll.get("demonstration_agreed_presentations", 0))
        return out

    brain.step = step


def student(lesson, k, surprise):
    seed = 5_000_000 + 1000 * lesson + k                     # EXP-53's seed for this student
    out = dict(lesson=lesson, student=k)
    for arm, kind in ARMS:
        rng = np.random.default_rng(seed)
        s = compose(seed, surprise)
        counts = dict(lessons=0, taught=0, agreed=0)
        tally(s, counts)
        lab = labeller(kind, np.random.default_rng(seed + 1)) if kind else None
        live_world(s, lesson, rng, label=lab)
        live_world(s, VEST, rng, call="live")
        out[arm] = per_state(s, UNSEEN)
        out[arm + "_counts"] = counts
    out["content"] = out["know4"] - out["random"]
    return out


def run(job):
    lesson, k = job
    t0 = time.time()
    out = student(lesson, k, surprise=True)
    out["secs"] = round(time.time() - t0, 1)
    c4, cr = out["know4_counts"], out["random_counts"]
    print(f"  L{lesson:3d} st{k}: know4 {out['know4']:.2f} random {out['random']:.2f} untaught {out['untaught']:.2f} "
          f"content {out['content']:+.2f} | agreed know4 {c4['agreed']}/{c4['lessons']} random {cr['agreed']}/{cr['lessons']} "
          f"({out['secs']}s)", flush=True)
    return out


def exp53_rows():
    return {(r["lesson"], r["student"]): r for r in map(json.loads, open(os.path.join(HERE, "EXP-53-full.jsonl")))}


def check():
    import cadence as cd
    print(f"EXP-54 check (P0): cadence {cd.__version__} from {os.path.dirname(cd.__file__)}", flush=True)
    ref, ok = exp53_rows(), True
    for k in (0, 1):
        got = student(40, k, surprise=False)
        for arm, _ in ARMS:
            same = got[arm] == ref[(40, k)][arm]
            ok &= same
            print(f"  L40 st{k} {arm}: gene off {got[arm]!r}  EXP-53 {ref[(40, k)][arm]!r}  {'SAME' if same else 'DIFFERENT'}",
                  flush=True)
        c = got["know4_counts"]
        print(f"  L40 st{k} gene off know4 lessons {c['lessons']} taught {c['taught']} agreed {c['agreed']}", flush=True)
    print(f"P0 (gene off reproduces EXP-53): {'HOLDS' if ok else 'FAILS'}", flush=True)


def main():
    t0 = time.time()
    ckpt = os.path.join(HERE, f"EXP-54-{TAG}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["lesson"], r["student"]) for r in rows}
    jobs = [(L, k) for k in range(STUDENTS) for L in LENGTHS if (L, k) not in done]
    print(f"EXP-54: {len(jobs)} students to go ({len(done)} done); lengths {LENGTHS}; cadence from {CADENCE_SRC}", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as f:
                    f.write(json.dumps(r) + "\n")
    ref = exp53_rows()
    sem = lambda x: float(np.std(x, ddof=1) / np.sqrt(len(x))) if len(x) > 1 else 0.0
    print(f"\nEXP-54 summary: {STUDENTS} students per length ({time.time() - t0:.0f}s); per-state accuracy on unseen weather;"
          f" every-row = EXP-53's rows for the same seeds")
    summary = {}
    for L in LENGTHS:
        rs = [r for r in rows if r["lesson"] == L and r["student"] < STUDENTS]
        if not rs:
            continue
        e = [ref[(L, r["student"])] for r in rs]
        o = {a: float(np.mean([r[a] for r in rs])) for a in ("know4", "random", "untaught")}
        c = [r["content"] for r in rs]
        g4 = [r["know4"] - x["know4"] for r, x in zip(rs, e)]
        gr = [r["random"] - x["random"] for r, x in zip(rs, e)]
        share = {a: sum(r[a + "_counts"]["agreed"] for r in rs) / max(1, sum(r[a + "_counts"]["lessons"] for r in rs))
                 for a in ("know4", "random")}
        o.update(n=len(rs), content=float(np.mean(c)), content_sem=sem(c),
                 content_everyrow=float(np.mean([x["content"] for x in e])),
                 gene_know4=float(np.mean(g4)), gene_know4_sem=sem(g4), gene_random=float(np.mean(gr)), gene_random_sem=sem(gr),
                 untaught_same=all(r["untaught"] == x["untaught"] for r, x in zip(rs, e)),
                 agreed_share_know4=share["know4"], agreed_share_random=share["random"])
        summary[str(L)] = o
        print(f"  lesson {L:3d} n={o['n']:2d}  know-4 {o['know4']:.3f}  random {o['random']:.3f}  untaught {o['untaught']:.3f}  "
              f"content {o['content']:+.3f} (SEM {o['content_sem']:.3f}; every-row {o['content_everyrow']:+.3f})")
        print(f"             gene effect know-4 {o['gene_know4']:+.3f} (SEM {o['gene_know4_sem']:.3f})  random {o['gene_random']:+.3f}"
              f" (SEM {o['gene_random_sem']:.3f})  agreed share know-4 {o['agreed_share_know4']:.3f} random "
              f"{o['agreed_share_random']:.3f}  untaught = EXP-53: {o['untaught_same']}")
    json.dump(dict(rows=rows, summary=summary), open(os.path.join(HERE, f"EXP-54-{TAG}.json"), "w"))


if __name__ == "__main__":
    check() if MODE == "check" else main()
