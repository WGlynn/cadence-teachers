"""
EXP-49: Noesis-lite v1. Does a market that pays teachers by measured transfer, on situations the lesson never covered and
after time alone, pay the genuine teachers in proportion to their skill and price every fake at zero?

Design: docs/NOESIS-LITE-SIM.md (v1 = transfer pricing + replication; the stake/standing finality rule and colluding
verifiers are v2). Chamber: EXP-48's weather chamber (V5 replica + 3 irrelevant bits; lessons under SEEN weathers, worth
measured under UNSEEN ones).

Teachers (per market seed):
  genuine-20/40/80/120 : memory brains taught by the corrective caregiver for 20/40/80/120 attempts (skill varies)
  random               : labels a uniformly random action
  wrong-chain          : labels a consistent wrong chain (each stage's action shifted by one)
  echo                 : labels the action the student just took (zero information, total agreement)
A lesson: a fresh memory student lives LESSON attempts under SEEN weather; on an executed mistake in a guided window
(V5's 4-of-12 schedule) the teacher's greedy answer for the student's situation is given as the label.
Worth (twin ablation): the same student seed lives the same attempts with no teacher (world reward only); both twins then
live VEST attempts alone through `live`; worth = per-state greedy accuracy under UNSEEN weather, taught twin minus
untaught twin. Replication: the lesson is re-run on a second, independent student; credit finalizes only if both worths
are above FINAL_BAR. Pay = finalized worth (clipped at 0). Readings: worth and pay by teacher, pay share, Spearman of pay
against the teacher's own unseen per-state accuracy across genuine teachers.
PREDICTION: experiments/EXP-49.md (written before the pilot).

    SEEDS=3 STUDENTS=6 WORKERS=4 TAG=full python -u EXP-49_noesis_lite_market.py
"""
import importlib.util, json, os, tempfile, time
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("EPISODES", "120")
_spec = importlib.util.spec_from_file_location("e48", os.path.join(HERE, "EXP-48_generalize_or_record.py"))
E48 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E48)
WeatherChamber, SEEN, UNSEEN, x_of, per_state = E48.WeatherChamber, E48.SEEN, E48.UNSEEN, E48.x_of, E48.per_state
STATES, RIGHTS, GUIDED, AUTONOMOUS = E48.STATES, E48.RIGHTS, E48.GUIDED, E48.AUTONOMOUS

SEEDS = int(os.environ.get("SEEDS", 3))
STUDENTS = int(os.environ.get("STUDENTS", 6))
WORKERS = int(os.environ.get("WORKERS", 4))
TAG = os.environ.get("TAG", "full")
LESSON = int(os.environ.get("LESSON", 40))
VEST = int(os.environ.get("VEST", 20))
FINAL_BAR = float(os.environ.get("FINAL_BAR", 0.125))
GENUINE = [20, 40, 80, 120]
TEACHERS = [f"genuine-{n}" for n in GENUINE] + ["random", "wrong-chain", "echo"]


def compose(seed):
    import cadence as cd
    return cd.Brain.compose(10, 5, modules=(48, 24), seed=int(seed), arousal=True, memory_choice=True)


def live_world(brain, attempts, rng, label=None, call="step"):
    """V5's continuing-life loop under SEEN weather. label(chamber, chosen_action) -> action label or None."""
    f = brain.step if call == "step" else brain.live
    c, g = WeatherChamber(SEEN[rng.integers(4)]), 0
    a = int(np.asarray(f(c.x())).reshape(-1)[0])
    for _ in range(attempts):
        while True:
            guided = (g % (GUIDED + AUTONOMOUS)) < GUIDED
            ok, r = c.execute(a)
            t = label(c, a) if (label is not None and guided and not ok and not c.done) else None
            g += 1
            if c.done:
                c = WeatherChamber(SEEN[rng.integers(4)])
                a = int(np.asarray(f(c.x(), reward=np.array([r]), done=np.array([True]))).reshape(-1)[0])
                break
            kw = dict(reward=np.array([r]), done=np.array([False]))
            if t is not None and call == "step":
                kw["teacher"] = np.array([t])
            a = int(np.asarray(f(c.x(), **kw)).reshape(-1)[0])
    brain.reset()


def make_teacher(kind, market_seed, d):
    """Returns (label function factory, teacher skill on unseen weather or None). Genuine teachers are saved brains."""
    import cadence as cd
    if kind.startswith("genuine-"):
        n = int(kind.split("-")[1])
        path = os.path.join(d, f"{kind}.npz")
        if not os.path.exists(path):
            b = compose(100_000 * (market_seed + 1) + n)
            live_world(b, n, np.random.default_rng(7 * market_seed + n), label=lambda c, a: c.right())
            b.save(path)
        skill = per_state(cd.Brain.load(path), UNSEEN)
        return path, skill
    return None, None


def labeller(kind, path, rng):
    import cadence as cd
    if kind.startswith("genuine-"):
        t = cd.Brain.load(path)
        def lab(c, a):
            t.reset()
            return int(t.act(c.x(), greedy=True)[0])
        return lab
    if kind == "random":
        return lambda c, a: int(rng.integers(5))
    if kind == "wrong-chain":
        return lambda c, a: (c.right() + 1) % 4
    if kind == "echo":
        return lambda c, a: int(a)
    raise ValueError(kind)


