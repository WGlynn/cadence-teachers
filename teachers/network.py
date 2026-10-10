"""The peer-teaching network: EXP-31's PEER pairing with EXP-33's forgetting fix, built on teachers.core.

N learners share one World (K contexts, rule_seed 1234). Learner i is a founder, trained to mastery on slice i of a
random permutation of the contexts. Every round the learners are paired at random and each pair teaches BOTH ways
(N lessons a round). In a lesson the teacher's policy picks M items from its pool and the student is graded on them
against the teacher's answers (lessons.grade). In arms with rehearse, the student then does M/2 self-practice steps
graded against its own notes (lessons.rehearse). Then the student is probed: every pool item it now answers like the
teacher becomes known to it, noted with the teacher's answer (provenance), with the teacher as its origin.

Arms (EXP-33):
  base     : EXP-31 PEER
  rehearse : + M/2 self-practice steps after each lesson, graded against the student's notes
  drift    : a teacher only teaches items whose current answer still matches its notes (drift check)
  both     : rehearse + drift (the fixed network; EXP-33 final .991, SEM .002, over 6 seeds)
  big      : base with brains twice as large, modules (32, 16)

Measured: mean accuracy of all learners on the true rule after every round (round 0 = founders only, before any
teaching), and forgetting = the share of a student's known items that matched its notes before a lesson and do not
after it, averaged over lessons.

With lessons.RandomTeacher, run_network(policy, seed, 16, arm) reproduces EXP-33's run((arm, seed)) exactly: the same
RNG draws and Cadence calls in the same order (tests/test_network_reproduces_exp33.py).
"""
from __future__ import annotations

import numpy as np

from .core import Learner, World, cadence_version
from .founders import reuse
from .lessons import LessonView, check_lesson, grade, rehearse

ARMS = ("base", "rehearse", "drift", "both", "big")
RULE_SEED = 1234                                   # the EXP-31/33 world


def _mean_accuracy(world: World, answers) -> float:
    """Mean over learners of each learner's accuracy on the true rule (EXP-31/33 'acc')."""
    return float(np.mean([world.accuracy(a) for a in answers]))


def run_network(teacher_policy, seed: int, rounds: int, arm: str = "both", M: int = 16, N: int = 8,
                K: int = 32, modules=None, *, founders=None) -> dict:
    """Run one teaching network for `rounds` rounds, every lesson planned by `teacher_policy`.

    Returns dict(seed, acc, final, mean_over_time, forgetting, cadence, arm, policy):
      acc            : mean accuracy after each round; acc[0] is before any teaching (len = rounds + 1)
      final          : acc[-1]
      mean_over_time : mean of acc including round 0 (EXP-35's mean-over-time; rewards learning fast, not just far)
      forgetting     : mean over lessons of the forgetting share (0.0 if no lesson measured it)
      cadence        : the Cadence version that ran it
    modules overrides the brain size (default: (16, 8), or (32, 16) for arm "big"); used by EXP-40.
    One rng, default_rng(1000 + seed), drives slicing, pairing, lessons and rehearsal in EXP-33's order.
    founders: optional pre-trained founders of this seed and size (teachers.founders.train or Cache.get). The run
    then lives on twins of them instead of training its own: same numbers, without the founder training."""
    if arm not in ARMS:
        raise ValueError(f"arm must be one of {ARMS}, got {arm!r}")
    if N < 2 or N % 2:
        raise ValueError(f"N must be even and >= 2 (learners teach in pairs), got {N}")
    name = str(teacher_policy.name)
    if not callable(getattr(teacher_policy, "lesson", None)):
        raise TypeError(f"teacher policy {name!r} has no lesson(view, rng) method")
    rehearse_on, drift = arm in ("rehearse", "both"), arm in ("drift", "both")
    world = World(K=K, rule_seed=RULE_SEED)
    rng = np.random.default_rng(1000 + seed)
    slices = world.slices(N, rng)
    if modules is None:
        modules = (32, 16) if arm == "big" else (16, 8)
    modules = tuple(int(m) for m in modules)
    if founders is None:
        peers = [Learner(world, 10_000 * (seed + 1) + i, founder=slices[i], modules=modules) for i in range(N)]
    else:
        peers = reuse(founders, world, seed, slices, modules)
    ans = [p.answers() for p in peers]             # current answers; a student is re-probed after each lesson
    acc, forget = [_mean_accuracy(world, ans)], []
    for _ in range(rounds):
        o = rng.permutation(N)
        pairs = []
        for j in range(0, N, 2):
            pairs += [(int(o[j]), int(o[j + 1])), (int(o[j + 1]), int(o[j]))]
        for t, s in pairs:
            T, S, tans = peers[t], peers[s], ans[t]
            pool = tuple(sorted(c for c in T.known if not drift or tans[c] == T.notes[c]))
            if not pool:
                continue
            before_ok = [c for c in S.known if ans[s][c] == S.notes[c]]
            view = LessonView(pool=pool, student_wrong=frozenset(c for c in pool if ans[s][c] != tans[c]), budget=M)
            grade(S, tans, check_lesson(view, teacher_policy.lesson(view, rng)))
            if rehearse_on:
                rehearse(S, M // 2, rng)
            after = S.answers()
            ans[s] = after
            if before_ok:
                forget.append(float(np.mean([after[c] != S.notes[c] for c in before_ok])))
            for c in pool:                         # learned = now answers like the teacher; note it with provenance
                if after[c] == tans[c] and c not in S.known:
                    S.known.add(c)
                    S.notes[c] = int(tans[c])
                    S.origin[c] = t
        acc.append(_mean_accuracy(world, ans))
    return dict(seed=seed, acc=acc, final=acc[-1], mean_over_time=float(np.mean(acc)),
                forgetting=float(np.mean(forget)) if forget else 0.0, cadence=cadence_version(),
                arm=arm, policy=name)
