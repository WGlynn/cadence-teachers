"""
EXP-38: repeat-need detection against the probe-fooling sandbagger, on top of reciprocity (EXP-36 RECIP).

World and attackers = EXP-36 (fixed): 8 brains, 0-4 honest, 5 = FAKE-NEED, 6 = COLLUDING TEACHER (always teaches 7),
7 = SANDBAGGER that flips its answers on protocol probes (SMART). Pay = protocol-probed gain, ledger credits each
(student, item) once.
New signal: the protocol keeps PASSED[s] = items student s answered right in a post-lesson test (the after-test is not
sandbaggable: it is where a sandbagger has to show skill to get its partner paid). A REPEAT CLAIM = the probe says s
lacks an item in PASSED[s]. Honest brains repeat-claim only when they really forgot (EXP-33: forgetting ~.01-.04).
Modes:
  RECIP        : EXP-36 RECIP baseline (need weighted by (1+given)/(1+received)).
  REPEAT       : RECIP, and items in PASSED[s] do not count as s's need (no second lesson on a passed item).
  REPEAT+RATE  : REPEAT, and s's need is also scaled by (1 - repeat_rate[s]), repeat_rate = repeat claims / probed
                 PASSED items (so a brain that habitually re-claims sinks for everything, not just repeats).
  ADAPT        : REPEAT+RATE against an ADAPTIVE sandbagger that knows the detector: it answers probes honestly on
                 PASSED items and flips only the rest. Shows the residual the detector cannot see.
Read-outs: fake pay to the colluder, share of lessons absorbed by attackers (5, 7), honest final knowledge, detector
separation (sandbagger vs honest repeat rate). Honest false positives: honest brains' repeat rate and need lost.
PREDICTION (2026-10-10, before the pilot): REPEAT cuts lessons absorbed by attackers well below RECIP (.69 in EXP-36)
and lifts honest final knowledge toward the no-attacker level (~.95); fake pay falls (bounded by items the sandbagger
knew before ever being taught). Sandbagger repeat rate >> honest (>0.5 vs <0.1). ADAPT recovers part of the soak
(fake need on founder items only), so ADAPT sits between REPEAT+RATE and RECIP.
PILOT (2 seeds, 16 rounds): detector separates (sandbagger 1.00 vs honest .025); absorbed .69 -> .34; honest .906 ->
.947; but colluder fake pay ROSE (.156 -> .42-.61). Reason: the ledger pays each (student, item) once; under RECIP
honest teachers burned those credits on the sandbagger, under REPEAT the colluder collects them. EXP-36's metric counted
only the colluder, so fake pay minted to fooled honest teachers was never measured. Added fake_all (any teacher).
PREDICTION REVISED after the pilot (before the full run): total fake pay (fake_all) roughly unchanged across RECIP /
REPEAT / REPEAT+RATE (bounded by the ledger, it only moves to the colluder); repeat detection buys THROUGHPUT (absorbed
<= .40, honest final >= .94 vs RECIP ~.91, > 2 SEM), not less minting. ADAPT: repeat rate ~0 (detector blind), yet
absorbed stays low because passed items are excluded from need regardless of the probe.
"""
# 2026-10-10: removed a duplicated lesson block (each teacher gave 2 lessons/round; only the 2nd was accounted,
# the 1st silently consumed ledger credits). iter24 numbers came from the buggy version (EXP-36.out).
import os, sys, json, time, importlib.util
import numpy as np
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
N, K = 8, 32
M = int(os.environ.get("M", 16))
ROUNDS = int(os.environ.get("ROUNDS", 16))
SEEDS = int(os.environ.get("SEEDS", 6))
FAKE, COLL, SAND = 5, 6, 7
HONEST = [0, 1, 2, 3, 4]


