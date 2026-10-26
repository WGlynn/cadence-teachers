#!/bin/sh
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
for s in 59101 59204 59203; do echo "$s"; done |
  xargs -P 3 -n 1 sh -c 'python -u EXP-74_calm_switch_step_spike.py --seed $0 --out EXP-74-$0.jsonl 2> EXP-74-$0.err'
echo "EXP-74 driver done $(date)"
