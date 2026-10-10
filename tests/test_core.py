"""World, Learner and twin-ablation worth on real Cadence brains (teachers/core.py, teachers/worth.py).

The World test needs only numpy; the rest skip when Cadence is not installed. Each test stays under ~30 s on the
lab PC: the founder fixture (~8-12 s) is built once per module, an EXP-08 witness is ~11 s."""
import importlib.util
import math

import numpy as np
import pytest

from teachers.core import Learner, World
from teachers.worth import coalition_values, twin_worth

needs_cadence = pytest.mark.skipif(importlib.util.find_spec("cadence") is None,
                                   reason="Cadence not installed (run ./setup.sh)")

# np.random.default_rng(1234).integers(0, 2, size=32): EXP-31's RULE, the world of EXP-31/33/34/36/38
RULE_32_1234 = [1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1]


def close(a, b):
    return math.isclose(a, b, rel_tol=0.0, abs_tol=1e-12)


def drill(c, judge, n=25):
    """A lesson: n graded steps on context c."""
    def lesson(learner):
        for _ in range(n):
            learner.live(c, judge)
    return lesson


def accuracy(learner):
    return learner.accuracy()


def wrong(learner):
    a = learner.answers()
    return [c for c in range(learner.world.K) if a[c] != learner.world.rule[c]]


@pytest.fixture(scope="module")
def founder():
    """EXP-31 seed 0, brain 0: world (32, 1234), slice 0 of rng(1000)'s permutation, brain seed 10_000.
    Shared by the tests below, which only ever teach its twins."""
    world = World(32, 1234)
    return Learner(world, 10_000, founder=world.slices(8, np.random.default_rng(1000))[0])


# ---------------- World ----------------
def test_world_rule_is_deterministic():
    a, b = World(32, 1234), World(32, 1234)
    assert np.array_equal(a.rule, b.rule)
    assert a.rule.tolist() == RULE_32_1234
    perm = np.random.default_rng(1000).permutation(32)            # EXP-31 run(): founder slices per seed
    assert a.slices(8, np.random.default_rng(1000)) == [list(perm[i * 4:(i + 1) * 4]) for i in range(8)]
    assert a.slices(8, np.random.default_rng(1000))[0] == [9, 6, 3, 14]
    assert a.accuracy(a.rule) == 1.0 and a.accuracy(1 - a.rule) == 0.0
    assert a.judge(0)(int(a.rule[0])) == 1.0 and a.judge(0)(1 - int(a.rule[0])) == -1.0


# ---------------- Learner ----------------
@needs_cadence
def test_founder_masters_its_slice(founder):
    world, own = founder.world, [9, 6, 3, 14]
    ans = founder.answers()
    assert all(ans[c] == world.rule[c] for c in own)
    assert founder.known == set(own) and founder.found == set()
    assert founder.notes == {c: int(world.rule[c]) for c in own}
    assert founder.origin == {c: None for c in own}
    assert founder.reward is not None                              # the last mastery step's reward is pending
    assert 0 < len(wrong(founder)) < world.K                        # it does not know the rest of the world


@needs_cadence
def test_twin_and_original_taught_the_same_steps_stay_identical(founder):
    world = founder.world
    original = founder.twin()                                       # keeps the shared fixture untouched
    twin = original.twin()
    c = wrong(original)[0]
    for _ in range(25):                                             # interleaved, so shared state would show
        assert original.live(c, world.judge(c)) == twin.live(c, world.judge(c))
    a = original.answers()
    assert np.array_equal(a, twin.answers())
    assert a[c] == world.rule[c]                                    # the steps changed the brain (not vacuous)
    assert np.array_equal(original.reward, twin.reward)
    twin.known.add(c)
    assert c not in original.known                                  # bookkeeping is copied, not shared


# ---------------- worth ----------------
@needs_cadence
def test_twin_worth_of_a_lesson_on_a_wrong_context_is_positive(founder):
    world, before = founder.world, founder.answers()
    reward, known = founder.reward.copy(), set(founder.known)
    c = wrong(founder)[0]
    assert twin_worth(founder, drill(c, world.judge(c)), accuracy) > 0
    assert np.array_equal(founder.answers(), before)                # the original was never taught
    assert np.array_equal(founder.reward, reward) and founder.known == known


@needs_cadence
def test_twin_worth_of_an_empty_lesson_is_exactly_zero(founder):
    assert twin_worth(founder, lambda learner: None, accuracy) == 0.0


@needs_cadence
def test_twin_worth_of_a_wrong_answer_is_negative(founder):
    """Worth is task-specific (EXP-08 fake_wrong): drilling the wrong answer on a known context costs accuracy."""
    c = 9                                                           # a founder item it answers right
    flipped = int(1 - founder.world.rule[c])
    assert twin_worth(founder, drill(c, lambda a: 1.0 if a == flipped else -1.0), accuracy) < 0


@needs_cadence
def test_coalition_values_on_real_brains(founder):
    world = founder.world
    c1, c2 = wrong(founder)[:2]
    lessons = {"a": drill(c1, world.judge(c1)), "b": drill(c2, world.judge(c2))}
    v = coalition_values(founder, lessons, accuracy)
    assert list(v) == [frozenset(), frozenset("a"), frozenset("b"), frozenset("ab")]
    assert v[frozenset()] == 0.0
    assert v[frozenset("a")] == twin_worth(founder, lessons["a"], accuracy)
    assert v[frozenset("ab")] > max(v[frozenset("a")], v[frozenset("b")]) > 0


# ---------------- EXP-08 reproduction (exp/EXP-08-v080.out, seed 1: tG +0.50, tFr -0.12) ----------------
EXP08_K, EXP08_STEPS, EXP08_SEED = 8, 1600, 1


def exp08_learner(seed):
    """EXP-08's fresh brain and held-out task T: World draws T as make_rule's first try (rng 10_000 + seed)."""
    world = World(EXP08_K, 10_000 + seed)
    assert len(set(world.rule.tolist())) > 1                       # make_rule would redraw an all-same map
    return Learner(world, seed)


@needs_cadence
def test_twin_worth_reproduces_exp08_genuine():
    learner = exp08_learner(EXP08_SEED)
    world, hits = learner.world, []

    def genuine(t):                                                 # EXP-08 ingest(): context t % K, +1 for T
        for step in range(EXP08_STEPS):
            c = step % EXP08_K
            hits.append(t.live(c, world.judge(c)) == world.rule[c])

    assert close(twin_worth(learner, genuine, accuracy), 0.5)       # accG 1.00 - acc0 0.50
    assert sum(hits) == 1587                                        # rateG = 1587 / 1600, pinned for the fake


@needs_cadence
def test_twin_worth_reproduces_exp08_fake_random():
    learner = exp08_learner(EXP08_SEED)
    rate_g = 1587 / EXP08_STEPS
    frng = np.random.default_rng(20_000 + EXP08_SEED)

    def fake_random(t):                                             # reward independent of context and action
        for step in range(EXP08_STEPS):
            t.live(step % EXP08_K, lambda a: 1.0 if frng.random() < rate_g else -1.0)

    assert close(twin_worth(learner, fake_random, accuracy), -0.125)  # accFr 0.375 - acc0 0.50
