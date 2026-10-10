"""A stand-in for the cadence module, for fast tests of code that runs whole markets and networks.

Brain has the call surface teachers.core uses (compose, live, save, load, reset, act) on a tiny epsilon-greedy table
learner whose contexts share 5 slots, so it learns some items and overwrites others. Pure numpy and deterministic.
save() pickles the whole state, random generator included, to the given file and load() reads it back, so a loaded
copy continues exactly like the original (as Cadence's Brain.save/load do), and files can go through a cache.

Install it with monkeypatch.setitem(sys.modules, "cadence", fake()).
"""
import pickle
import types

import numpy as np


class ArousalConfig:
    pass


class Brain:
    SLOTS = 5

    def __init__(self, q, rng, last=None):
        self.q, self.rng, self.last = q, rng, last

    @classmethod
    def compose(cls, inputs, actions, modules, seed, arousal=None):
        return cls(np.zeros((cls.SLOTS, actions)), np.random.default_rng(seed + sum(modules)))

    def live(self, x, reward=None, done=None):
        c = int(np.argmax(x[0]))
        if reward is not None and self.last is not None:
            s, a = self.last
            self.q[s, a] += 0.3 * (float(reward[0]) - self.q[s, a])
        s = c % self.SLOTS
        a = int(self.rng.integers(self.q.shape[1])) if self.rng.random() < 0.1 else int(np.argmax(self.q[s]))
        self.last = (s, a)
        return np.array([a])

    def save(self, path):
        with open(path, "wb") as f:
            pickle.dump((self.q, self.rng, self.last), f)
        return path

    @classmethod
    def load(cls, path):
        with open(path, "rb") as f:
            return cls(*pickle.load(f))

    def reset(self):
        pass

    def act(self, x, greedy=False):
        return np.array([int(np.argmax(self.q[int(np.argmax(x[0])) % self.SLOTS]))])


def fake() -> types.SimpleNamespace:
    return types.SimpleNamespace(Brain=Brain, ArousalConfig=ArousalConfig, __version__="fake")
