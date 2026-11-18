#!/bin/bash
# CAL-1b chain (experiments/CAL-1b.md, pre-registered c47fa0f): V1 audit + inspect, V2 gate, pilot, then the full run
# only on a pilot GO, at the m the pilot rule picks. Pinned to Cadence 0.94.0 from ~/_cadence_v0940/src.
set -u
cd "$(dirname "$0")"
export PYTHONUTF8=1 PYTHONPATH="$HOME/_cadence_v0940/src"
unset LATERAL
python -u EXP-77b_construction_audit.py > CAL-1b-v1-audit.out 2>&1; echo "audit exit $?"
grep -q "ADMITTED BY CONSTRUCTION" CAL-1b-v1-audit.out || { echo "VOID: V1 audit did not admit"; exit 1; }
MODE=v1 python -u CAL-1b_calibration_vs.py > CAL-1b-v1-inspect.out 2>&1 || { echo "VOID: V1 inspect failed"; cat CAL-1b-v1-inspect.out; exit 1; }
cat CAL-1b-v1-inspect.out
MODE=gate WORKERS=4 python -u CAL-1b_calibration_vs.py > CAL-1b-v2-gate.out 2>&1 || { echo "VOID: V2 gate failed"; cat CAL-1b-v2-gate.out; exit 1; }
tail -1 CAL-1b-v2-gate.out
TAG=pilot WORKERS=4 python -u CAL-1b_calibration_vs.py > CAL-1b-pilot.out 2> CAL-1b-pilot.err; echo "pilot exit $?"
tail -6 CAL-1b-pilot.out
m=$(python -c "import json;d=json.load(open('CAL-1b-pilot.json'));print(d['m'] if d['verdict'].startswith('GO') else 0)")
[ "$m" = "0" ] && { echo "PILOT STOP: no full run"; exit 0; }
s=$(date +%s)
TAG=full M=$m WORKERS=4 python -u CAL-1b_calibration_vs.py > CAL-1b-full.out 2> CAL-1b-full.err; rc=$?
echo "full m=$m exit $rc in $(( $(date +%s) - s ))s"
tail -3 CAL-1b-full.out