def worth(kind, path, student_seed):
    """Twin ablation: taught twin minus untaught twin, per-state accuracy on UNSEEN weather after VEST attempts alone."""
    out = {}
    for arm in ("taught", "untaught"):
        rng = np.random.default_rng(student_seed)            # same world draws for both twins
        s = compose(student_seed)
        lab = labeller(kind, path, np.random.default_rng(student_seed + 1)) if arm == "taught" else None
        live_world(s, LESSON, rng, label=lab)
        out[arm + "_lesson_end"] = per_state(s, UNSEEN)
        live_world(s, VEST, rng, call="live")
        out[arm] = per_state(s, UNSEEN)
    out["worth"] = out["taught"] - out["untaught"]
    out["worth_at_lesson_end"] = out["taught_lesson_end"] - out["untaught_lesson_end"]
    return out


def run(job):
    market_seed, kind, k, d = job
    t0 = time.time()
    path, _ = make_teacher(kind, market_seed, d)
    base = 1_000_000 * (market_seed + 1) + 1000 * TEACHERS.index(kind) + 10 * k
    first, second = worth(kind, path, base), worth(kind, path, base + 5)
    final = first["worth"] > FINAL_BAR and second["worth"] > FINAL_BAR
    pay = max(0.0, (first["worth"] + second["worth"]) / 2) if final else 0.0
    row = dict(market_seed=market_seed, teacher=kind, student=k, first=first, second=second, final=final, pay=pay,
               secs=round(time.time() - t0, 1))
    print(f"  m{market_seed} {kind:12s} st{k}: worth {first['worth']:+.2f} / {second['worth']:+.2f} "
          f"(at lesson end {first['worth_at_lesson_end']:+.2f}) final {int(final)} pay {pay:.2f} ({row['secs']}s)", flush=True)
    return row


def main():
    t0 = time.time()
    root = os.path.join(HERE, f"EXP-49-{TAG}-teachers")
    os.makedirs(root, exist_ok=True)
    skills = {}
    for m in range(SEEDS):                                   # genuine teachers trained once per market seed, serially
        d = os.path.join(root, f"m{m}")
        os.makedirs(d, exist_ok=True)
        for kind in TEACHERS:
            _, sk = make_teacher(kind, m, d)
            if sk is not None:
                skills[f"m{m}/{kind}"] = sk
    print("teacher skill on unseen weather:", {k: round(v, 2) for k, v in skills.items()}, flush=True)
    ckpt = os.path.join(HERE, f"EXP-49-{TAG}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["market_seed"], r["teacher"], r["student"]) for r in rows}
    jobs = [(m, kind, k, os.path.join(root, f"m{m}")) for m in range(SEEDS) for k in range(STUDENTS) for kind in TEACHERS
            if (m, kind, k) not in done]
    print(f"EXP-49: {len(jobs)} lessons to go ({len(done)} done); lesson {LESSON}, vest {VEST}, teachers {TEACHERS}", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as f:
                    f.write(json.dumps(r) + "\n")
    rows = [r for r in rows if r["market_seed"] < SEEDS and r["student"] < STUDENTS]
    total = sum(r["pay"] for r in rows) or 1.0
    print(f"\nEXP-49 summary: {SEEDS} market seeds x {STUDENTS} students x {len(TEACHERS)} teachers ({time.time() - t0:.0f}s)")
    summary = {}
    for kind in TEACHERS:
        rs = [r for r in rows if r["teacher"] == kind]
        w = [x for r in rs for x in (r["first"]["worth"], r["second"]["worth"])]
        we = [x for r in rs for x in (r["first"]["worth_at_lesson_end"], r["second"]["worth_at_lesson_end"])]
        sk = [skills[f"m{m}/{kind}"] for m in range(SEEDS) if f"m{m}/{kind}" in skills]
        o = dict(worth=float(np.mean(w)), worth_sem=float(np.std(w, ddof=1) / np.sqrt(len(w))) if len(w) > 1 else 0.0,
                 worth_lesson_end=float(np.mean(we)), finalized=sum(r["final"] for r in rs), lessons=len(rs),
                 pay=float(sum(r["pay"] for r in rs)), pay_share=float(sum(r["pay"] for r in rs) / total),
                 skill=float(np.mean(sk)) if sk else None)
        summary[kind] = o
        print(f"  {kind:12s} worth {o['worth']:+.3f} (SEM {o['worth_sem']:.3f}; at lesson end {o['worth_lesson_end']:+.3f})  "
              f"finalized {o['finalized']}/{o['lessons']}  pay share {o['pay_share']:.3f}"
              + (f"  teacher skill {o['skill']:.2f}" if o['skill'] is not None else ""))
    # rank correlation of pay with skill across genuine teachers, per market seed (pooled)
    pairs = []
    for m in range(SEEDS):
        for kind in TEACHERS[:len(GENUINE)]:
            pay = sum(r["pay"] for r in rows if r["market_seed"] == m and r["teacher"] == kind)
            pairs.append((skills[f"m{m}/{kind}"], pay))
    a, b = np.array(pairs).T
    ra, rb = a.argsort().argsort(), b.argsort().argsort()
    rho = float(np.corrcoef(ra, rb)[0, 1]) if a.std() > 0 and b.std() > 0 else float("nan")
    print(f"  Spearman(pay, teacher skill) across genuine teachers, pooled over market seeds: {rho:.2f} (n={len(pairs)})")
    json.dump(dict(rows=rows, summary=summary, skills=skills, spearman=rho), open(os.path.join(HERE, f"EXP-49-{TAG}.json"), "w"))


if __name__ == "__main__":
    main()
