"""teachers.network reproduces EXP-33 (exp/EXP-33_forgetting_fix.py), the published record.

Two checks:
  fast : with a fake brain standing in for Cadence, the port and the original script make the SAME brain calls in the
         SAME order with the same arguments (every RNG-driven choice shows up in that trace) and return the same
         numbers: every arm on two seeds in EXP-33's setting, and every arm in a sparse world where pools run empty.
         Under a minute, no Cadence needed.
  slow : with real Cadence, RandomTeacher on seed 0, arm 'both', 16 rounds gives exactly the per-round accuracy and
         forgetting stored in exp/EXP-33.json. That file was made on Cadence 0.78.0; the original script reproduces
         it bit for bit on 0.80.0 (checked 2026-10-10). About two minutes; run with --runslow.
The original script is imported read-only: its main() is never called and no bytecode is written under exp/.
"""
import copy
import importlib.util
import json
import sys
import types
from pathlib import Path

import numpy as np
import pytest

from teachers.lessons import RandomTeacher
from teachers.network import ARMS, run_network

EXP = Path(__file__).resolve().parents[1] / "exp"
TOL = 1e-12                                        # the reproduction bar: same seed, same numbers


def _original(monkeypatch, rounds: int, N: int = 8):
    """Load exp/EXP-33_forgetting_fix.py as a module (EXP-31 is loaded by its run()), set to `rounds` rounds and N
    learners (its run() reads both module globals at call time)."""
    monkeypatch.setattr(sys, "dont_write_bytecode", True)     # covers the EXP-31 import inside run() too
    spec = importlib.util.spec_from_file_location("exp33_original", EXP / "EXP-33_forgetting_fix.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.ROUNDS, m.N = rounds, N
    return m


# ---------------- fast: call-order check on a fake brain ----------------
def _fake_cadence(trace: list, noisy_probe: bool = False) -> types.SimpleNamespace:
    """A stand-in for the cadence module with Brain's call surface: a tiny epsilon-greedy table learner whose 32
    contexts share 5 slots, so learning one item can overwrite another (the fake forgets, which exercises the drift
    check, rehearsal and the forgetting measure). Pure numpy, deterministic, and every call goes into `trace`.
    With noisy_probe, a probe copy answers at random (seeded by the brain and how often it has been saved), so the
    drift check filters pools hard; in a sparse world (N=40) it also empties them (the table learner never does)."""

    class ArousalConfig:
        pass

    class Brain:
        SLOTS = 5

        def __init__(self, tag, q, rng, noise=None):
            self.tag, self.q, self.rng, self.noise, self.last, self.saves = tag, q, rng, noise, None, 0

        @classmethod
        def compose(cls, inputs, actions, modules, seed, arousal=None):
            trace.append(("compose", inputs, actions, tuple(modules), seed, type(arousal).__name__))
            return cls(seed, np.zeros((cls.SLOTS, actions)), np.random.default_rng(seed))

        def live(self, x, reward=None, done=None):
            c = int(np.argmax(x[0]))
            if reward is not None and self.last is not None:
                s, a = self.last
                self.q[s, a] += 0.3 * (float(reward[0]) - self.q[s, a])
            s = c % self.SLOTS
            a = int(self.rng.integers(self.q.shape[1])) if self.rng.random() < 0.1 else int(np.argmax(self.q[s]))
            self.last = (s, a)
            trace.append(("live", self.tag, c, None if reward is None else float(reward[0]),
                          None if done is None else bool(done[0]), a))
            return np.array([a])

        def save(self, path):
            self.saves += 1
            trace.append(("save", self.tag, self.saves))
            return (self.tag, self.saves, self.q.copy(), copy.deepcopy(self.rng))

        @classmethod
        def load(cls, saved):
            tag, saves, q, rng = saved
            trace.append(("load", tag, saves))
            noise = np.random.default_rng([tag, saves]) if noisy_probe and isinstance(tag, int) else None
            return cls(("copy", tag), q.copy(), copy.deepcopy(rng), noise)

        def reset(self):
            trace.append(("reset", self.tag))

        def act(self, x, greedy=False):
            c = int(np.argmax(x[0]))
            a = int(self.noise.integers(2)) if self.noise is not None else int(np.argmax(self.q[c % self.SLOTS]))
            trace.append(("act", self.tag, c, greedy, a))
            return np.array([a])

    return types.SimpleNamespace(Brain=Brain, ArousalConfig=ArousalConfig, __version__="fake")


class _CountingTeacher(RandomTeacher):
    """RandomTeacher that counts the lessons it plans (a lesson is skipped when the drift check empties the pool)."""

    def __init__(self):
        self.lessons = 0

    def lesson(self, view, rng):
        self.lessons += 1
        return super().lesson(view, rng)


# (arm, seed, noisy probe, N, rounds). EXP-33's own setting: N=8, 16 rounds. N=40 on K=32 is a sparse world: founders
# start with 0 or 1 items, so empty known sets, emptied pools (skipped lessons) and rehearsal with nothing known occur.
CASES = [(arm, seed, False, 8, 16) for arm in ARMS for seed in (0, 1)] + [(arm, 0, True, 40, 6) for arm in ARMS]


@pytest.mark.parametrize("arm,seed,noisy_probe,N,rounds", CASES)
def test_same_brain_calls_as_original_script(monkeypatch, arm, seed, noisy_probe, N, rounds):
    trace = []
    monkeypatch.setitem(sys.modules, "cadence", _fake_cadence(trace, noisy_probe))
    m = _original(monkeypatch, rounds=rounds, N=N)
    var, s, acc, forgetting = m.run((arm, seed))
    original = list(trace)
    trace.clear()
    out = run_network(RandomTeacher(), seed=seed, rounds=rounds, arm=arm, N=N)
    assert len(trace) == len(original), f"{len(trace)} brain calls vs {len(original)} in the original"
    first = next((i for i, (a, b) in enumerate(zip(trace, original)) if a != b), None)
    assert first is None, f"call {first} differs: port {trace[first]} vs original {original[first]}"
    assert len(out["acc"]) == len(acc) == rounds + 1
    assert all(abs(a - b) <= TOL for a, b in zip(out["acc"], acc)), (out["acc"], acc)
    assert abs(out["forgetting"] - forgetting) <= TOL
    assert out["final"] == out["acc"][-1] and out["cadence"] == "fake"


def test_fake_brain_exercises_every_branch(monkeypatch):
    """Guard against a trivial fake: the table fake must forget (else rehearse, drift and the forgetting measure are
    never exercised) and the sparse noisy world must skip some lessons (else the empty-pool branch never runs)."""
    monkeypatch.setitem(sys.modules, "cadence", _fake_cadence([]))
    base = run_network(RandomTeacher(), seed=0, rounds=16, arm="base")
    both = run_network(RandomTeacher(), seed=0, rounds=16, arm="both")
    assert base["forgetting"] > 0 and both["forgetting"] > 0
    assert base["acc"] != both["acc"]
    monkeypatch.setitem(sys.modules, "cadence", _fake_cadence([], noisy_probe=True))
    teacher = _CountingTeacher()
    run_network(teacher, seed=0, rounds=6, arm="drift", N=40)
    assert 0 < teacher.lessons < 6 * 40


# ---------------- slow: real Cadence against the published numbers ----------------
@pytest.mark.slow
def test_random_teacher_reproduces_published_exp33_seed0_both():
    pytest.importorskip("cadence")
    rows = json.loads((EXP / "EXP-33.json").read_text())
    (pub,) = [r for r in rows if r[0] == "both" and r[1] == 0]   # rows are [arm, seed, acc per round, forgetting]
    _, _, acc, forgetting = pub
    out = run_network(RandomTeacher(), seed=0, rounds=len(acc) - 1, arm="both")
    print(json.dumps(out))
    hint = (f" (Cadence {out['cadence']}: if Cadence changed, rerun the original script for seed 0 and compare; the "
            f"fast trace test tells a port bug from a Cadence change)")
    assert len(out["acc"]) == len(acc)
    for r, (got, want) in enumerate(zip(out["acc"], acc)):
        assert abs(got - want) <= TOL, f"round {r}: {got!r} vs published {want!r}" + hint
    assert abs(out["forgetting"] - forgetting) <= TOL, f"forgetting {out['forgetting']!r} vs {forgetting!r}" + hint
    assert out["final"] == out["acc"][-1]
    assert abs(out["mean_over_time"] - float(np.mean(acc))) <= TOL
