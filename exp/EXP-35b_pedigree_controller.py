"""
EXP-35b: the pedigree share as a control dial, with DISCOVERY, at K=96.

World: K=96 bandit contexts. 8 brains each start knowing 4 (32 known to the network, 64 known to nobody).
Every brain keeps notes (EXP-33 fix: drift-check + rehearse). Each round every brain makes ONE move:
  TEACH    : teach its neediest peer, choosing OWN vs RELAYED items by what each paid it before. Pay = student's
             measured gain, split over newly learned items: the item's ORIGIN gets share ALPHA, the teacher keeps
             the rest. Budget-balanced. The first teacher of founder knowledge becomes its origin (relay royalty).
  DISCOVER : spend the round learning one context it does not know from the world (D graded trials); it becomes
             that item's DISCOVERER. Its pay arrives later, as royalty when others relay the item.
Move choice: running estimate of what each move pays (epsilon 0.15), so ALPHA changes behaviour only through pay.
CREDIT=orig : iter25 accounting (royalty credited to whatever move was made that round). Control arm.
CREDIT=fixed: 2026-10-10 review fixes. Only royalty on items the brain DISCOVERED is credited to Discover (founder-
              relay royalty stays with Teach); every such royalty is credited, sign included; a Discover move is not
              scored when made (its outcome is pending, credited when its royalty arrives; cf. Cadence Brain.wait).
CREDIT=item : 2026-10-10 iter28 (iter27 showed fixed starved Discover: a discoverer is paid mostly by TEACHING its own
              find, which fixed booked as Teach; royalty alone was ~1/40 of direct pay, estD never left PRIOR).
              Discover is credited ALL pay on items the brain found by a Discover move (its own teaching of them +
              royalty from relays). Each move's value = decayed pay / decayed move count (PRIOR = one pseudo-move),
              so a failed or never-relayed discovery counts as 0, not as missing.
Both: estimates start at PRIOR (default 0.01, about one item's pay; was 0.05). PI arm is positional with anti-windup.
Arms: ALPHA fixed 0 / 0.9 and PI (share of brains discovering tracks the share of contexts nobody knows).
Read-outs: final acc AND mean-over-time acc (curves still climb at round 30), network-NEW discoveries per arm (not
just Discover moves, which can rediscover known items), estT/estD, discovery royalty vs all royalty.
Sanity: at ALPHA 0 there is no royalty, so orig and fixed must give identical rows per seed (determinism check).
PREDICTION (2026-10-10, before running): under fixed, estD and network-new discoveries rise with ALPHA (0.9 > 0);
under orig they do not. Accuracy gain is small (headroom ~.05 at round 30) but should show in mean-over-time.
  -> iter27: WRONG (fixed starved Discover; see CREDIT=item).
PREDICTION iter28 (2026-10-10 12:52, before the full run; pilot 3 seeds, PRIOR .01 and .002, all chain links moved):
under CREDIT=item, 12 seeds, ALPHA 0.9 vs 0: per-move Discover pay ~2x (>3 SEM), Discover share in the last 10 rounds
higher by >=.08, network-new discoveries higher by 1-4 (may not clear 2 SEM), final accuracy within +-.02 (no claim).
PI should hold alpha well above 0 (unlike fixed, where it fell to 0).
"""
import os, sys, json, time, importlib.util
import numpy as np
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
N, SLICE = 8, 4
K = int(os.environ.get("K", 96))
M = int(os.environ.get("M", 16))
D = int(os.environ.get("D", 40))
ROUNDS = int(os.environ.get("ROUNDS", 20))
SEEDS = int(os.environ.get("SEEDS", 6))
ARMS = os.environ.get("ARMS", "0.0,0.3,0.6,0.9,PI").split(",")
EPS = 0.15
PRIOR = float(os.environ.get("PRIOR", 0.01))
# CREDIT=orig: royalty credited to whatever move the origin made this round (iter25 run; discovery never sees its pay).
# CREDIT=fixed: royalty credited to the DISCOVER estimate, the move that earned it.
CREDIT = os.environ.get("CREDIT", "orig")
RULE = np.random.default_rng(4321).integers(0, 2, size=K)
MODULES = tuple(int(x) for x in os.environ.get("MODULES", "32,16").split(","))


