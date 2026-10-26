"""EXP-08 determinism probe (2026-10-25): run chosen seeds of EXP-08 and print each seed's row, to test whether the
fake_random arm is reproducible run to run (BLAS threads, CPU load) or moved by a code change. Path-isolated (EXP-08's
per-process temp dir). Usage: SEEDS=7,12 PYTHONPATH=<worktree>/src python -u EXP-08-determinism.py"""
import importlib.util, os, pathlib, cadence
spec = importlib.util.spec_from_file_location("exp08", pathlib.Path(__file__).with_name("EXP-08_vs_transfer_separation.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
for s in [int(x) for x in os.environ["SEEDS"].split(",")]:
    print(cadence.__version__, os.environ.get("OMP_NUM_THREADS", "default"), s, m.run_seed(s), flush=True)
