"""
EXP-62: does transfer price skill on a brain that takes in content, against a committed null?

Merges EXP-52's market (know-k teachers, task-blind fakes, form-matched random-label null, untaught twin) with EXP-58's
delayed-credit brain (EXP-45's operating point) and its alone phase run through `step`. Changes vs EXP-52 (VS program
NEXT ITERATIONS item 1): (a) shared student seeds across arms, null and untaught built once per student; (b) worth priced
against the committed stronger counterfactual (whichever of null / untaught has the higher pooled mean), both reported;
(c) lesson-length window pilot under the exact run conditions; (d) pay finalized on batches of 6 students per teacher
(mean > 0 and mean / SEM > 2); (e) every twin's per-state greedy actions and every teacher's label stream logged.
New arm: anti-echo (uniform among the 4 actions other than the executed mistake). Abstain = the untaught twin.
PRE-REGISTRATION: experiments/EXP-62.md (written before the pilot).

    TAG=pilot STUDENTS=3 LENGTHS=40,80,120 ARMS=pilot WORKERS=4 python -u EXP-62_content_market_committed_null.py
    TAG=full STUDENTS=72 LENGTHS=<chosen> ARMS=full WORKERS=4 python -u EXP-62_content_market_committed_null.py
"""
import importlib.util, json, os, time
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("EPISODES", "120")
_spec = importlib.util.spec_from_file_location("e58", os.path.join(HERE, "EXP-58_content_delayed_credit_brain.py"))
E58 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E58)
E52, compose, live_world = E58.E52, E58.compose, E58.live_world
E49 = E52.E49
E48 = E49.E48
STATES, RIGHTS, UNSEEN, x_of = E48.STATES, E48.RIGHTS, E48.UNSEEN, E48.x_of

TAG = os.environ.get("TAG", "full")
STUDENTS = int(os.environ.get("STUDENTS", 72))
WORKERS = int(os.environ.get("WORKERS", 4))
LENGTHS = [int(x) for x in os.environ.get("LENGTHS", "80").split(",")]
VEST = 20
BATCH = 6
KNOW = ["know-1", "know-2", "know-3", "know-4"]
FAKES = ["random", "wrong-chain", "echo", "anti-echo"]
TEACHERS = KNOW + (FAKES if os.environ.get("ARMS", "full") == "full" else ["random"])
SEED_BASE = 6_290_000 if TAG == "pilot" else 6_200_000


def labeller(kind, rng):
    if kind == "anti-echo":
        return lambda c, a: int(rng.choice([x for x in range(5) if x != int(a)]))
    return E52.labeller(kind, rng)


def logged(lab, stream):
    def f(c, a):
        t = lab(c, a)
        stream.append([int(c.right()), int(a), int(t)])
        return t
    return f


def greedy_actions(b):
    out = []
    for wx in UNSEEN:
        for st in STATES:
            b.reset()
            out.append(int(b.act(x_of(st, wx), greedy=True)[0]))
    return out


def twin(seed, lesson, kind, lab_seed):
    rng = np.random.default_rng(seed)                      # same world draws for every arm of this student
    s = compose(seed)
    stream = []
    lab = logged(labeller(kind, np.random.default_rng(lab_seed)), stream) if kind else None
    live_world(s, lesson, rng, label=lab)
    live_world(s, VEST, rng)                               # alone through `step`, no labels (EXP-58)
    acts = greedy_actions(s)
    hits = [a == r for a, r in zip(acts, RIGHTS * len(UNSEEN))]
    return dict(acc=float(np.mean(hits)), actions=acts, labels=stream,
                label_right=float(np.mean([t == r for r, _, t in stream])) if stream else None, n_labels=len(stream))


def run(job):
    lesson, k = job
    t0 = time.time()
    seed = SEED_BASE + (1000 * lesson if TAG == "pilot" else 0) + k
    out = dict(lesson=lesson, student=k, seed=seed, arms={})
    out["arms"]["null"] = twin(seed, lesson, "random", seed + 2)
    out["arms"]["untaught"] = twin(seed, lesson, None, None)
    for kind in TEACHERS:
        out["arms"][kind] = twin(seed, lesson, kind, seed + 1)
    out["secs"] = round(time.time() - t0, 1)
    a = out["arms"]
    print(f"  L{lesson:3d} st{k:2d}: null {a['null']['acc']:.2f} untaught {a['untaught']['acc']:.2f} | "
          + " ".join(f"{t} {a[t]['acc']:.2f}" for t in TEACHERS) + f" ({out['secs']}s)", flush=True)
    return out


def sem(x):
    x = np.asarray(x, float)
    return float(np.std(x, ddof=1) / np.sqrt(len(x))) if len(x) > 1 else 0.0