def onehot(c):
    return np.eye(K)[[c]]


class Peer:
    def __init__(self, seed, slice_):
        from cadence import Brain, ArousalConfig
        self.b = Brain.compose(inputs=K, actions=2, modules=MODULES, seed=seed, arousal=ArousalConfig())
        self.reward = None
        self.known = set(int(c) for c in slice_)
        self.notes = {int(c): int(RULE[c]) for c in slice_}
        self.origin = {int(c): None for c in slice_}          # None = founder knowledge (no pedigree)
        self.found = set()                                    # items this brain got by a Discover move
        for t in range(len(slice_) * 400):
            c = int(slice_[t % len(slice_)])
            self.live(c, lambda a, c=c: 1.0 if a == RULE[c] else -1.0)

    def live(self, c, judge):
        a = self.b.live(onehot(c)) if self.reward is None else self.b.live(
            onehot(c), reward=self.reward, done=np.array([True]))
        a = int(np.asarray(a).reshape(-1)[0])
        self.reward = np.array([judge(a)])
        return a

    def answers(self):
        import tempfile
        from cadence import Brain
        with tempfile.TemporaryDirectory() as d:
            cp = Brain.load(self.b.save(os.path.join(d, "p.npz")))
        out = []
        for c in range(K):
            cp.reset()
            out.append(int(np.asarray(cp.act(onehot(c), greedy=True)).reshape(-1)[0]))
        return np.array(out)


