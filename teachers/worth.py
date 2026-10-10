"""Worth by twin ablation: what a lesson is worth to a learner, measured on byte-identical twins.

EXP-08: copy a brain, teach one copy, leave the other, and score both on a held-out task; the difference is the
lesson's worth. The original learner is never touched, so worth can be measured before anyone pays for (or gives)
the lesson for real. Worth is task-specific: `score` is the held-out task, and a lesson that teaches the wrong
thing scores negative (EXP-08 fake_wrong).

coalition_values extends this to several lessons at once (EXP-19): every coalition of lessons is taught to its own
fresh twin in one fixed interleaved order, absent lessons' slots optionally filled with a null lesson, and v(S) is
measured against the twin taught the empty coalition. The result plugs straight into teachers.credit.

A lesson is a callable(Learner) -> None that teaches by living graded steps (Learner.live). Every coalition
receives the same teaching only if lessons replay the same content on every call (e.g. contexts drawn once when
the lesson is built); a lesson that draws fresh randomness per call adds that noise to v(S).
"""
from __future__ import annotations

from collections.abc import Callable, Hashable, Mapping, Sequence
from typing import TYPE_CHECKING

from .credit import MAX_PLAYERS

if TYPE_CHECKING:  # pragma: no cover
    from .core import Learner

Lesson = Callable[["Learner"], None]
Score = Callable[["Learner"], float]


def twin_worth(learner: "Learner", lesson: Lesson, score: Score) -> float:
    """v = score(taught twin) - score(untaught twin); both are learner.twin(), the learner itself is untouched.

    Order: untaught twin made and scored, then taught twin made, taught and scored (EXP-08 scores the baseline
    first). An empty lesson is worth exactly 0.0 whenever score is deterministic (Learner.accuracy is)."""
    base = learner.twin()
    s0 = score(base)
    taught = learner.twin()
    lesson(taught)
    return float(score(taught) - s0)


def coalition_scores(learner: "Learner", lessons: Mapping[Hashable, Lesson], score: Score,
                     players: Sequence[Hashable] | None = None, rounds: int = 1,
                     null: Lesson | None = None) -> dict[frozenset, float]:
    """Raw score of a fresh twin taught each coalition S of `players` (default: the keys of `lessons`). The raw
    score of the empty coalition is worth looking at: in EXP-19 run 1 the null twin already passed the test,
    which is how that degenerate score was caught.

    Schedule (EXP-19 interleave + null fill): the twin lives `rounds` rounds; in each round every slot of
    `players`, in order, delivers one unit: lessons[p] if p is in S, else `null` (null trips: experience without
    information, so every coalition gets the same amount of experience); null=None leaves absent slots empty.
    With two players, rounds=N and a null lesson this is EXP-19's interleave("A"*N, "0"*N) and so on.
    Coalitions run in increasing bitmask order (bit j = players[j]): empty, {p0}, {p1}, {p0, p1}, ... as EXP-19's
    null, A, B, AB; the returned dict keeps that order. Each coalition is twin, teach, score."""
    players = list(lessons) if players is None else list(players)
    n = len(players)
    if len(set(players)) != n:
        raise ValueError(f"players must be distinct, got {players!r}")
    missing = [p for p in players if p not in lessons]
    if missing:
        raise KeyError(f"no lesson for players {missing!r}")
    if n > MAX_PLAYERS:
        raise ValueError(f"{n} players = 2^{n} twins; at most MAX_PLAYERS={MAX_PLAYERS}")
    if rounds < 1:
        raise ValueError(f"rounds must be >= 1, got {rounds}")
    out = {}
    for m in range(1 << n):
        t = learner.twin()
        for _ in range(rounds):
            for j, p in enumerate(players):
                if m >> j & 1:
                    lessons[p](t)
                elif null is not None:
                    null(t)
        out[frozenset(p for j, p in enumerate(players) if m >> j & 1)] = float(score(t))
    return out


def coalition_values(learner: "Learner", lessons: Mapping[Hashable, Lesson], score: Score,
                     players: Sequence[Hashable] | None = None, rounds: int = 1,
                     null: Lesson | None = None) -> dict[frozenset, float]:
    """v(S) = score(twin taught S) - score(twin taught the empty coalition), for every coalition S of `players`.

    Same schedule and arguments as coalition_scores; v(empty) is exactly 0.0. With one player, rounds=1 and no
    null lesson it makes the same calls in the same order as twin_worth(learner, lessons[p], score), so v({p}) is
    the same float. Feed the result to teachers.credit (shapley, leave_one_out, equal_split) directly; they
    accept the dict."""
    raw = coalition_scores(learner, lessons, score, players, rounds, null)
    base = raw[frozenset()]
    return {s: r - base for s, r in raw.items()}
