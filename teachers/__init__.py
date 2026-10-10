"""teachers: teaching between Cadence brains.

Grading lessons, probes on a saved copy, twin-ablation worth, Shapley / leave-one-out credit, the teaching network
(EXP-33) and the attack market with its defences (EXP-36/38). Every port reproduces its published experiment exactly
from the same seeds (tests/test_*_reproduces_*.py, run with pytest --runslow). Cadence is imported lazily by
teachers.core, so importing this package is cheap.
"""
__version__ = "0.1.0"
