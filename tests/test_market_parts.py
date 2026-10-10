"""Fast checks of the attack market's parts, no Cadence run: the defences against EXP-38's inline need formulas
(exact float equality) and the sandbagger's probe answers."""
import numpy as np
import pytest

from teachers.attackers import FAKE, HONEST, SAND, probe
from teachers.defences import NeedView, Neediest, Recip, Repeat, RepeatRate
from teachers.market import run_market


def exp38_need(mode, pool, claims, passed, given, received, rc, rp):
    """One student's need as exp/EXP-38_repeat_need.py computes it (the j != t branch), same expressions."""
    if mode == "RECIP":
        n = len(set(pool) - claims)
    else:
        n = len(set(pool) - claims - passed)
        if mode in ("REPEAT+RATE", "ADAPT"):
            n = n * (1 - rc / rp) if n >= 0 and rp else n
    return n * (1 + given) / (1 + received) if n >= 0 else -1


@pytest.mark.parametrize("defence", [Recip(), Repeat(), RepeatRate()], ids=lambda d: d.name)
def test_defence_matches_exp38_formula_exactly(defence):
    rng = np.random.default_rng(38)
    for _ in range(3000):
        pool = {int(c) for c in rng.choice(32, size=rng.integers(1, 9), replace=False)}
        claims = {int(c) for c in np.flatnonzero(rng.random(32) < .5)}
        passed = {int(c) for c in np.flatnonzero(rng.random(32) < .3)}
        given, received = int(rng.integers(0, 30)), int(rng.integers(0, 30))
        rp = int(rng.integers(0, 300))
        rc = int(rng.integers(0, rp + 1))
        view = NeedView(student=1, teacher=0, missing=frozenset(pool - claims), passed=frozenset(passed),
                        given=given, received=received, repeat_claims=rc, repeat_probes=rp)
        assert defence.need(view) == exp38_need(defence.name, pool, claims, passed, given, received, rc, rp)


def test_neediest_is_items_missing():
    view = NeedView(student=1, teacher=0, missing=frozenset({3, 5, 8}), passed=frozenset({3}), given=0,
                    received=4, repeat_claims=2, repeat_probes=2)
    assert Neediest().need(view) == 3.0


def test_probe_answers():
    a = np.array([0, 1, 1, 0, 1])
    passed = {1, 3}
    for i in HONEST + (FAKE,):                 # only the sandbagger lies
        for attacker in ("naive", "smart", "adaptive"):
            assert probe(i, a, passed, attacker) is a
    assert probe(SAND, a, passed, "naive") is a
    assert probe(SAND, a, passed, "smart").tolist() == [1, 0, 0, 1, 0]
    assert probe(SAND, a, passed, "adaptive").tolist() == [1, 1, 0, 0, 0]   # honest on passed items 1 and 3
    assert a.tolist() == [0, 1, 1, 0, 1]       # the real answers are never mutated


def test_unknown_attacker_is_rejected_before_any_run():
    with pytest.raises(ValueError):
        run_market(Recip(), 0, attacker="clever")
