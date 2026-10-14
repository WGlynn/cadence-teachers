"""
EXP-55: does a teacher's content get through when it demonstrates at EVERY decision in a guided window, and does upstream's
surprise rule (PR #197, `learning_surprise=True`) help there?

EXP-53's chamber, seeds, world draws and readings, but the teacher labels the state about to be acted in at every guided
decision (the label goes with the call that presents that state; never with a done call). Five twins per student:
know-4 / random labels x rule off / on, and untaught. Runs at the pinned PR head (CADENCE_SRC, default ~/_cadence_197/src).
The untaught twin is EXP-53's untaught twin (same path, gene irrelevant), so it must match EXP-53's rows exactly.
PREDICTION: experiments/EXP-55.md (written before the pilot).

    STUDENTS=3 TAG=pilot python -u EXP-55_every_decision_demonstrations.py
    STUDENTS=24 WORKERS=4 TAG=full python -u EXP-55_every_decision_demonstrations.py
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
E49 = E52.E49
WeatherChamber, SEEN, GUIDED, AUTONOMOUS = E49.WeatherChamber, E49.SEEN, E49.GUIDED, E49.AUTONOMOUS
per_state, UNSEEN, labeller = E52.per_state, E52.UNSEEN, E52.labeller

STUDENTS = int(os.environ.get("STUDENTS", 24))
WORKERS = int(os.environ.get("WORKERS", 4))
TAG = os.environ.get("TAG", "full")
LENGTHS = [int(x) for x in os.environ.get("LENGTHS", "40,120,240").split(",")]
VEST = 20
TWINS = (("know4_off", "know-4", False), ("random_off", "random", False), ("know4_on", "know-4", True),
         ("random_on", "random", True), ("untaught", None, False))


def compose(seed, surprise):
    import cadence as cd
    kw = dict(learning_surprise=True) if surprise else {}
    return cd.Brain.compose(10, 5, modules=(48, 24), seed=int(seed), arousal=True, memory_choice=True, **kw)


def tally(brain, counts):
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


def live_demo(brain, attempts, rng, label=None, call="step"):
    """V5's continuing life under SEEN weather (EXP-49's loop); with a label, the teacher demonstrates at every decision in
    a guided window: the right (or random) action for the state about to be acted in, with the call that presents it."""
    f = brain.step if call == "step" else brain.live
    c, g = WeatherChamber(SEEN[rng.integers(4)]), 0
    a = int(np.asarray(f(c.x())).reshape(-1)[0])
    for _ in range(attempts):
        while True:
            ok, r = c.execute(a)
            g += 1
            if c.done:
                c = WeatherChamber(SEEN[rng.integers(4)])
                a = int(np.asarray(f(c.x(), reward=np.array([r]), done=np.array([True]))).reshape(-1)[0])
                break
            kw = dict(reward=np.array([r]), done=np.array([False]))
            if label is not None and call == "step" and (g % (GUIDED + AUTONOMOUS)) < GUIDED:
                kw["teacher"] = np.array([label(c, a)])
            a = int(np.asarray(f(c.x(), **kw)).reshape(-1)[0])
    brain.reset()


def run(job):
    lesson, k = job
    t0 = time.time()
    seed = 5_000_000 + 1000 * lesson + k                     # EXP-53's seed for this student
    out = dict(lesson=lesson, student=k)
    for name, kind, surprise in TWINS:
        rng = np.random.default_rng(seed)
        s = compose(seed, surprise)
        counts = dict(lessons=0, taught=0, agreed=0)
        tally(s, counts)
        lab = labeller(kind, np.random.default_rng(seed + 1)) if kind else None
        live_demo(s, lesson, rng, label=lab)
        live_demo(s, VEST, rng, call="live")
        out[name] = per_state(s, UNSEEN)
        out[name + "_counts"] = counts
    out["content_off"] = out["know4_off"] - out["random_off"]
    out["content_on"] = out["know4_on"] - out["random_on"]
    out["secs"] = round(time.time() - t0, 1)
    c4, cr = out["know4_on_counts"], out["random_on_counts"]
    print(f"  L{lesson:3d} st{k}: off know4 {out['know4_off']:.2f} random {out['random_off']:.2f} | on know4 {out['know4_on']:.2f} "
          f"random {out['random_on']:.2f} | untaught {out['untaught']:.2f} | content off {out['content_off']:+.2f} on "
          f"{out['content_on']:+.2f} | agreed know4 {c4['agreed']}/{c4['lessons']} random {cr['agreed']}/{cr['lessons']} "
          f"({out['secs']}s)", flush=True)
    return out


def main():
    t0 = time.time()
    ckpt = os.path.join(HERE, f"EXP-55-{TAG}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["lesson"], r["student"]) for r in rows}
    jobs = [(L, k) for k in range(STUDENTS) for L in LENGTHS if (L, k) not in done]
    print(f"EXP-55: {len(jobs)} students to go ({len(done)} done); lengths {LENGTHS}; cadence from {CADENCE_SRC}", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as fh:
                    fh.write(json.dumps(r) + "\n")
    ref = {(r["lesson"], r["student"]): r for r in map(json.loads, open(os.path.join(HERE, "EXP-53-full.jsonl")))}
    sem = lambda x: float(np.std(x, ddof=1) / np.sqrt(len(x))) if len(x) > 1 else 0.0
    print(f"\nEXP-55 summary: {STUDENTS} students per length ({time.time() - t0:.0f}s); per-state accuracy on unseen weather")
    summary = {}
    for L in LENGTHS:
        rs = [r for r in rows if r["lesson"] == L and r["student"] < STUDENTS]
        if not rs:
            continue
        o = {n: float(np.mean([r[n] for r in rs])) for n, _, _ in TWINS}
        co, cn = [r["content_off"] for r in rs], [r["content_on"] for r in rs]
        gain = [b - a for a, b in zip(co, cn)]
        k4u = [r["know4_off"] - r["untaught"] for r in rs]
        share = {n: sum(r[n + "_counts"]["agreed"] for r in rs) / max(1, sum(r[n + "_counts"]["lessons"] for r in rs))
                 for n in ("know4_on", "random_on")}
        same = all(r["untaught"] == ref[(L, r["student"])]["untaught"] for r in rs if (L, r["student"]) in ref)
        o.update(n=len(rs), content_off=float(np.mean(co)), content_off_sem=sem(co), content_on=float(np.mean(cn)),
                 content_on_sem=sem(cn), rule_gain=float(np.mean(gain)), rule_gain_sem=sem(gain),
                 know4_minus_untaught=float(np.mean(k4u)), know4_minus_untaught_sem=sem(k4u),
                 agreed_share_know4=share["know4_on"], agreed_share_random=share["random_on"], untaught_equals_exp53=same)
        summary[str(L)] = o
        print(f"  lesson {L:3d} n={o['n']:2d}  off: know-4 {o['know4_off']:.3f} random {o['random_off']:.3f} | on: know-4 "
              f"{o['know4_on']:.3f} random {o['random_on']:.3f} | untaught {o['untaught']:.3f} (= EXP-53: {same})")
        print(f"             content off {o['content_off']:+.3f} (SEM {o['content_off_sem']:.3f})  on {o['content_on']:+.3f} "
              f"(SEM {o['content_on_sem']:.3f})  rule gain {o['rule_gain']:+.3f} (SEM {o['rule_gain_sem']:.3f})  know-4 off - "
              f"untaught {o['know4_minus_untaught']:+.3f} (SEM {o['know4_minus_untaught_sem']:.3f})  agreed share know-4 "
              f"{o['agreed_share_know4']:.3f} random {o['agreed_share_random']:.3f}")
    json.dump(dict(rows=rows, summary=summary), open(os.path.join(HERE, f"EXP-55-{TAG}.json"), "w"))


if __name__ == "__main__":
    main()
