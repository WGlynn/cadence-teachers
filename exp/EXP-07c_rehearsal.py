"""EXP-07c: does rehearsal (one A moment in four during B training) keep both skills when inputs overlap?

Pre-registered in experiments/EXP-07c.md (commit 8ba827c) before any data. Run: python -u exp/EXP-07c_rehearsal.py
Arms: SEQ repeats EXP-07b's LEARN-B call for call; INTER draws the same cue indices but every 4th moment is an A cue;
REF is a fresh brain on B only (learnability filter).
"""
import copy
import json
import os
import sys
import time

import numpy as np

import cadence
from cadence import Brain

SEEDS = int(os.environ.get("SEEDS", "20"))
BASE = 7_071_000
N_A, N_B = 200, 200
EVERY = 4  # INTER: moment k is an A moment when k % EVERY == EVERY - 1


def _two_hot(i, ctx):
    v = np.zeros(6)
    v[i] = 1.0
    v[ctx] = 1.0
    return v


# Same cues as EXP-07b. Rows 0-3 are A (cue i = {i, 4 if i < 2 else 5}), rows 4-7 are B (the other context).
CUES = np.array([_two_hot(i, 4 if i < 2 else 5) for i in range(4)] + [_two_hot(i, 5 if i < 2 else 4) for i in range(4)])
A_CUES, B_CUES = [0, 1, 2, 3], [4, 5, 6, 7]


def live(brain, cue, reward=None):
    """One `live` call under the documented refusal contract (docs/start.md, Qualification and refusal)."""
    obs = CUES[[cue]]
    for _ in range(5):
        try:
            if reward is None:
                return int(brain.live(obs)[0])
            return int(brain.live(obs, reward=np.array([float(reward)]))[0])
        except RuntimeError:
            if not brain.pending_feedback:
                reward = None
    raise RuntimeError("no settled answer in 5 tries")


def rule_for(rng):
    return {int(c): a for c, a in zip(rng.permutation(4), [0, 0, 1, 1])}


def answers(brain, pending_reward):
    """The brain's answer to each of the 8 cues, each from a fresh copy that first gets the true pending outcome."""
    return [live(copy.deepcopy(brain), c, pending_reward) for c in A_CUES + B_CUES]


def score(ans, rule_a, rule_b):
    a = sum(int(ans[i] == rule_a[i]) for i in range(4)) / 4
    b = sum(int(ans[4 + i] == rule_b[i]) for i in range(4)) / 4
    return a, b


def klass(ans, a, b):
    """EXP-07b's split: kept both / overwrote / one answer for all / partial."""
    same_pairs = sum(int(ans[i] == ans[4 + i]) for i in range(4))
    if len(set(ans)) == 1:
        return "collapse"
    if same_pairs == 0:
        return "kept_both"
    if same_pairs == 4:
        return "overwrote" if b == 1.0 else "same_pairs_other"
    return "partial"


def train(brain, rng, cues, rule, n, pending_reward):
    """EXP-07b's train, unchanged: n moments on random cues of one skill. Returns the outcome still owed."""
    for _ in range(n):
        i = int(rng.integers(len(cues)))
        a = live(brain, cues[i], pending_reward)
        pending_reward = 1.0 if a == rule[i] else -1.0
    return pending_reward


def train_inter(brain, rng, rule_a, rule_b, n, pending_reward):
    """Same index draws as train(B); moment k uses A cue i instead of B cue i when k % EVERY == EVERY - 1."""
    n_a = 0
    for k in range(n):
        i = int(rng.integers(4))
        if k % EVERY == EVERY - 1:
            a = live(brain, A_CUES[i], pending_reward)
            pending_reward = 1.0 if a == rule_a[i] else -1.0
            n_a += 1
        else:
            a = live(brain, B_CUES[i], pending_reward)
            pending_reward = 1.0 if a == rule_b[i] else -1.0
    return pending_reward, n_a


