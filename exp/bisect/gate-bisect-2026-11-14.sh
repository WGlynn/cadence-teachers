#!/bin/bash
# Localize the 0.94.0 -> 0.99.0 identity-gate drift (monitor 2026-11-14). Each tag in its own worktree,
# imported through PYTHONPATH, gate run with LATERAL=-0.5 PIN0940=1 GATE=1.
set -u
export PYTHONUTF8=1
EXP=~/cadence-lab/exp
for tag in "$@"; do
  wt=~/_cadence_bisect_$tag
  [ -d "$wt" ] || git -C ~/_cadence_study worktree add -q --detach "$wt" "$tag"
  v=$(cd "$EXP" && PYTHONPATH="$wt/src" python -c "import cadence;print(cadence.__version__)")
  s=$(date +%s)
  line=$(cd "$EXP" && PYTHONPATH="$wt/src" LATERAL=-0.5 PIN0940=1 GATE=1 python -u EXP-73_m1b_measured_zero.py 2>"$EXP/bisect/gate-$tag.err" | tee "$EXP/bisect/gate-$tag.out" | grep "identity gate")
  echo "$tag (imported $v, $(( $(date +%s) - s ))s): ${line#*: }"
done
