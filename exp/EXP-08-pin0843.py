"""EXP-08 on a release with the 0.84.3 founder laws pinned back, to separate announced founder changes
from anything else.

0.85.0 changed three founders that EXP-08 reaches: an unset motor `lateral` resolves to 0.0 (#220),
`ArousalConfig.need_scale` defaults to 0.1 (#198), and `Brain.reset()` keeps the arousal state (#213).
This wrapper runs EXP-08 unchanged except that it pins `lateral=-0.5`, `need_scale=0.0` and
`reset(keep=())`, the 0.84.3 behaviour of each. If the release changed nothing else EXP-08 depends on,
the output equals the 0.84.3 baseline (+0.422 / -0.109 / -0.578) exactly.

Run: python -u EXP-08-pin0843.py > EXP-08-pin0843-<sha>.out
"""
import functools
import importlib.util
import pathlib

import cadence
from cadence import ArousalConfig, Brain

spec = importlib.util.spec_from_file_location(
    "exp08", pathlib.Path(__file__).with_name("EXP-08_vs_transfer_separation.py"))
exp08 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exp08)

_compose = Brain.compose.__func__ if hasattr(Brain.compose, "__func__") else Brain.compose


@classmethod
def compose_pinned(cls, *args, **kw):
    kw.setdefault("lateral", -0.5)
    return _compose(cls, *args, **kw)


_reset = Brain.reset


def reset_pinned(self, *, keep=(), **kw):
    return _reset(self, keep=keep, **kw)


Brain.compose = compose_pinned
Brain.reset = reset_pinned
exp08.Brain = Brain
exp08.ArousalConfig = functools.partial(ArousalConfig, need_scale=0.0)

if __name__ == "__main__":
    print(f"EXP-08 pinned to 0.84.3 founders on cadence {cadence.__version__}: "
          "lateral=-0.5, need_scale=0.0, reset(keep=())", flush=True)
    exp08.main()
