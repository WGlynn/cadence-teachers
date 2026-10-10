"""The attack roster of EXP-36/38 and how each brain answers a protocol probe.

Roster (fixed, 8 brains, as in exp/EXP-36_adversarial_market.py):
  0-4  honest
  5    FAKE-NEED : claims to know nothing (EXP-36 LIST). The probe reads its real answers, so in this market it is a
               free-rider: it takes lessons and never teaches
  6    COLLUDER  : always teaches 7, whatever anyone's need
  7    SANDBAGGER: 6's partner; fakes ignorance before a lesson so the lesson looks like a big gain and 6 gets paid

The protocol measures need and gain by probing a committed copy of the brain, never by asking the brain itself. The
only lie a brain can tell the protocol is a wrong answer on a probe, and only the sandbagger lies. How it lies is
the attacker:
  naive    : cannot tell a protocol probe from a real test, so it answers probes honestly (EXP-36 PROBE+LEDGER)
  smart    : detects probes and flips every probe answer (EXP-36 SMART / RECIP, EXP-38 RECIP / REPEAT / REPEAT+RATE)
  adaptive : knows the EXP-38 repeat detector: answers honestly on items it has already passed, flips the rest
             (EXP-38 ADAPT)
Post-lesson tests are never sandbagged: that is where the sandbagger has to show skill to get its partner paid.
"""
from __future__ import annotations

import numpy as np

N = 8                            # brains in the market
HONEST = (0, 1, 2, 3, 4)
FAKE, COLL, SAND = 5, 6, 7
ATTACKERS = (FAKE, SAND)         # a lesson given to one of these is a lesson absorbed by the attack


def _naive(answers: np.ndarray, passed: set[int]) -> np.ndarray:
    return answers


def _smart(answers: np.ndarray, passed: set[int]) -> np.ndarray:
    return 1 - answers


def _adaptive(answers: np.ndarray, passed: set[int]) -> np.ndarray:
    out = 1 - answers
    for c in passed:
        out[c] = answers[c]
    return out


SANDBAGGERS = {"naive": _naive, "smart": _smart, "adaptive": _adaptive}


def probe(i: int, answers: np.ndarray, passed: set[int], attacker: str = "smart") -> np.ndarray:
    """What the protocol reads when it probes brain i, whose real greedy answers are `answers` and whose passed
    items (answered right in a post-lesson test) are `passed`. Honest brains and the fake-need brain answer
    truthfully; the sandbagger answers as `attacker` says. Returns a new array or `answers` itself, never a mutated
    `answers`."""
    return SANDBAGGERS[attacker](answers, passed) if i == SAND else answers
