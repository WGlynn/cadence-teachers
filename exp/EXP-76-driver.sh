#!/bin/sh
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
for s in 76101 76102 76103 76104 76105; do for h in 1 2 3; do echo "$s $h"; done; done |
  xargs -P 5 -n 2 sh -c 'python -u EXP-76_v05c_three_facts.py --seed $0 --heads $1 --out EXP-76-$0-H$1.jsonl 2> EXP-76-$0-H$1.err'
echo "EXP-76 driver done $(date)"
