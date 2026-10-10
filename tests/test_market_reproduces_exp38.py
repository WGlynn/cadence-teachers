"""The library attack market reproduces the published EXP-38 rows (exp/EXP-38-full.jsonl) from the same seed.

Each case is a full EXP-38 run (8 brains, 16 rounds, about 2 minutes on the lab PC), so the test is slow:
    python -m pytest tests/test_market_reproduces_exp38.py --runslow
Both cases matched the published rows exactly on Cadence 0.80.0 (checked 2026-10-10).
"""
import json
import math
from pathlib import Path

import pytest

from teachers.core import cadence_version
from teachers.defences import Recip, Repeat
from teachers.market import run_market

ROWS = Path(__file__).resolve().parents[1] / "exp" / "EXP-38-full.jsonl"
TOL = 1e-12


def published(mode: str, seed: int) -> dict:
    for line in ROWS.read_text().splitlines():
        row = json.loads(line)
        if row["mode"] == mode and row["seed"] == seed:
            return row
    raise LookupError(f"no {mode} seed {seed} row in {ROWS}")


def assert_same_row(got: dict, want: dict) -> None:
    assert sorted(got) == sorted(want), "keys differ"
    for k, w in want.items():
        g = got[k]
        if isinstance(w, list):
            assert len(g) == len(w), f"{k}: {len(g)} rounds, published {len(w)}"
            for r, (gr, wr) in enumerate(zip(g, w)):
                assert math.isclose(gr, wr, rel_tol=0.0, abs_tol=TOL), f"{k}[{r}]: {gr!r} != published {wr!r}"
        elif isinstance(w, float):
            assert math.isclose(g, w, rel_tol=0.0, abs_tol=TOL), f"{k}: {g!r} != published {w!r}"
        else:
            assert g == w, f"{k}: {g!r} != published {w!r}"


@pytest.mark.slow
@pytest.mark.parametrize("defence", [Recip(), Repeat()], ids=lambda d: d.name)
def test_market_reproduces_exp38_seed0(defence):
    want = published(defence.name, 0)
    if cadence_version() != want["cadence"]:
        pytest.skip(f"published row ran on Cadence {want['cadence']}, installed {cadence_version()}")
    assert_same_row(run_market(defence, seed=0), want)
