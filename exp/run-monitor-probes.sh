#!/bin/bash
# Monitor-loop probe runner: EXP-08 and the EXP-62e identity gate on the installed Cadence.
# Outputs are written as *.partial (gitignored) and renamed on finish, so a timed checkpoint never commits a half-written run (2026-11-03).
# Usage: bash run-monitor-probes.sh <version-tag> <short-sha>     e.g. v0912 2062eda
# The gate needs LATERAL=-0.5: EXP-62e was recorded under 0.84.3, whose unset lateral was -0.5
# (0.85.0 made it 0.0). Without it the gate reads DIFFERS on every version (seen 2026-10-30).
# 2026-11-14: 0.95.2 changed Brain.lesson (free phase warm from the stream, no option back), so EXP-62e cannot
# match past 0.95.1. The gate now pins the 0.94.0 composition (PIN0940) and compares with a row recorded on
# 0.99.0 (b0b09d4). EXP-08 also runs pinned (EXP-08-pin0941.py), compared with the 0.99.0 pinned run.
set -u
cd "$(dirname "$0")"
export PYTHONUTF8=1
tag=$1; sha=$2

s=$(date +%s); python -u EXP-08_vs_transfer_separation.py > "EXP-08-$tag-$sha.out.partial" 2> "EXP-08-$tag-$sha.err.partial"; rc=$?
mv "EXP-08-$tag-$sha.out.partial" "EXP-08-$tag-$sha.out"; mv "EXP-08-$tag-$sha.err.partial" "EXP-08-$tag-$sha.err"
echo "$(( $(date +%s) - s ))s exit $rc" > "EXP-08-$tag-$sha.time"

s=$(date +%s); LATERAL=-0.5 PIN0940=1 GATE=1 GATE_REF=EXP-77b-gate-ref-b0b09d4.jsonl python -u EXP-73_m1b_measured_zero.py > "EXP-77b-gate-$sha.out.partial" 2> "EXP-77b-gate-$sha.err.partial"; rc=$?
mv "EXP-77b-gate-$sha.out.partial" "EXP-77b-gate-$sha.out"; mv "EXP-77b-gate-$sha.err.partial" "EXP-77b-gate-$sha.err"
echo "$(( $(date +%s) - s ))s exit $rc (LATERAL=-0.5)" > "EXP-77b-gate-$sha.time"

prev=$(ls -t EXP-08-v*-*.out | grep -v -- "-$sha.out" | head -1)
cmp -s "$prev" "EXP-08-$tag-$sha.out" && echo "EXP-08 BYTE-IDENTICAL to $prev" || echo "EXP-08 DIFFERS from $prev"
grep -h "identity gate" "EXP-77b-gate-$sha.out"

s=$(date +%s); python -u EXP-08-pin0941.py > "EXP-08-pin0941-$sha.out.partial" 2> "EXP-08-pin0941-$sha.err"; rc=$?
mv "EXP-08-pin0941-$sha.out.partial" "EXP-08-pin0941-$sha.out"; echo "$(( $(date +%s) - s ))s exit $rc" > "EXP-08-pin0941-$sha.time"
tail -n +2 "EXP-08-pin0941-$sha.out" | cmp -s - <(tail -n +2 EXP-08-pin0941-b0b09d4.out) && echo "EXP-08 pinned BYTE-IDENTICAL to the 0.99.0 pinned run" || echo "EXP-08 pinned DIFFERS from the 0.99.0 pinned run"
