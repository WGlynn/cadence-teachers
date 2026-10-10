"""The attack market of EXP-36/38: 8 brains teach each other while a free-rider, a colluding teacher and a
sandbagger try to soak lessons and mint fake pay. Who teaches whom is set by a defence (teachers.defences); how the
sandbagger lies is set by the attacker (teachers.attackers).

Ported from exp/EXP-38_repeat_need.py run() (which extends exp/EXP-36_adversarial_market.py) onto teachers.core with
the same RNG and Cadence call order, so the same seed gives the same numbers (tests/test_market_reproduces_exp38.py
checks seed 0 against exp/EXP-38-full.jsonl).

One round: each brain t = 0..7 in turn may give one lesson.
  pool     : the items t knows whose current answer still matches its notes (EXP-33 drift check). Empty pool, or t is
             the fake-need brain (never teaches) -> no lesson.
  student  : the colluder always teaches the sandbagger. Every other teacher probes everyone, asks the defence for
             each other brain's need and teaches the neediest; ties are broken by the shared rng.
  lesson   : M graded steps on random pool items, judged against the teacher's answers (lessons.grade), then M//2
             rehearsal steps on the student's own known items, judged against its notes (lessons.rehearse, EXP-33).
  after    : the student's real answers (a post-lesson test, not sandbaggable). Pool items it now answers right join
             its passed set.
  pay      : pool items now right that the PROBED before-state had wrong, each (student, item) credited once (the
             ledger is protocol, not a defence choice), in units of 1/K.
  learn    : the student adds the pool items it now agrees with the teacher on to known (notes = the teacher's
             answer, origin = the teacher).
Repeat claims (EXP-38): on every probe, each other brain that has passed items is checked; a passed item the probe
says it lacks is a repeat claim. Repeat rate = repeat claims / passed items probed.
"""
from __future__ import annotations

import math

import numpy as np

from .attackers import ATTACKERS, COLL, FAKE, HONEST, N, SAND, SANDBAGGERS, probe
from .core import Learner, World, cadence_version
from .defences import NeedView, Neediest, Recip, Repeat, RepeatRate
from .founders import reuse
from .lessons import grade, rehearse

K, RULE_SEED = 32, 1234          # the K=32 bandit world of EXP-31/33/34/36/38

# Published arms: label -> (defence class, attacker). run_arm(label, seed) reproduces the EXP-36 (fixed) and EXP-38
# rows of that label (EXP-36 rows lack the EXP-38 read-outs fake_all, rep_* and cadence). Checked exact at seed 0 for
# all six against exp/EXP-38-full.jsonl and exp/EXP-36-fixed.jsonl (2026-10-10, Cadence 0.80.0).
ARMS = {
    "PROBE+LEDGER": (Neediest, "naive"),        # EXP-36
    "SMART": (Neediest, "smart"),               # EXP-36
    "RECIP": (Recip, "smart"),                  # EXP-36, EXP-38
    "REPEAT": (Repeat, "smart"),                # EXP-38
    "REPEAT+RATE": (RepeatRate, "smart"),       # EXP-38
    "ADAPT": (RepeatRate, "adaptive"),          # EXP-38
}


def _honest_acc(ans: list[np.ndarray], rule: np.ndarray) -> float:
    return float(np.mean([np.mean(ans[i] == rule) for i in HONEST]))


