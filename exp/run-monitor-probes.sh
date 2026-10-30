#!/bin/bash
# Monitor-loop probe runner: EXP-08 and the EXP-62e identity gate on the installed Cadence.
# Usage: bash run-monitor-probes.sh <version-tag> <short-sha>     e.g. v0912 2062eda
# The gate needs LATERAL=-0.5: EXP-62e was recorded under 0.84.3, whose unset lateral was -0.5
# (0.85.0 made it 0.0). Without it the gate reads DIFFERS on every version (seen 2026-10-30).
set -u
cd "$(dirname "$0")"
export PYTHONUTF8=1
tag=$1; sha=$2

s=$(date +%s); python -u EXP-08_vs_transfer_separation.py > "EXP-08-$tag-$sha.out" 2> "EXP-08-$tag-$sha.err"
echo "$(( $(date +%s) - s ))s exit $?" > "EXP-08-$tag-$sha.time"

s=$(date +%s); LATERAL=-0.5 GATE=1 python -u EXP-73_m1b_measured_zero.py > "EXP-77b-gate-$sha.out" 2> "EXP-77b-gate-$sha.err"
echo "$(( $(date +%s) - s ))s exit $? (LATERAL=-0.5)" > "EXP-77b-gate-$sha.time"

prev=$(ls -t EXP-08-v*-*.out | grep -v -- "-$sha.out" | head -1)
cmp -s "$prev" "EXP-08-$tag-$sha.out" && echo "EXP-08 BYTE-IDENTICAL to $prev" || echo "EXP-08 DIFFERS from $prev"
grep -h "identity gate" "EXP-77b-gate-$sha.out"
