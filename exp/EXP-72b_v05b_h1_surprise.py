"""EXP-72b: EXP-72's one-head arm. Runs EXP-72's script unchanged with --heads 1 (learning_surprise from lesson 0),
so one head and two heads can be compared under stable teaching on the same founders and lesson stream.
Pre-registration: experiments/EXP-72b.md.

    python -u EXP-72b_v05b_h1_surprise.py --seed 59201 --out EXP-72b-59201-H1.jsonl
"""
import pathlib, runpy, sys
sys.argv = [sys.argv[0], "--heads", "1", "--teach", "surprise"] + sys.argv[1:]
runpy.run_path(str(pathlib.Path(__file__).with_name("EXP-72_v05b_surprise_from_start.py")), run_name="__main__")
