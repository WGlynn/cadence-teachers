#!/bin/bash
# CAL-1c chain (experiments/CAL-1c.md, pre-registered before any data): V6 identity audit, V1 audit + inspect, V2 gate,
# pilot, then the full run only on a pilot GO, at the m the pilot rule picks. Pinned to Cadence 0.94.0 from
# ~/_cadence_v0940/src; BLAS threads pinned to 1 (also set inside the harness before numpy loads).
set -u
cd "$(dirname "$0")"
export PYTHONUTF8=1 PYTHONPATH="$HOME/_cadence_v0940/src"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
unset LATERAL
MODE=ids python -u CAL-1c_calibration_vs.py > CAL-1c-v6-ids.out 2>&1 || { echo "VOID: V6 identity audit failed"; cat CAL-1c-v6-ids.out; exit 1; }
tail -1 CAL-1c-v6-ids.out
python -u EXP-77b_construction_audit.py > CAL-1c-v1-audit.out 2>&1; echo "audit exit $?"
grep -q "ADMITTED BY CONSTRUCTION" CAL-1c-v1-audit.out || { echo "VOID: V1 audit did not admit"; exit 1; }
MODE=v1 python -u CAL-1c_calibration_vs.py > CAL-1c-v1-inspect.out 2>&1 || { echo "VOID: V1 inspect failed"; cat CAL-1c-v1-inspect.out; exit 1; }
cat CAL-1c-v1-inspect.out
MODE=gate WORKERS=4 python -u CAL-1c_calibration_vs.py > CAL-1c-v2-gate.out 2>&1 || { echo "VOID: V2 gate failed"; cat CAL-1c-v2-gate.out; exit 1; }
tail -1 CAL-1c-v2-gate.out
s=$(date +%s)
TAG=pilot WORKERS=4 python -u CAL-1c_calibration_vs.py > CAL-1c-pilot.out 2> CAL-1c-pilot.err; echo "pilot exit $? in $(( $(date +%s) - s ))s"
tail -8 CAL-1c-pilot.out
m=$(python -c "import json;d=json.load(open('CAL-1c-pilot.json'));print(d['m'] if d['verdict'].startswith('GO') else 0)")
[ "$m" = "0" ] && { echo "PILOT STOP: no full run"; exit 0; }
[ -n "${PILOT_ONLY:-}" ] && { echo "PILOT_ONLY set: stopping after the pilot (m = $m)"; exit 0; }
s=$(date +%s)
TAG=full M=$m WORKERS=4 python -u CAL-1c_calibration_vs.py > CAL-1c-full.out 2> CAL-1c-full.err; rc=$?
echo "full m=$m exit $rc in $(( $(date +%s) - s ))s"
tail -3 CAL-1c-full.out
