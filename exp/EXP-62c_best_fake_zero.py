"""
EXP-62c: EXP-62's harness on fresh seeds with the committed zero declared in advance as the best fake in a declared class:
anti-echo, the best labeller that sees only what the corrective schedule gives it (the executed action was wrong).
PRE-REGISTRATION: experiments/EXP-62c.md (written before the run). Runs EXP-62's script unchanged under these settings:

    TAG=full python -u EXP-62c_best_fake_zero.py
"""
import os

os.environ.setdefault("PREFIX", "EXP-62c")
os.environ.setdefault("CF", "anti-echo")
os.environ.setdefault("SEED_BASE", "6400000")
os.environ.setdefault("LENGTHS", "80")
os.environ.setdefault("STUDENTS", "72")
os.environ.setdefault("ARMS", "full")
__file__ = os.path.abspath(__file__)
exec(compile(open(os.path.join(os.path.dirname(__file__), "EXP-62_content_market_committed_null.py"), encoding="utf-8").read(),
             "EXP-62_content_market_committed_null.py", "exec"))