def run(s):
    rng = np.random.default_rng(BASE + s)
    rule_a = rule_for(rng)
    rule_b = {i: 1 - a for i, a in rule_a.items()}
    brain = Brain.compose(inputs=6, actions=2, arousal=True, seed=BASE + s)
    # EXP-07b also examined B at birth here; exam copies do not touch the brain or the stream, so skipping it is safe.
    owed = train(brain, rng, A_CUES, rule_a, N_A, None)
    a_before, _ = score(answers(brain, owed), rule_a, rule_b)
    fork_state = copy.deepcopy(rng.bit_generator.state)

    seq = copy.deepcopy(brain)                       # SEQ: EXP-07b's LEARN-B, continuing the same stream
    owed_s = train(seq, rng, B_CUES, rule_b, N_B, owed)
    ans_s = answers(seq, owed_s)
    a_s, b_s = score(ans_s, rule_a, rule_b)

    rng_i = np.random.default_rng(); rng_i.bit_generator.state = copy.deepcopy(fork_state)
    inter = copy.deepcopy(brain)                     # INTER: same index draws, every 4th an A moment
    owed_i, n_a = train_inter(inter, rng_i, rule_a, rule_b, N_B, owed)
    ans_i = answers(inter, owed_i)
    a_i, b_i = score(ans_i, rule_a, rule_b)

    rng_r = np.random.default_rng(); rng_r.bit_generator.state = copy.deepcopy(fork_state)
    ref = Brain.compose(inputs=6, actions=2, arousal=True, seed=BASE + s)   # REF: fresh brain, B only
    owed_r = train(ref, rng_r, B_CUES, rule_b, N_B, None)
    _, b_ref = score(answers(ref, owed_r), rule_a, rule_b)

    return dict(seed=BASE + s, a_before=a_before, b_ref=b_ref, passes=bool(a_before >= 0.75 and b_ref >= 0.75),
                seq=dict(a=a_s, b=b_s, ans=ans_s, cls=klass(ans_s, a_s, b_s)),
                inter=dict(a=a_i, b=b_i, ans=ans_i, cls=klass(ans_i, a_i, b_i), a_moments=n_a))


def main():
    t0 = time.time()
    print(f"EXP-07c rehearsal on cadence {cadence.__version__}: {SEEDS} seeds, A {N_A}, then B {N_B} (SEQ) or "
          f"B with every {EVERY}th moment A (INTER); REF fresh B-only", flush=True)
    ref07b = None
    p07b = os.path.join(os.path.dirname(__file__), "EXP-07b-f84125e.json")
    if os.path.exists(p07b):
        ref07b = {r["seed"]: r for r in json.load(open(p07b))["rows"]}
    rows, mismatch = [], 0
    for s in range(SEEDS):
        r = run(s)
        rows.append(r)
        if ref07b is not None:
            o = ref07b[r["seed"]]
            if (o["a_before"], o["a_after"], o["b_after"]) != (r["a_before"], r["seq"]["a"], r["seq"]["b"]):
                mismatch += 1
        print(f"  seed {r['seed']}: A before {r['a_before']:.2f}  REF B {r['b_ref']:.2f}  pass {int(r['passes'])}  |  "
              f"SEQ A {r['seq']['a']:.2f} B {r['seq']['b']:.2f} {r['seq']['cls']:<9} |  "
              f"INTER A {r['inter']['a']:.2f} B {r['inter']['b']:.2f} {r['inter']['cls']}", flush=True)
    f = [r for r in rows if r["passes"]]
    n_f = len(f)
    a_s = np.array([r["seq"]["a"] for r in f]); a_i = np.array([r["inter"]["a"] for r in f])
    b_s = np.array([r["seq"]["b"] for r in f]); b_i = np.array([r["inter"]["b"] for r in f])
    diff = a_i - a_s
    sem = diff.std(ddof=1) / np.sqrt(n_f) if n_f > 1 else float("nan")
    if ref07b is None:
        repro = "EXP-07b json missing, reproduction not checked"
    else:
        repro = f"SEQ vs EXP-07b per-seed mismatches: {mismatch}/{SEEDS}"
    if n_f < 8 or (ref07b is not None and mismatch > 0):
        verdict = "VOID"
    elif diff.mean() >= 0.25 and a_i.mean() >= 0.75 and b_i.mean() >= 0.75:
        verdict = "SUPPORTIVE"
    elif diff.mean() <= 0.10:
        verdict = "NULL"
    else:
        verdict = "INCONCLUSIVE"
    counts = {arm: {c: sum(1 for r in rows if r[arm]["cls"] == c)
                    for c in ["kept_both", "overwrote", "collapse", "partial", "same_pairs_other"]} for arm in ["seq", "inter"]}
    summary = dict(version=cadence.__version__, seeds=SEEDS, filtered=n_f, repro=repro,
                   seq_a=a_s.mean(), seq_b=b_s.mean(), inter_a=a_i.mean(), inter_b=b_i.mean(),
                   diff=diff.mean(), diff_sem=sem, counts=counts, verdict=verdict, seconds=round(time.time() - t0))
    print(repro)
    print(f"FILTERED ({n_f}/{SEEDS}): SEQ A {a_s.mean():.3f} B {b_s.mean():.3f} | INTER A {a_i.mean():.3f} "
          f"B {b_i.mean():.3f} | A diff INTER-SEQ {diff.mean():+.3f} (SEM {sem:.3f})")
    print(f"CLASSES (all {SEEDS}): SEQ {counts['seq']}  INTER {counts['inter']}")
    print(f"VERDICT: {verdict}  ({summary['seconds']} s)")
    tag = os.environ.get("TAG", "run")
    json.dump(dict(summary=summary, rows=rows), open(os.path.join(os.path.dirname(__file__), f"EXP-07c-{tag}.json"), "w"),
              indent=1, default=float)


if __name__ == "__main__":
    sys.exit(main())