def run(args):
    arm, seed = args
    rng = np.random.default_rng(2000 + seed)
    perm = rng.permutation(K)
    peers = [Peer(20_000 * (seed + 1) + i, perm[i * SLICE:(i + 1) * SLICE]) for i in range(N)]
    alpha = 0.3 if arm == "PI" else float(arm)
    integ = 0.0
    avg = [{"T": PRIOR, "D": PRIOR} for _ in range(N)]
    pay_sum = [{"T": PRIOR, "D": PRIOR} for _ in range(N)]     # CREDIT=item: decayed pay per move type
    mv_cnt = [{"T": 1.0, "D": 1.0} for _ in range(N)]          # decayed move counts (PRIOR = one pseudo-move)
    dpay, nD, nT = [], [], []
    avgc = [{"own": PRIOR, "relay": PRIOR} for _ in range(N)]      # what teaching OWN vs RELAYED items paid
    content = ["own"] * N
    relay_share = []
    estT, estD, roy, direct, droy, novel = [], [], [], [], [], []
    discoverer = {}                                              # item -> brain that found it first (network-new)
    ans = [p.answers() for p in peers]
    acc, alphas, disc_share, net_known = [float(np.mean([np.mean(a == RULE) for a in ans]))], [], [], []
    for r in range(ROUNDS):
        known_any = set().union(*[p.known for p in peers])
        unknown_frac = 1 - len(known_any) / K
        moves = []
        for i in range(N):
            if rng.random() < EPS:
                moves.append("T" if rng.random() < .5 else "D")
            else:
                moves.append("T" if avg[i]["T"] >= avg[i]["D"] else "D")
        earned = [0.0] * N
        royalty = [0.0] * N
        disc_roy = [0.0] * N                                     # royalty on items this brain DISCOVERED
        found_pay = [0.0] * N                                    # ALL pay on items this brain found (own teach + royalty)
        new_items = 0
        for i in range(N):
            P = peers[i]
            if moves[i] == "D":
                cand = [c for c in range(K) if c not in P.known]
                if not cand:
                    continue
                c = int(rng.choice(cand))
                for _ in range(D):
                    P.live(c, lambda a, c=c: 1.0 if a == RULE[c] else -1.0)
                ans[i] = P.answers()
                if ans[i][c] == RULE[c]:
                    P.known.add(c); P.notes[c] = int(RULE[c]); P.origin[c] = i; P.found.add(c)
                    if c not in known_any and c not in discoverer:
                        discoverer[c] = i; new_items += 1
                continue
            fresh = [c for c in P.known if ans[i][c] == P.notes[c]]
            own = [c for c in fresh if P.origin.get(c) in (None, i)]
            rel = [c for c in fresh if P.origin.get(c) not in (None, i)]
            if rng.random() < EPS:
                pick = "own" if rng.random() < .5 else "relay"
            else:
                pick = "own" if avgc[i]["own"] >= avgc[i]["relay"] else "relay"
            pool = sorted(own if (pick == "own" and own) or not rel else rel)
            if not pool:
                content[i] = None
                continue
            content[i] = "own" if pool == sorted(own) and own else "relay"
            need = [len(set(pool) - peers[j].known) if j != i else -1 for j in range(N)]
            s = int(rng.choice(np.flatnonzero(np.array(need) == max(need))))
            S = peers[s]
            before = float(np.mean(ans[s] == RULE))
            tans = ans[i]
            for _ in range(M):
                c = int(rng.choice(pool))
                S.live(c, lambda a, c=c: 1.0 if a == tans[c] else -1.0)
            if S.known:
                reh = sorted(S.known)
                for _ in range(M // 2):
                    c = int(rng.choice(reh))
                    S.live(c, lambda a, c=c: 1.0 if a == S.notes[c] else -1.0)
            ans[s] = S.answers()
            gain = float(np.mean(ans[s] == RULE)) - before
            newly = [c for c in pool if ans[s][c] == tans[c] and c not in S.known]
            for c in newly:
                S.known.add(c); S.notes[c] = int(tans[c])
                S.origin[c] = P.origin.get(c) if P.origin.get(c) is not None else i
            if newly:
                per = gain / len(newly)
                for c in newly:
                    o = P.origin.get(c)
                    if o is None or o == i:
                        earned[i] += per
                        if c in P.found:
                            found_pay[i] += per
                    else:
                        earned[i] += (1 - alpha) * per
                        earned[o] += alpha * per
                        royalty[o] += alpha * per
                        if discoverer.get(c) == o:
                            disc_roy[o] += alpha * per
                        if c in peers[o].found:
                            found_pay[o] += alpha * per
            else:
                earned[i] += gain
        for i in range(N):
            if moves[i] == "T" and content[i] is not None:
                x = earned[i] - disc_roy[i] if CREDIT == "fixed" else (earned[i] - found_pay[i] if CREDIT == "item" else earned[i])
                avgc[i][content[i]] = 0.7 * avgc[i][content[i]] + 0.3 * x
        teach_moves = [i for i in range(N) if moves[i] == "T" and content[i] is not None]
        relay_share.append(sum(content[i] == "relay" for i in teach_moves) / max(1, len(teach_moves)))
        for i in range(N):
            # each brain's estimate of what each move pays: credit this round's earnings to the move it made
            if CREDIT == "item":
                for k in ("T", "D"):
                    pay_sum[i][k] *= 0.9; mv_cnt[i][k] *= 0.9
                pay_sum[i]["D"] += found_pay[i]
                pay_sum[i]["T"] += earned[i] - found_pay[i]
                mv_cnt[i][moves[i]] += 1.0
                for k in ("T", "D"):
                    avg[i][k] = pay_sum[i][k] / mv_cnt[i][k]
            elif CREDIT == "fixed":
                # Discover's outcome is its later royalty: score D only when that royalty arrives (any sign),
                # never at the moment of the move (pending outcome). Everything else is Teach's pay.
                if disc_roy[i] != 0:
                    avg[i]["D"] = 0.7 * avg[i]["D"] + 0.3 * disc_roy[i]
                if moves[i] == "T":
                    avg[i]["T"] = 0.7 * avg[i]["T"] + 0.3 * (earned[i] - disc_roy[i])
            else:
                avg[i][moves[i]] = 0.7 * avg[i][moves[i]] + 0.3 * earned[i]
        estT.append(float(np.mean([a["T"] for a in avg]))); estD.append(float(np.mean([a["D"] for a in avg])))
        roy.append(float(sum(royalty))); direct.append(float(sum(earned) - sum(royalty)))
        droy.append(float(sum(disc_roy))); novel.append(new_items)
        dpay.append(float(sum(found_pay))); nD.append(moves.count("D")); nT.append(moves.count("T"))
        dshare = moves.count("D") / N
        if arm == "PI":
            # positional PI with anti-windup (2026-10-10; the old velocity form sat at .95 then wound down)
            err = unknown_frac - dshare
            raw = 0.3 + 0.4 * err + 0.05 * (integ + err)
            if 0.0 < raw < 0.95:
                integ += err
            alpha = float(np.clip(raw, 0.0, 0.95))
        alphas.append(alpha); disc_share.append(dshare)
        net_known.append(len(set().union(*[p.known for p in peers])) / K)
        acc.append(float(np.mean([np.mean(a == RULE) for a in ans])))
    return dict(arm=arm, seed=seed, acc=acc, alpha=alphas, disc=disc_share, net_known=net_known, relay=relay_share, estT=estT, estD=estD, royalty=roy, direct=direct, disc_royalty=droy, novel=novel, found_pay=dpay, nD=nD, nT=nT,
                prior=PRIOR, credit=CREDIT, cadence=_cadence_version())


def _cadence_version():
    try:
        import cadence
        return getattr(cadence, "__version__", "?")
    except Exception:
        return "?"


def main():
    t0 = time.time()
    # per-job checkpoint: a killed run resumes instead of losing everything (2026-10-09 crash at 29 min)
    ckpt = os.path.join(HERE, f"EXP-35b-K{K}-R{ROUNDS}-{CREDIT}.jsonl")
    res = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["arm"], r["seed"]) for r in res}
    jobs = [(a, s) for a in ARMS for s in range(SEEDS) if (a, s) not in done]
    print(f"resuming: {len(done)} done, {len(jobs)} to run", flush=True)
    with get_context("spawn").Pool(int(os.environ.get("WORKERS", 6))) as pool:
        for r in pool.imap_unordered(run, jobs):
            res.append(r)
            with open(ckpt, "a") as f:
                f.write(json.dumps(r) + "\n")
            print(f"  done {r['arm']} seed {r['seed']}  ({time.time()-t0:.0f}s)", flush=True)
    res = [r for r in res if r["arm"] in ARMS and r["seed"] < SEEDS]
    print(f"EXP-35b pedigree controller  N={N} K={K} rounds={ROUNDS} seeds={SEEDS} D={D}  ({time.time()-t0:.0f}s)")
    for a in ARMS:
        rs = [r for r in res if r["arm"] == a]
        curves = np.array([r["acc"] for r in rs])
        fin = curves[:, -1]
        auc = curves.mean(1)
        print(f"  alpha {a:4s} final {fin.mean():.3f} (SEM {fin.std(ddof=1)/len(fin)**.5:.3f})  mean-over-time {auc.mean():.3f}  "
              f"network-knows {np.mean([r['net_known'][-1] for r in rs]):.2f}  discovering {np.mean([np.mean(r['disc']) for r in rs]):.2f}  relaying {np.mean([np.mean(r['relay']) for r in rs]):.2f}"
              + (f"  est T/D {np.mean([np.mean(r['estT']) for r in rs]):.4f}/{np.mean([np.mean(r['estD']) for r in rs]):.4f}  royalty {np.mean([np.sum(r['royalty']) for r in rs]):.3f} direct {np.mean([np.sum(r['direct']) for r in rs]):.3f}" if "estT" in rs[0] else "")
              + (f"  new-discoveries {np.mean([np.sum(r['novel']) for r in rs]):.1f}  disc-royalty {np.mean([np.sum(r['disc_royalty']) for r in rs]):.3f}" if "novel" in rs[0] else "")
              + (f"  alpha path {' '.join(f'{x:.2f}' for x in np.mean([r['alpha'] for r in rs], 0)[::4])}" if a == "PI" else ""))
    json.dump(res, open(os.path.join(HERE, f"EXP-35b-K{K}-R{ROUNDS}-{CREDIT}.json"), "w"))


if __name__ == "__main__":
    main()
