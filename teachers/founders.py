"""Founder brains: trained once per seed, reused as twins.

Training the founders (8 brains x 4 items x 400 graded steps) is most of a market or network run: about 66 s of the
about 110 s an EXP-38 seed takes. It depends only on the world, the seed and the brain size, not on the defence, the
attacker or the teaching policy, and the market (teachers.market) and the network (teachers.network) train the same
founders for the same seed: one rng, default_rng(1000 + seed), whose first call slices the contexts, then learner i
seeded 10_000 * (seed + 1) + i, trained on slice i. So the founders can be trained once and reused: run_market and
run_network take founders=[...] and live on twins of them (Learner.twin; Brain.save keeps the weights, optimizer,
random state and pending feedback). A run on twins gives the same numbers as a run that trains its own founders
(tests/test_founders.py).

Cache keeps founders on disk between processes and runs (the Arena's workers share one). Its key includes the
Cadence version, the numpy version and the source of teachers/core.py, so after a change to any of them it trains
new founders instead of loading stale ones.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path

import numpy as np

from .core import Learner, World, _cadence, cadence_version

FIRST_SEED = 1000                # the run's rng is default_rng(FIRST_SEED + seed); its first call slices the contexts


def founder_seed(seed: int, i: int) -> int:
    """Brain seed of founder i in run `seed` (EXP-31/33/36/38)."""
    return 10_000 * (seed + 1) + i


def slices(world: World, seed: int, n: int) -> list[list[int]]:
    """The founder slices of run `seed`: the first call on the run's rng, as run_market and run_network make it."""
    return world.slices(n, np.random.default_rng(FIRST_SEED + seed))


def train(world: World, seed: int, n: int = 8, modules=(16, 8)) -> list[Learner]:
    """The n founders of run `seed`, trained in order 0..n-1 exactly as run_market / run_network train them."""
    return [Learner(world, founder_seed(seed, i), founder=s, modules=modules)
            for i, s in enumerate(slices(world, seed, n))]


def reuse(founders, world: World, seed: int, founder_items, modules) -> list[Learner]:
    """Twins of pre-trained `founders` for a run that would train them itself from `founder_items` (its slices).

    Raises ValueError unless they are exactly that run's founders (count, brain seeds, size, world, items and
    founder-only bookkeeping), so a cache mix-up cannot silently change a result. The founders are not touched."""
    founders = list(founders)
    if len(founders) != len(founder_items):
        raise ValueError(f"{len(founders)} founders given, the run has {len(founder_items)}")
    for i, (f, items) in enumerate(zip(founders, founder_items)):
        items = {int(c) for c in items}
        ok = (f.seed == founder_seed(seed, i) and tuple(f.modules) == tuple(modules)
              and f.world.K == world.K and np.array_equal(f.world.rule, world.rule)
              and f.known == items and f.origin == {c: None for c in items} and not f.found
              and f.notes == {c: int(world.rule[c]) for c in items})
        if not ok:
            raise ValueError(f"founder {i} is not founder {i} of seed {seed} (modules {tuple(modules)})")
    return [f.twin() for f in founders]


def _core_sha() -> str:
    return hashlib.sha256((Path(__file__).with_name("core.py")).read_bytes()).hexdigest()[:16]


class Cache:
    """Founders on disk under `directory`, trained the first time a seed is asked for and loaded after.

    One sub-directory per (seed, n, K, rule_seed, modules), named by a hash that also covers the Cadence version,
    the numpy version and teachers/core.py. Written to a temporary directory and renamed into place, so two
    processes training the same seed at once both end up with a complete copy."""

    def __init__(self, directory):
        self.dir = Path(directory)

    def key(self, seed: int, n: int = 8, K: int = 32, rule_seed: int = 1234, modules=(16, 8)) -> str:
        spec = dict(seed=int(seed), n=int(n), K=int(K), rule_seed=int(rule_seed), modules=[int(m) for m in modules],
                    cadence=cadence_version(), numpy=np.__version__, core=_core_sha())
        return f"seed{int(seed)}-" + hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()[:16]

    def get(self, seed: int, n: int = 8, K: int = 32, rule_seed: int = 1234, modules=(16, 8)) -> list[Learner]:
        """The founders of run `seed`, loaded from the cache or trained and stored. Fresh objects on every call."""
        world = World(K, rule_seed)
        d = self.dir / self.key(seed, n, K, rule_seed, modules)
        if not (d / "founders.json").exists():
            self._store(d, train(world, seed, n, modules))
        return self._load(d, world, seed, modules)

    def _store(self, d: Path, founders: list[Learner]) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        tmp = Path(tempfile.mkdtemp(dir=self.dir, prefix=".tmp-"))
        try:
            for i, f in enumerate(founders):
                f.b.save(str(tmp / f"{i}.npz"))
            meta = dict(n=len(founders), cadence=cadence_version(),
                        reward=[None if f.reward is None else [float(r) for r in f.reward] for f in founders])
            (tmp / "founders.json").write_text(json.dumps(meta))
            try:
                os.replace(tmp, d)
            except OSError:                   # another process stored this seed first; keep its copy
                if not (d / "founders.json").exists():
                    raise
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def _load(self, d: Path, world: World, seed: int, modules) -> list[Learner]:
        Brain, _ = _cadence()
        meta = json.loads((d / "founders.json").read_text())
        out = []
        for i, items in enumerate(slices(world, seed, meta["n"])):
            f = Learner(world, founder_seed(seed, i), founder=items, modules=modules, _brain=Brain.load(d / f"{i}.npz"))
            r = meta["reward"][i]
            f.reward = None if r is None else np.array(r, dtype=float)
            out.append(f)
        return out
