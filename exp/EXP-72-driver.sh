#!/bin/sh
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
for s in 59101 59201 59202 59203 59204; do echo "$s"; done |
  xargs -P 5 -n 1 sh -c 'python -u EXP-72_v05b_surprise_from_start.py --seed $0 --heads 2 --teach surprise --out EXP-72-$0-H2.jsonl 2> EXP-72-$0-H2.err'
echo "EXP-72 driver done $(date)"
