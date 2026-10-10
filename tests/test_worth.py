"""Twin-ablation worth (teachers/worth.py) on a stand-in learner: call order, the EXP-19 interleave + null fill
schedule, values relative to the empty coalition, and that the original is never taught. Fast; no Cadence
(tests/test_core.py runs the same functions on real brains)."""
import pytest

from teachers.credit import MAX_PLAYERS, shapley
from teachers.worth import coalition_scores, coalition_values, twin_worth


class Tape:
    """Learner stand-in: a twin copies the tape of lesson units lived so far; every call is logged in `events`."""

    def __init__(self, tape=(), events=None):
        self.tape = list(tape)
        self.events = [] if events is None else events

    def twin(self):
        self.events.append("twin")
        return Tape(self.tape, self.events)


def unit(name):
    """A one-unit lesson that writes its name on the tape."""
    def lesson(learner):
        learner.tape.append(name)
        learner.events.append(name)
    return lesson


def length(learner):
    learner.events.append("score")
    return float(len(learner.tape))


def interleave(x, y):
    """exp/EXP-19_keydoor_teamwork.py interleave() (verbatim)."""
    out = []
    for p, q in zip(x, y):
        out += [p, q]
    return out


# ---------------- twin_worth ----------------
def test_twin_worth_order_and_original_untouched():
    learner = Tape(["founder"])
    assert twin_worth(learner, unit("x"), length) == 1.0
    assert learner.tape == ["founder"]
    assert learner.events == ["twin", "score", "twin", "x", "score"]   # untaught scored first, as EXP-08


def test_twin_worth_of_empty_lesson_is_exactly_zero():
    assert twin_worth(Tape(), lambda learner: None, length) == 0.0


# ---------------- coalition schedule ----------------
def test_schedule_is_exp19_interleave_with_null_fill():
    N, seen = 3, []

    def record(learner):
        seen.append(learner.tape)
        return 0.0

    lessons = {"A": unit("A"), "B": unit("B")}
    raw = coalition_scores(Tape(), lessons, record, ["A", "B"], rounds=N, null=unit("0"))
    exp19 = {                                                  # EXP-19's COALITIONS, in its order
        "null": interleave("0" * N, "0" * N),
        "A": interleave("A" * N, "0" * N),
        "B": interleave("0" * N, "B" * N),
        "AB": interleave("A" * N, "B" * N),
    }
    assert seen == list(exp19.values())
    assert list(raw) == [frozenset(), frozenset("A"), frozenset("B"), frozenset("AB")]


def test_three_slots_and_no_filler():
    seen = {}

    def record(learner):
        seen[frozenset(t for t in learner.tape if t != "0")] = "".join(learner.tape)
        return 0.0

    lessons = {p: unit(p) for p in "ABC"}
    coalition_scores(Tape(), lessons, record, rounds=2, null=unit("0"))
    assert seen[frozenset("AC")] == "A0CA0C"
    assert seen[frozenset()] == "000000"
    coalition_scores(Tape(), lessons, record, rounds=2)             # null=None: absent slots stay empty
    assert seen[frozenset("AC")] == "ACAC" and seen[frozenset()] == ""


def test_each_coalition_gets_a_fresh_twin_of_the_original():
    learner, seen = Tape(["f"]), []

    def record(t):
        seen.append(tuple(t.tape))
        return 0.0

    coalition_scores(learner, {"A": unit("A"), "B": unit("B")}, record)
    assert learner.tape == ["f"]
    assert learner.events.count("twin") == 4
    assert seen == [("f",), ("f", "A"), ("f", "B"), ("f", "A", "B")]   # nothing carries over between coalitions


def test_values_are_relative_to_the_empty_coalition():
    weight = {"A": 0.25, "B": 0.5, "0": 0.125}

    def score(t):
        return sum(weight[u] for u in t.tape) + 3.0

    lessons = {"A": unit("A"), "B": unit("B")}
    raw = coalition_scores(Tape(), lessons, score, rounds=2, null=unit("0"))
    v = coalition_values(Tape(), lessons, score, rounds=2, null=unit("0"))
    assert v[frozenset()] == 0.0
    assert all(v[s] == raw[s] - raw[frozenset()] for s in raw)
    assert v[frozenset("A")] == 2 * (0.25 - 0.125)               # A replaced two null units


def test_single_player_value_is_twin_worth():
    a, b = Tape(["f"]), Tape(["f"])
    v = coalition_values(a, {"x": unit("x")}, length)
    assert v[frozenset({"x"})] == twin_worth(b, unit("x"), length)
    assert a.events == b.events                                   # same twin / lesson / score order


def test_values_feed_credit():
    """An additive stand-in game: Shapley gives each lesson its own worth, straight from the dict."""
    worth = {"A": 0.25, "B": 0.5, "C": -0.125}
    lessons = {p: unit(p) for p in worth}
    v = coalition_values(Tape(), lessons, lambda t: sum(worth[u] for u in t.tape))
    phi = shapley(list(worth), v)
    assert all(abs(phi[p] - worth[p]) <= 1e-12 for p in worth)


def test_bad_inputs_fail_loud():
    lessons = {"A": unit("A")}
    with pytest.raises(KeyError):
        coalition_values(Tape(), lessons, length, ["A", "B"])
    with pytest.raises(ValueError):
        coalition_values(Tape(), lessons, length, ["A", "A"])
    with pytest.raises(ValueError):
        coalition_values(Tape(), lessons, length, rounds=0)
    many = {i: unit(str(i)) for i in range(MAX_PLAYERS + 1)}
    with pytest.raises(ValueError):
        coalition_values(Tape(), many, length)
