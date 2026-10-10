"""teachers.founders: a run on reused founders is the same run as one that trains its own.

Fast, on a fake brain (tests/_fake_cadence.py) whose save/load keep the whole state, as Cadence's do. With real
Cadence the same identity was checked on seed 1, 3 rounds: run_market(Repeat, adaptive) and run_network(missing-first)
on cached founders gave rows identical (==) to fresh runs, Cadence 0.80.0, 2026-10-10; the slow test in
tests/test_arena_reproduces.py checks arena runs on cached founders against the published EXP-38 / EXP-33 rows.
"""
import sys

import numpy as np
import pytest

from _fake_cadence import fake
from teachers import founders
from teachers.core import World
from teachers.defences import Recip, Repeat
from teachers.lessons import MissingFirstTeacher, RandomTeacher
from teachers.market import run_market
from teachers.network import run_network


@pytest.fixture
def cadence(monkeypatch):
    monkeypatch.setitem(sys.modules, "cadence", fake())


def _state(learners):
    return [(l.b.q.copy(), l.b.rng.bit_generator.state, l.b.last, None if l.reward is None else l.reward.copy(),
             set(l.known), dict(l.notes), dict(l.origin), set(l.found)) for l in learners]


def _same_state(a, b) -> bool:
    return all(np.array_equal(x[0], y[0]) and x[1:3] == y[1:3] and np.array_equal(x[3], y[3]) and x[4:] == y[4:]
               for x, y in zip(a, b))


@pytest.mark.parametrize("seed", [0, 3])
def test_market_on_reused_founders_is_the_same_run(cadence, seed):
    f = founders.train(World(32, 1234), seed)
    before = _state(f)
    for defence, attacker in [(Recip(), "smart"), (Repeat(), "adaptive"), (Repeat(), "naive")]:
        reused = run_market(defence, seed, rounds=4, attacker=attacker, founders=f)
        assert reused == run_market(defence, seed, rounds=4, attacker=attacker)
    assert _same_state(before, _state(f)), "the founders passed in were changed"


@pytest.mark.parametrize("arm", ["both", "base", "rehearse"])
def test_network_on_reused_founders_is_the_same_run(cadence, arm):
    f = founders.train(World(32, 1234), 2)
    for policy in (RandomTeacher(), MissingFirstTeacher()):
        assert run_network(policy, 2, 4, arm=arm, founders=f) == run_network(policy, 2, 4, arm=arm)


def test_market_and_network_share_founders(cadence):
    """Same seed, same founders: one cache entry serves both tracks."""
    f = founders.train(World(32, 1234), 1)
    assert run_network(RandomTeacher(), 1, 2, founders=f) == run_network(RandomTeacher(), 1, 2)
    assert run_market(Recip(), 1, rounds=2, founders=f) == run_market(Recip(), 1, rounds=2)


def test_cache_trains_once_then_loads(cadence, tmp_path, monkeypatch):
    calls = []
    train = founders.train
    monkeypatch.setattr(founders, "train", lambda *a, **k: calls.append(a[1]) or train(*a, **k))
    c = founders.Cache(tmp_path)
    a, b = c.get(2), c.get(2)
    assert calls == [2]
    assert a is not b and a[0] is not b[0]
    # the full state comes back: weights, rng, last move, the pending reward and the bookkeeping (a lost pending
    # reward rarely changes a fake run, so check it directly)
    assert _same_state(_state(founders.train(World(32, 1234), 2)), _state(a))
    assert all(x.reward is not None for x in a)
    fresh = run_market(Repeat(), 2, rounds=3, attacker="adaptive")
    assert run_market(Repeat(), 2, rounds=3, attacker="adaptive", founders=a) == fresh
    assert run_market(Repeat(), 2, rounds=3, attacker="adaptive", founders=b) == fresh
    assert run_market(Repeat(), 2, rounds=3, attacker="adaptive", founders=founders.Cache(tmp_path).get(2)) == fresh


def test_cache_key_covers_what_shapes_the_founders(cadence, monkeypatch):
    c = founders.Cache("unused")
    k = c.key(0)
    assert len({k, c.key(1), c.key(0, modules=(32, 16)), c.key(0, n=4), c.key(0, K=16), c.key(0, rule_seed=1)}) == 6
    monkeypatch.setattr(founders, "_core_sha", lambda: "edited")
    assert c.key(0) != k
    monkeypatch.undo()
    monkeypatch.setitem(sys.modules, "cadence", type(fake())(**{**vars(fake()), "__version__": "other"}))
    assert c.key(0) != k


def test_reuse_rejects_founders_of_another_run(cadence):
    w = World(32, 1234)
    f1 = founders.train(w, 1)
    with pytest.raises(ValueError, match="seed 0"):
        run_market(Recip(), 0, rounds=1, founders=f1)                     # another seed
    with pytest.raises(ValueError, match="modules"):
        run_network(RandomTeacher(), 1, 1, arm="big", founders=f1)        # another brain size
    with pytest.raises(ValueError, match="7 founders"):
        run_market(Recip(), 1, rounds=1, founders=f1[:7])
    taught = f1[0].twin()
    taught.known.add(31)
    with pytest.raises(ValueError, match="founder 0"):
        run_market(Recip(), 1, rounds=1, founders=[taught] + f1[1:])      # not founder-only any more
