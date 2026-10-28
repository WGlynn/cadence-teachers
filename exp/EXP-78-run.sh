#!/bin/sh
# EXP-78: Sean McClane's cadence-arcade (c8a5e4c) classic/run.py, unchanged, with surprise lessons.
# Venv ~/_ext/venv-arcade: Cadence 0.89.0 from ~/_cadence_0890, numpy 2.5.4, minatar 1.0.15, no numba
# (the configuration whose seed-10 identity check matched Sean's log exactly: exp/EXP-78-identity).
cd ~/_ext/sean-arcade/classic && ../../venv-arcade/Scripts/python.exe run.py --arms pos32,pos0,norecall --seeds 10-21 --procs 4 --cadence '{"learning_surprise": true}' --out ~/cadence-lab/exp/EXP-78-surprise
