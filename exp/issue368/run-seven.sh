#!/bin/bash
# Reproduce cadence #368 per file on Windows (default checkout, autocrlf=true). Log per file.
cd ~/_cadence_study
OUT=~/cadence-lab/exp/issue368
for f in benchmarks/acquisition/test_confirmation_verifier.py tests/test_documentation.py benchmarks/attention/test_look_back.py benchmarks/stream_words/test_stream_words.py benchmarks/attention/test_contextual_choice.py benchmarks/recall/test_finite_horizon.py benchmarks/attention/test_retained_receipts.py; do
  n=$(basename $f .py)
  s=$(date +%s)
  timeout 900 python -m pytest -q -p no:cacheprovider --tb=short -rf "$f" > $OUT/$n.log 2>&1
  echo "$n exit=$? secs=$(( $(date +%s) - s )) $(tail -1 $OUT/$n.log)" >> $OUT/summary.txt
done
echo DONE >> $OUT/summary.txt
