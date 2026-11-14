"""EXP-08 on a release with the 0.94.0 composition pinned back, to separate announced default changes
from anything else.

0.95.0 made the recall memory part of every new brain and `backend="auto"` the default of
`Brain.compose`; `recall=False` on `backend="cpu"` composes what 0.94.0 composed. 0.97.0 changed
`history_decays` to (0.0,) and `memory_rate` to 0.2; `history_decays=()` with `memory_rate=1.0`
composes the brain of 0.96.1. 0.98.0 and 0.99.0 changed no default. This wrapper runs EXP-08 unchanged
except that it names those four. If the releases changed nothing else EXP-08 depends on, the output
after the header line equals the 0.93.1 run (`EXP-08-v0931-a4fcea0.out`) exactly.

Run: python -u EXP-08-pin0941.py > EXP-08-pin0941-<sha>.out
"""
import importlib.util
import pathlib

import cadence
from cadence import Brain

spec = importlib.util.spec_from_file_location(
    "exp08", pathlib.Path(__file__).with_name("EXP-08_vs_transfer_separation.py"))
exp08 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exp08)

_compose = Brain.compose.__func__ if hasattr(Brain.compose, "__func__") else Brain.compose


@classmethod
def compose_pinned(cls, *args, **kw):
    kw.setdefault("recall", False)
    kw.setdefault("backend", "cpu")
    kw.setdefault("history_decays", ())
    kw.setdefault("memory_rate", 1.0)
    return _compose(cls, *args, **kw)


Brain.compose = compose_pinned
exp08.Brain = Brain

if __name__ == "__main__":
    print(f"EXP-08 pinned to the 0.94.0 composition on cadence {cadence.__version__}: "
          "recall=False, backend=cpu, history_decays=(), memory_rate=1.0", flush=True)
    exp08.main()