def spearman(a, b):
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def analyse(rows, lesson):
    rs = sorted((r for r in rows if r["lesson"] == lesson and r["student"] < STUDENTS), key=lambda r: r["student"])
    acc = lambda arm: np.array([r["arms"][arm]["acc"] for r in rs])
    null, unt = acc("null"), acc("untaught")
    cf_name = "null" if null.mean() > unt.mean() else "untaught"
    cf = null if cf_name == "null" else unt
    arms = TEACHERS + ["abstain"]
    worth = {t: (acc(t) if t != "abstain" else unt) - cf for t in arms}
    o = dict(lesson=lesson, n=len(rs), cf=cf_name, null_acc=float(null.mean()), untaught_acc=float(unt.mean()), arms={})
    for t in arms:
        raw = acc(t) if t != "abstain" else unt
        lr = [r["arms"][t]["label_right"] for r in rs if t != "abstain" and r["arms"][t]["label_right"] is not None]
        o["arms"][t] = dict(acc=float(raw.mean()), worth=float(worth[t].mean()), sem=sem(worth[t]),
                            vs_null=float((raw - null).mean()), vs_null_sem=sem(raw - null),
                            vs_untaught=float((raw - unt).mean()), vs_untaught_sem=sem(raw - unt),
                            label_right=float(np.mean(lr)) if lr else None)
    kv = np.array([int(t.split("-")[1]) for t in KNOW for _ in rs], float)
    wv = np.concatenate([worth[t] for t in KNOW])
    o["spearman_k"], o["n_spearman"] = spearman(kv, wv), len(wv)
    means = [o["arms"][t]["worth"] for t in KNOW]
    o["ordered"] = bool(all(means[i] < means[i + 1] for i in range(3)))
    pay = {}
    for t in arms:
        p = 0.0
        for i in range(0, len(rs) - BATCH + 1, BATCH):
            w = worth[t][i:i + BATCH]
            m, se = float(w.mean()), sem(w)
            if m > 0 and se > 0 and m / se > 2:
                p += m
        pay[t] = p
    total = sum(pay.values()) or 1.0
    blind = FAKES + ["abstain"]
    o["pay"] = {t: pay[t] / total for t in arms}
    o["fake_pay_share"] = float(sum(pay[t] for t in blind if t in pay) / total)
    k2 = o["arms"]["know-2"]["worth"]
    fk = {t: o["arms"][t]["worth"] for t in blind if t in o["arms"]}
    ae = o["arms"].get("anti-echo")
    crit = dict(ordered=o["ordered"], spearman_ge_3=o["spearman_k"] >= 0.3 and o["n_spearman"] >= 288,
                know4_ge_2=o["arms"]["know-4"]["worth"] >= 0.2, fakes_le_0=all(v <= 0 for v in fk.values()),
                fake_pay_le_10=o["fake_pay_share"] <= 0.10)
    o["criteria"] = crit
    o["kill"] = bool(any(v >= k2 for v in fk.values()))
    o["anti_echo_pos_2sem"] = bool(ae is not None and ae["worth"] > 2 * ae["sem"] and ae["sem"] > 0)
    o["filter_not_price"] = bool(o["arms"]["know-4"]["worth"] >= 0.2 and o["spearman_k"] < 0.1)
    o["verdict"] = ("KILL" if o["kill"] else "CONFIRM" if all(crit.values()) else "BOUNDARY")
    return o


def report(o):
    print(f"\n  lesson {o['lesson']}: n={o['n']}  committed CF = {o['cf']}  (null acc {o['null_acc']:.3f}, untaught "
          f"{o['untaught_acc']:.3f})")
    print(f"    {'arm':12s} {'acc':>6s} {'worth':>7s} {'sem':>6s} {'vs null':>8s} {'vs untaught':>12s} {'label right':>12s} {'pay':>6s}")
    for t, a in o["arms"].items():
        lr = f"{a['label_right']:.2f}" if a["label_right"] is not None else "-"
        print(f"    {t:12s} {a['acc']:6.3f} {a['worth']:+7.3f} {a['sem']:6.3f} {a['vs_null']:+8.3f} {a['vs_untaught']:+12.3f} "
              f"{lr:>12s} {o['pay'].get(t, 0):6.3f}")
    print(f"    Spearman(worth, k) = {o['spearman_k']:.3f} (n={o['n_spearman']})  ordered={o['ordered']}  "
          f"fake pay share = {o['fake_pay_share']:.3f}")
    print(f"    criteria: {o['criteria']}  kill={o['kill']}  anti-echo>0 by 2 SEM={o['anti_echo_pos_2sem']}  "
          f"filter-not-price={o['filter_not_price']}  -> {o['verdict']}")


def main():
    import cadence
    t0 = time.time()
    ckpt = os.path.join(HERE, f"EXP-62-{TAG}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["lesson"], r["student"]) for r in rows}
    jobs = [(L, k) for k in range(STUDENTS) for L in LENGTHS if (L, k) not in done]
    print(f"EXP-62 [{TAG}]: cadence {getattr(cadence, '__version__', '?')} at {os.path.dirname(cadence.__file__)}; "
          f"{len(jobs)} students to go ({len(done)} done); lengths {LENGTHS}; arms null, untaught, {TEACHERS}", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as fh:
                    fh.write(json.dumps(r) + "\n")
    print(f"\nEXP-62 [{TAG}] summary ({time.time() - t0:.0f}s); worth = taught - committed CF, per-state accuracy on unseen weather")
    summ = {}
    for L in LENGTHS:
        o = analyse(rows, L)
        summ[str(L)] = o
        report(o)
    json.dump(dict(summary=summ), open(os.path.join(HERE, f"EXP-62-{TAG}.json"), "w"))


if __name__ == "__main__":
    main()
