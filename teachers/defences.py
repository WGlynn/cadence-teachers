"""Need defences: who gets the next lesson in the attack market (teachers.market).

Every honest teacher teaches the student with the highest need; ties are broken by the market's rng. A defence
decides what "need" means. It sees only what the protocol can see, a NeedView per candidate student:
  student, teacher : brain indices (the teacher never sees itself as a candidate)
  missing          : items in the teacher's fresh pool that the protocol probe says the student lacks. The probe
                     reads a committed copy of the student, so only a probe-detecting sandbagger can fake this
  passed           : items the student answered right in a post-lesson test (any teacher's pool, so far). After-tests
                     are not sandbaggable: a sandbagger must show skill there to get its partner paid
  given, received  : lessons the student has given and received so far
  repeat_claims    : times so far the probe said the student lacks an item it had already passed (EXP-38)
  repeat_probes    : passed items probed so far, this probe included; repeat rate = repeat_claims / repeat_probes
Honest brains repeat-claim only when they really forgot (EXP-33: forgetting ~.01-.04).

A defence is any object with .name (str) and .need(view) -> float. Higher need = taught first. The protocol parts
(probe, once-per-(student, item) pay ledger, colluder always teaching its partner) are fixed by the market and are
not a defence choice.

The published defences copy the EXP-36/38 need formulas exactly, float operation order included, so a library run
gives the same numbers as the experiment script from the same seed (checked at seed 0 for every arm in
teachers.market.ARMS, 2026-10-10, Cadence 0.80.0).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class NeedView:
    student: int
    teacher: int
    missing: frozenset[int]
    passed: frozenset[int]
    given: int
    received: int
    repeat_claims: int
    repeat_probes: int


class Defence(Protocol):
    name: str

    def need(self, view: NeedView) -> float: ...


class Neediest:
    """No defence beyond probe + ledger: need = items missing (EXP-36 PROBE+LEDGER and SMART)."""
    name = "NEEDIEST"

    def need(self, v: NeedView) -> float:
        return float(len(v.missing))


class Recip:
    """Reciprocity (EXP-36/38 RECIP): need weighted by (1 + given) / (1 + received), so free-riders (never teach)
    and lesson-soakers sink in the queue."""
    name = "RECIP"

    def need(self, v: NeedView) -> float:
        return len(v.missing) * (1 + v.given) / (1 + v.received)


class Repeat:
    """Repeat-need (EXP-38 REPEAT): RECIP, and items the student has already passed are not its need (no second
    lesson on a passed item)."""
    name = "REPEAT"

    def need(self, v: NeedView) -> float:
        return len(v.missing - v.passed) * (1 + v.given) / (1 + v.received)


class RepeatRate:
    """Repeat rate (EXP-38 REPEAT+RATE): REPEAT, and need is also scaled by (1 - repeat rate), so a brain that
    habitually re-claims sinks for everything, not just its repeats. Same float order as EXP-38: n * (1 - rc / rp)
    first, then * (1 + given) / (1 + received), left to right."""
    name = "REPEAT+RATE"

    def need(self, v: NeedView) -> float:
        n = len(v.missing - v.passed)
        if v.repeat_probes:
            n = n * (1 - v.repeat_claims / v.repeat_probes)
        return n * (1 + v.given) / (1 + v.received)