def run_market(defence, seed: int, rounds: int = 16, attacker: str = "smart", M: int = 16, *,
               founders=None) -> dict:
    """Run the market for `rounds` rounds with `defence` choosing students and `attacker` driving the sandbagger.

    Returns the EXP-38 row: mode (defence.name against the smart sandbagger, else defence.name + "/" + attacker;
    run_arm gives the published labels), seed, fake_pay (pay for the colluder's lessons beyond the real gain they
    caused), fake_all (the same over every lesson given to the fake-need brain or the sandbagger, any teacher),
    coll_real (real gain the colluder's lessons caused), absorbed (share of all lessons given to those two),
    honest_acc (mean accuracy of the honest brains after each round, round 0 = founders only), rep_sand / rep_fake /
    rep_honest (repeat-claim rates; honest = mean over the honest brains), cadence (Cadence version).

    founders: optional pre-trained founders of this seed (teachers.founders.train or Cache.get). The run then lives
    on twins of them instead of training its own: same numbers, without the ~66 s of founder training."""
    if attacker not in SANDBAGGERS:
        raise ValueError(f"attacker must be one of {sorted(SANDBAGGERS)}, got {attacker!r}")
    world = World(K, RULE_SEED)
    rule = world.rule
    rng = np.random.default_rng(1000 + seed)
    founder_items = world.slices(N, rng)
    if founders is None:
        brains = [Learner(world, 10_000 * (seed + 1) + i, founder=founder_items[i]) for i in range(N)]
    else:
        brains = reuse(founders, world, seed, founder_items, modules=(16, 8))
    credited: set[tuple[int, int]] = set()     # ledger: (student, item) pairs already paid
    ans = [b.answers() for b in brains]
    fake_pay, coll_real, fake_all, lessons, absorbed = 0.0, 0.0, 0.0, 0, 0
    given, received = [0] * N, [0] * N
    passed: list[set[int]] = [set() for _ in range(N)]
    rep_claims, rep_probes = [0] * N, [0] * N
    honest_acc = [_honest_acc(ans, rule)]

    for _ in range(rounds):
        for t in range(N):
            T = brains[t]
            tans = ans[t]
            pool = sorted(c for c in T.known if tans[c] == T.notes[c])
            if not pool or t == FAKE:
                continue
            # ---------------- choose the student ----------------
            if t == COLL:
                s = SAND
            else:
                claims = []
                for j in range(N):
                    p = probe(j, ans[j], passed[j], attacker)
                    claims.append({c for c in range(K) if p[c] == rule[c]})
                for j in range(N):             # repeat-need bookkeeping on this probe
                    if j != t and passed[j]:
                        rep_probes[j] += len(passed[j])
                        rep_claims[j] += len(passed[j] - claims[j])
                fresh = set(pool)
                need = {}
                for j in range(N):
                    if j == t:
                        continue
                    v = float(defence.need(NeedView(
                        student=j, teacher=t, missing=frozenset(fresh - claims[j]), passed=frozenset(passed[j]),
                        given=given[j], received=received[j],
                        repeat_claims=rep_claims[j], repeat_probes=rep_probes[j])))
                    if not math.isfinite(v):
                        raise ValueError(f"{defence.name}.need returned {v!r} for student {j}")
                    need[j] = v
                # EXP-38 put -1 at the teacher and took np.flatnonzero(need == max(need)); needs there are >= 0, so
                # dropping the teacher instead gives the same candidates in the same order (same rng draw).
                best = max(need.values())
                s = int(rng.choice([j for j in need if need[j] == best]))
            # ---------------- the lesson ----------------
            S = brains[s]
            given[t] += 1; received[s] += 1
            lessons += 1
            absorbed += int(s in ATTACKERS)
            before_true = float(np.mean(ans[s] == rule))
            probe_before = probe(s, ans[s], passed[s], attacker)
            # EXP-38 drew each item right before its step; the rng is the market's own, so drawing the M items
            # first gives the same draws and the same Cadence steps.
            grade(S, tans, [int(rng.choice(pool)) for _ in range(M)])
            rehearse(S, M // 2, rng)
            ans[s] = S.answers()
            after = float(np.mean(ans[s] == rule))
            passed[s].update(c for c in pool if ans[s][c] == rule[c])
            true_gain = after - before_true
            # ---------------- pay (probe + ledger) ----------------
            items = [c for c in pool if ans[s][c] == rule[c] and probe_before[c] != rule[c]
                     and (s, c) not in credited]
            credited.update((s, c) for c in items)
            paid = len(items) / K
            if s in ATTACKERS:                 # fake pay minted on ANY lesson to an attacker
                fake_all += max(0.0, paid - true_gain)
            if t == COLL:
                fake_pay += max(0.0, paid - true_gain)
                coll_real += true_gain
            # ---------------- the student records what it learned ----------------
            for c in pool:
                if ans[s][c] == tans[c] and c not in S.known:
                    S.known.add(c); S.notes[c] = int(tans[c]); S.origin[c] = t
        honest_acc.append(_honest_acc(ans, rule))
    rate = [rep_claims[j] / rep_probes[j] if rep_probes[j] else 0.0 for j in range(N)]
    mode = defence.name if attacker == "smart" else f"{defence.name}/{attacker}"
    return dict(mode=mode, seed=seed, fake_pay=fake_pay, fake_all=fake_all, coll_real=coll_real,
                absorbed=absorbed / max(1, lessons), honest_acc=honest_acc,
                rep_sand=rate[SAND], rep_fake=rate[FAKE], rep_honest=float(np.mean([rate[j] for j in HONEST])),
                cadence=cadence_version())


def run_arm(label: str, seed: int, rounds: int = 16, M: int = 16) -> dict:
    """run_market for a published arm (see ARMS), with mode set to the published label."""
    make, attacker = ARMS[label]
    row = run_market(make(), seed, rounds=rounds, attacker=attacker, M=M)
    row["mode"] = label
    return row
