#!/bin/sh
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
for s in 59101 59201 59202 59203 59204; do echo "$s"; done |
  xargs -P 5 -n 1 sh -c 'python -u EXP-72b_v05b_h1_surprise.py --seed $0 --out EXP-72b-$0-H1.jsonl 2> EXP-72b-$0-H1.err'
echo "EXP-72b driver done $(date)"
