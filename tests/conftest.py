"""Shared pytest setup.

Slow tests (full Cadence simulations, minutes each) are marked @pytest.mark.slow and skipped unless pytest is run
with --runslow.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:          # import teachers from the checkout, installed or not
    sys.path.insert(0, str(ROOT))


def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true", default=False,
                     help="also run tests marked slow (full Cadence simulations, minutes each)")


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: full Cadence simulation, minutes per case; skipped unless --runslow")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        return
    skip = pytest.mark.skip(reason="slow: run with --runslow")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip)
