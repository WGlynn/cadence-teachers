"""Locate the Cadence source checkout (the key-door experiments import its benchmarks/keydoor module).
Order: $CADENCE_SRC, then vendor/cadence (created by setup.sh), then ~/_cadence_study (the original author's machine)."""
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_CANDIDATES = [os.environ.get("CADENCE_SRC"), os.path.join(_HERE, "..", "vendor", "cadence"),
               os.path.expanduser("~/_cadence_study")]
CADENCE_SRC = next((os.path.abspath(p) for p in _CANDIDATES
                    if p and os.path.isdir(os.path.join(p, "benchmarks", "keydoor"))), None)
if CADENCE_SRC is None:
    raise SystemExit("Cadence source not found. Run ./setup.sh, or set CADENCE_SRC to a clone of "
                     "https://github.com/muellerberndt/cadence")
KEYDOOR = os.path.join(CADENCE_SRC, "benchmarks", "keydoor")
