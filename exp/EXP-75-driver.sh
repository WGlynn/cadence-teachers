#!/bin/sh
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
for s in 59101 59201 59202 59203 59204; do echo "$s"; done |
  xargs -P 5 -n 1 sh -c 'python -u EXP-75_v05b_tolerance.py --seed $0 --out EXP-75-$0.jsonl 2> EXP-75-$0.err'
echo "EXP-75 driver done $(date)"