def e31():
    spec = importlib.util.spec_from_file_location("e31", os.path.join(HERE, "EXP-31_peer_exchange.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def run(args):
    mode, seed = args
    m = e31()
    RULE = m.RULE
    rng = np.random.default_rng(1000 + seed)
    perm = rng.permutation(K)
    peers = [m.Peer(10_000 * (seed + 1) + i, list(perm[i * K // N:(i + 1) * K // N])) for i in range(N)]
    notes = [{int(c): int(RULE[c]) for c in p.known} for p in peers]
    credited = set()                      # (student, item) pairs already paid (ledger)
    ans = [p.answers() for p in peers]
    fake_pay, real_gain_by_coll, lessons, absorbed = 0.0, 0.0, 0, 0
    fake_all = 0.0
    given, received = [0] * N, [0] * N
    honest_acc = [float(np.mean([np.mean(ans[i] == RULE) for i in HONEST]))]

    def reported(i, a):
        """What brain i's own before-test reports. The sandbagger flips its answers (pretends ignorance)."""
        return (1 - a) if i == SAND else a

    passed = [set() for _ in range(N)]     # items each brain answered right in a post-lesson test
    rep_claims, rep_probes = [0] * N, [0] * N

    def probed(i, a):
        if i == SAND:
            if mode == "ADAPT":                # knows the detector: honest on passed items, flips the rest
                out = 1 - a
                for c in passed[i]:
                    out[c] = a[c]
                return out
            return 1 - a                       # detects protocol probes too (SMART sandbagger)
        return a

    for r in range(ROUNDS):
        for t in range(N):
            T = peers[t]
            tans = ans[t]
            pool = sorted(c for c in T.known if tans[c] == notes[t][c])
            if not pool or t == FAKE:
                continue
            if t == COLL:
                s = SAND
            else:
                if mode == "LIST":
                    claims = [set() if j in (FAKE, SAND) else peers[j].known for j in range(N)]
                else:
                    claims = [{c for c in range(K) if probed(j, ans[j])[c] == RULE[c]} for j in range(N)]
                for j in range(N):             # repeat-need bookkeeping on this probe
                    if j != t and passed[j]:
                        rep_probes[j] += len(passed[j])
                        rep_claims[j] += len(passed[j] - claims[j])
                if mode == "RECIP":
                    need = [len(set(pool) - claims[j]) if j != t else -1 for j in range(N)]
                else:
                    need = [len(set(pool) - claims[j] - passed[j]) if j != t else -1 for j in range(N)]
                    if mode in ("REPEAT+RATE", "ADAPT"):
                        need = [n * (1 - rep_claims[j] / rep_probes[j]) if n >= 0 and rep_probes[j] else n
                                for j, n in enumerate(need)]
                if mode != "LIST":
                    need = [n * (1 + given[j]) / (1 + received[j]) if n >= 0 else -1 for j, n in enumerate(need)]
                s = int(rng.choice(np.flatnonzero(np.array(need) == max(need))))
            S = peers[s]
            given[t] += 1; received[s] += 1
            lessons += 1
            absorbed += int(s in (FAKE, SAND))
            measure = reported if mode == "LIST" else probed
            before_true = float(np.mean(ans[s] == RULE))
            probe_before = measure(s, ans[s])
            before_meas = float(np.mean(probe_before == RULE))
            for _ in range(M):
                c = int(rng.choice(pool))
                S._live(c, lambda a, c=c: 1.0 if a == tans[c] else -1.0)
            if S.known:
                own = sorted(S.known)
                for _ in range(M // 2):
                    c = int(rng.choice(own))
                    S._live(c, lambda a, c=c: 1.0 if a == notes[s][c] else -1.0)
            ans[s] = S.answers()
            after = float(np.mean(ans[s] == RULE))       # after-test: the sandbagger shows real skill
            passed[s].update(c for c in pool if ans[s][c] == RULE[c])
            true_gain = after - before_true
            if mode == "LIST":
                paid = after - before_meas            # gain against the student's own (sandbaggable) report
            else:
                # protocol pay: items now right that the PROBED before-state had wrong, each (student, item) once
                items = [c for c in pool if ans[s][c] == RULE[c] and probe_before[c] != RULE[c]
                         and (s, c) not in credited]
                credited.update((s, c) for c in items)
                paid = len(items) / K
            if s in (FAKE, SAND):                # fake pay minted on ANY lesson to an attacker (EXP-36 counted COLL only)
                fake_all += max(0.0, paid - true_gain)
            if t == COLL:
                fake_pay += max(0.0, paid - true_gain)
                real_gain_by_coll += true_gain
            for c in pool:
                if ans[s][c] == tans[c] and c not in S.known:
                    S.known.add(c); notes[s][c] = int(tans[c])
        honest_acc.append(float(np.mean([np.mean(ans[i] == RULE) for i in HONEST])))
    rate = [rep_claims[j] / rep_probes[j] if rep_probes[j] else 0.0 for j in range(N)]
    return dict(mode=mode, seed=seed, fake_pay=fake_pay, fake_all=fake_all, coll_real=real_gain_by_coll,
                absorbed=absorbed / max(1, lessons), honest_acc=honest_acc,
                rep_sand=rate[SAND], rep_fake=rate[FAKE], rep_honest=float(np.mean([rate[j] for j in HONEST])),
                cadence=_ver())


def _ver():
    try:
        import cadence
        return getattr(cadence, "__version__", "?")
    except Exception:
        return "?"


def main():
    t0 = time.time()
    modes = os.environ.get("MODES", "RECIP,REPEAT,REPEAT+RATE,ADAPT").split(",")
    tag = os.environ.get("TAG", "full")
    ckpt = os.path.join(HERE, f"EXP-38-{tag}.jsonl")
    res = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["mode"], r["seed"]) for r in res}
    jobs = [(md, s) for md in modes for s in range(SEEDS) if (md, s) not in done]
    print(f"resuming: {len(done)} done, {len(jobs)} to run", flush=True)
    with get_context("spawn").Pool(int(os.environ.get("WORKERS", 3))) as pool:
        for r in pool.imap_unordered(run, jobs):
            res.append(r)
            with open(ckpt, "a") as f:
                f.write(json.dumps(r) + chr(10))
            print(f"  done {r['mode']} seed {r['seed']}  ({time.time()-t0:.0f}s)", flush=True)
    res = [r for r in res if r["mode"] in modes and r["seed"] < SEEDS]
    print(f"EXP-38 repeat-need detection  rounds={ROUNDS} seeds={SEEDS}  ({time.time()-t0:.0f}s)")
    for md in modes:
        rs = [r for r in res if r["mode"] == md]
        h = np.array([r["honest_acc"] for r in rs])
        print(f"  {md:13s} fake pay minted {np.mean([r['fake_pay'] for r in rs]):.3f} (real gain caused by colluder "
              f"{np.mean([r['coll_real'] for r in rs]):.3f})  lessons absorbed by attackers "
              f"{np.mean([r['absorbed'] for r in rs]):.2f}  honest knowledge final {h[:, -1].mean():.3f}  curve "
              + " ".join(f"{x:.2f}" for x in h.mean(0)[::2])
              + f"  | fake pay ALL teachers {np.mean([r['fake_all'] for r in rs]):.3f}"
              + f"  | repeat rate sand {np.mean([r['rep_sand'] for r in rs]):.2f} fake {np.mean([r['rep_fake'] for r in rs]):.2f} honest {np.mean([r['rep_honest'] for r in rs]):.3f}"
              + f"  | SEM honest {h[:, -1].std(ddof=1)/len(h)**.5 if len(h) > 1 else 0:.3f} absorbed {np.std([r['absorbed'] for r in rs], ddof=1)/len(rs)**.5 if len(rs) > 1 else 0:.3f}")
    json.dump(res, open(os.path.join(HERE, f"EXP-38-{tag}.json"), "w"))


if __name__ == "__main__":
    main()
