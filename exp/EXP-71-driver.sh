#!/bin/sh
# EXP-71 driver: 10 jobs (5 founders x 2 arms), 5 at a time, single-threaded BLAS.
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
for h in 2 1; do for s in 59101 59201 59202 59203 59204; do echo "$s $h"; done; done |
  xargs -P 5 -n 2 sh -c 'python -u EXP-71_v05b_fit_vs_generalize.py --seed $0 --heads $1 --out EXP-71-$0-H$1.jsonl 2> EXP-71-$0-H$1.err'
echo "EXP-71 driver done $(date)"
