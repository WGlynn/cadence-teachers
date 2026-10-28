"""EXP-78 analysis: surprise lessons vs Sean McClane's every-row lessons on single-frame Breakout.

Baselines: Sean's logged runs (cadence-arcade c8a5e4c, classic/runs/main.log), admitted by the
pre-registered identity check (seed 10, norecall and pos32, exact match incl. position-map size).
Surprise arms: exp/EXP-78-surprise/<arm>-<seed>.json from his run.py with learning_surprise=True.

Run:  ~/_ext/venv-arcade/Scripts/python.exe EXP-78_analyze.py
"""
import json
import re
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

HERE = Path(__file__).resolve().parent
SEAN_LOG = Path.home() / "_ext" / "sean-arcade" / "classic" / "runs" / "main.log"
SURPRISE = HERE / "EXP-78-surprise"
ARMS = ("pos32", "pos0", "norecall")
SEEDS = list(range(10, 22))


def sean_baselines():
    base = {}
    pat = re.compile(r"^(pos32|pos0|norecall) (\d+) primary ([\d.]+) agree ([\d.]+)")
    for line in SEAN_LOG.read_text(encoding="utf-8").splitlines():
        m = pat.match(line)
        if m:
            base[(m.group(1), int(m.group(2)))] = (float(m.group(3)), float(m.group(4)))
    return base


def surprise_runs():
    out = {}
    for f in SURPRISE.glob("*-*.json"):  # skips meta.json
        r = json.loads(f.read_text(encoding="utf-8"))
        out[(r["arm"], r["seed"])] = (float(r["primary"]), float(r["agree"][-1]), r.get("warned", {}))
    return out


def paired(name, a, b):
    d = np.array(a) - np.array(b)
    wins = int((d > 0).sum())
    try:
        p = wilcoxon(d).pvalue if np.any(d != 0) else 1.0
    except ValueError:
        p = float("nan")
    print(f"  {name}: mean {np.mean(a):.2f} vs {np.mean(b):.2f}; wins {wins}/{len(d)}; "
          f"median diff {np.median(d):+.2f}; Wilcoxon p={p:.3g}")
    return wins, float(np.median(d)), p


def main():
    base = sean_baselines()
    sur = surprise_runs()
    missing = [(a, s) for a in ARMS for s in SEEDS if (a, s) not in sur]
    if missing:
        print(f"INCOMPLETE: {len(missing)} surprise lives missing: {missing[:6]}")
    print("EXP-78: bricks per test episode, last 10 blocks (primary); final test agreement\n")
    print("arm       seed  every-row  surprise   agree(every-row -> surprise)")
    for a in ARMS:
        for s in SEEDS:
            if (a, s) in sur and (a, s) in base:
                print(f"{a:9s} {s:4d}  {base[(a,s)][0]:8.2f}  {sur[(a,s)][0]:8.2f}   {base[(a,s)][1]:.3f} -> {sur[(a,s)][1]:.3f}")
    print("\nP1 (surprise raises the recall arms; bar: >=8/12 wins, median diff > 0):")
    res = {}
    for a in ARMS:
        seeds = [s for s in SEEDS if (a, s) in sur and (a, s) in base]
        if len(seeds) < 2:
            continue
        res[a] = paired(f"{a} surprise vs every-row", [sur[(a, s)][0] for s in seeds], [base[(a, s)][0] for s in seeds])
    p1 = all(res[a][0] >= 8 and res[a][1] > 0 for a in ("pos32", "pos0") if a in res)
    print("\nP2 (recall seeds ending with test agreement < .75; bar: <= 1 of 24 under surprise):")
    low_base = sum(1 for a in ("pos32", "pos0") for s in SEEDS if (a, s) in base and base[(a, s)][1] < .75)
    low_sur = sum(1 for a in ("pos32", "pos0") for s in SEEDS if (a, s) in sur and sur[(a, s)][1] < .75)
    print(f"  every-row {low_base}/24, surprise {low_sur}/24")
    p2 = low_sur <= 1
    print("\nP3 (reported): pos32-surprise vs norecall-surprise")
    seeds = [s for s in SEEDS if ("pos32", s) in sur and ("norecall", s) in sur]
    if len(seeds) >= 2:
        paired("pos32-s vs norecall-s", [sur[("pos32", s)][0] for s in seeds], [sur[("norecall", s)][0] for s in seeds])
    warn = {a: sum(sur[(a, s)][2].get("unsettled", 0) for s in SEEDS if (a, s) in sur) for a in ARMS}
    print(f"\nunsettled-lesson warnings per arm (surprise runs): {warn}")
    verdict = "SUPPORTIVE" if (p1 and p2) else ("PARTIAL" if (p1 or p2) else "NOT SUPPORTED")
    print(f"\nP1 {'holds' if p1 else 'fails'}, P2 {'holds' if p2 else 'fails'} -> {verdict}"
          + (" (INCOMPLETE DATA)" if missing else ""))


if __name__ == "__main__":
    main()
