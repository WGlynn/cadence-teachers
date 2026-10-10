"""
EXP-36 — attack the market: sandbagging collusion + fake need, under self-reported lists vs probe + ledger.

World = EXP-34 FIX (notes + drift-check + rehearse, neediest-first, pay = student's measured gain).
8 brains: 0-4 honest, 5 = FAKE-NEED (claims to know nothing, soaks lessons), 6 = COLLUDING TEACHER,
7 = SANDBAGGER (6's partner: 6 always teaches 7; 7 answers WRONG on purpose in the before-test so the
measured gain is inflated, and pay goes to 6).
Modes:
  LIST          : need = self-reported known lists; gain measured on answers the student reports itself
  PROBE+LEDGER  : need and gain measured by the protocol on a committed copy (sandbagging only works on tests
                  the brain itself runs); each (student, item) can be credited once (provenance ledger)
  SMART         : PROBE+LEDGER, but the sandbagger ALSO sandbags protocol probes (it detects tests) - the
                  ledger is then the only defence
  RECIP         : SMART + reciprocity: a brain's need is weighted by (1 + lessons it has given) / (1 + lessons it
                  has received), so free-riders (never teach) and lesson-soakers sink in the queue
Measured: fake pay (pay to 6 beyond the real gain it caused), honest network knowledge, share of all lessons
absorbed by 5 and 7.
PREDICTION (before running): LIST leaks large fake pay and loses throughput; PROBE+LEDGER leaks ~0; SMART leaks
a bounded amount (at most one credit per item), set by the ledger.
Honest scope: in PROBE+LEDGER the adversary cannot detect the probe BY CONSTRUCTION; SMART is the realistic case.
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
    given, received = [0] * N, [0] * N
    honest_acc = [float(np.mean([np.mean(ans[i] == RULE) for i in HONEST]))]

    def reported(i, a):
        """What brain i's own before-test reports. The sandbagger flips its answers (pretends ignorance)."""
        return (1 - a) if i == SAND else a

    def probed(i, a):
        if mode in ("SMART", "RECIP") and i == SAND:
            return 1 - a                       # detects protocol probes too
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
                need = [len(set(pool) - claims[j]) if j != t else -1 for j in range(N)]
                if mode == "RECIP":
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
            true_gain = after - before_true
            if mode == "LIST":
                paid = after - before_meas            # gain against the student's own (sandbaggable) report
            else:
                # protocol pay: items now right that the PROBED before-state had wrong, each (student, item) once
                items = [c for c in pool if ans[s][c] == RULE[c] and probe_before[c] != RULE[c]
                         and (s, c) not in credited]
                credited.update((s, c) for c in items)
                paid = len(items) / K
            if t == COLL:
                fake_pay += max(0.0, paid - true_gain)
                real_gain_by_coll += true_gain
            for c in pool:
                if ans[s][c] == tans[c] and c not in S.known:
                    S.known.add(c); notes[s][c] = int(tans[c])
        honest_acc.append(float(np.mean([np.mean(ans[i] == RULE) for i in HONEST])))
    return dict(mode=mode, seed=seed, fake_pay=fake_pay, coll_real=real_gain_by_coll,
                absorbed=absorbed / max(1, lessons), honest_acc=honest_acc)


def main():
    t0 = time.time()
    modes = os.environ.get("MODES", "LIST,PROBE+LEDGER,SMART,RECIP").split(",")
    tag = os.environ.get("TAG", "fixed")
    ckpt = os.path.join(HERE, f"EXP-36-{tag}.jsonl")
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
    print(f"EXP-36 adversarial market  rounds={ROUNDS} seeds={SEEDS}  ({time.time()-t0:.0f}s)")
    for md in modes:
        rs = [r for r in res if r["mode"] == md]
        h = np.array([r["honest_acc"] for r in rs])
        print(f"  {md:13s} fake pay minted {np.mean([r['fake_pay'] for r in rs]):.3f} (real gain caused by colluder "
              f"{np.mean([r['coll_real'] for r in rs]):.3f})  lessons absorbed by attackers "
              f"{np.mean([r['absorbed'] for r in rs]):.2f}  honest knowledge final {h[:, -1].mean():.3f}  curve "
              + " ".join(f"{x:.2f}" for x in h.mean(0)[::2]))
    json.dump(res, open(os.path.join(HERE, f"EXP-36-{tag}.json"), "w"))


if __name__ == "__main__":
    main()
