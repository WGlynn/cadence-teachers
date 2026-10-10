"""Core objects: a bandit World and a Learner (one Cadence brain living through it).

These are lifted from the experiment harness that EXP-31, -33, -36 and -38 share (exp/EXP-31_peer_exchange.py,
class Peer), with the same call order, so experiments ported onto the library reproduce their published
numbers from the same seeds.

World:   K contexts (one-hot inputs), two actions, a hidden binary rule; context c is "right" when the action
         equals rule[c].
Learner: a Cadence Brain plus the bookkeeping a teaching market needs: `known` (items it believes it knows),
         `notes` (what it wrote down when it learned each item; EXP-33 provenance), `origin` (who it learned each
         item from; None = founder knowledge), and `found` (items it got by its own discovery).
"""
from __future__ import annotations

import os
import tempfile

import numpy as np


def _cadence():
    try:
        import cadence  # noqa: F401
        from cadence import Brain, ArousalConfig
    except ImportError as e:  # pragma: no cover - environment problem, not logic
        raise ImportError(
            "teachers needs Cadence (package 'cadence-net'). Run ./setup.sh from the repo root, or "
            "pip install -e <your clone of https://github.com/muellerberndt/cadence>"
        ) from e
    return Brain, ArousalConfig


def cadence_version() -> str:
    try:
        import cadence
        return getattr(cadence, "__version__", "?")
    except Exception:
        return "?"


class World:
    """A K-context bandit with a hidden binary rule.

    rule_seed=1234 with K=32 is the world of EXP-31/33/34/36/38; rule_seed=4321 with K=96 is EXP-35b's."""

    def __init__(self, K: int = 32, rule_seed: int = 1234, actions: int = 2):
        self.K, self.actions, self.rule_seed = K, actions, rule_seed
        self.rule = np.random.default_rng(rule_seed).integers(0, actions, size=K)
        self._eye = np.eye(K)

    def x(self, c: int) -> np.ndarray:
        """One-hot observation for context c, shaped (1, K) as Cadence expects."""
        return self._eye[[int(c)]]

    def judge(self, c: int):
        """Reward function for the true rule: +1 right, -1 wrong."""
        r = int(self.rule[c])
        return lambda a: 1.0 if a == r else -1.0

    def accuracy(self, answers: np.ndarray) -> float:
        return float(np.mean(np.asarray(answers) == self.rule))

    def slices(self, n: int, rng: np.random.Generator) -> list[list[int]]:
        """Split a random permutation of the contexts into n founder slices (one rng.permutation call)."""
        perm = rng.permutation(self.K)
        return [list(perm[i * self.K // n:(i + 1) * self.K // n]) for i in range(n)]


class Learner:
    """One Cadence brain plus its teaching-market bookkeeping.

    The founder is trained to mastery on its slice: `mastery_steps` graded steps per founder item, cycling
    through the slice in order (EXP-31: 400 per item)."""

    def __init__(self, world: World, seed: int, founder=(), modules=(16, 8), mastery_steps: int = 400,
                 arousal: bool = True, _brain=None):
        Brain, ArousalConfig = _cadence()
        self.world, self.seed, self.modules = world, seed, tuple(modules)
        if _brain is not None:
            self.b = _brain
        else:
            kw = {"arousal": ArousalConfig()} if arousal else {}
            self.b = Brain.compose(inputs=world.K, actions=world.actions, modules=self.modules, seed=seed, **kw)
        self.reward = None                      # pending reward, delivered with the next observation
        founder = [int(c) for c in founder]
        self.known: set[int] = set(founder)
        self.notes: dict[int, int] = {c: int(world.rule[c]) for c in founder}
        self.origin: dict[int, int | None] = {c: None for c in founder}
        self.found: set[int] = set()
        if _brain is None:
            for t in range(len(founder) * mastery_steps):
                c = founder[t % len(founder)]
                self.live(c, world.judge(c))

    # ---------------- living ----------------
    def live(self, c: int, judge) -> int:
        """One graded step: show context c, act, and queue judge(action) as the reward for the next step."""
        x = self.world.x(c)
        a = self.b.live(x) if self.reward is None else self.b.live(x, reward=self.reward, done=np.array([True]))
        a = int(np.asarray(a).reshape(-1)[0])
        self.reward = np.array([judge(a)])
        return a

    # ---------------- measuring ----------------
    def answers(self) -> np.ndarray:
        """Greedy answer on every context, read from a saved copy so the live brain is untouched (a probe)."""
        Brain, _ = _cadence()
        with tempfile.TemporaryDirectory() as d:
            cp = Brain.load(self.b.save(os.path.join(d, "p.npz")))
        out = []
        for c in range(self.world.K):
            cp.reset()
            out.append(int(np.asarray(cp.act(self.world.x(c), greedy=True)).reshape(-1)[0]))
        return np.array(out)

    def accuracy(self) -> float:
        return self.world.accuracy(self.answers())

    # ---------------- copying ----------------
    def twin(self) -> "Learner":
        """A byte-identical copy (weights, pending reward, bookkeeping) that then lives independently.
        Twins are how worth is measured: teach one, not the other, compare (EXP-08)."""
        Brain, _ = _cadence()
        with tempfile.TemporaryDirectory() as d:
            b = Brain.load(self.b.save(os.path.join(d, "t.npz")))
        t = Learner(self.world, self.seed, modules=self.modules, _brain=b)
        t.reward = None if self.reward is None else self.reward.copy()
        t.known, t.notes, t.origin, t.found = set(self.known), dict(self.notes), dict(self.origin), set(self.found)
        return t
