"""Latch diagnostic for EXP-43: replay one arm's first pass, log saturation / trace / action share every 500 steps.
usage: python EXP-43_diag_latch.py <arm> <seed> [json genes for Brain.compose]"""
import importlib.util, json, sys
from collections import Counter
import numpy as np
spec = importlib.util.spec_from_file_location("e43", __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "EXP-43_judged_grades.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
from cadence import ArousalConfig, Brain
arm, seed = sys.argv[1], int(sys.argv[2])
genes = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
kind, n, always = m.split(arm)
brain = Brain.compose(inputs=n * m.V, actions=m.V, modules=m.MODULES, seed=10_000 * (seed + 1) + 42,
                      arousal=None if always else ArousalConfig(), **genes)
d = brain.describe()
print({k: v for k, v in (d.items() if isinstance(d, dict) else []) if any(s in k for s in ("eta", "cap", "temperature"))} or str(d)[:600])
move = brain.step if always else brain.live
a, _ = m.corpus(); t = m.Teacher(n + 1); reward = None
acts, hits, sats, trs = Counter(), 0, [], []
for i in range(len(a)):
    x = m.window(a, i, n)
    act = int(np.asarray(move(x) if reward is None else move(x, reward=reward, done=np.array([True]))).reshape(-1)[0])
    acts[act] += 1; hits += act == m.IDX[a[i]]
    rep = brain.last_learning or {}
    if "saturation" in rep: sats.append(rep["saturation"]); trs.append(rep["trace"])
    reward = np.array([m.grade(kind, t, a, i, act)]); t.tell(a, i)
    if (i + 1) % 500 == 0:
        top, cnt = acts.most_common(1)[0]
        print(f"{i+1:6d} acc {hits/500:.3f} top '{m.ALPHA[top]}' {cnt/500:.2f} learned {len(sats)}/500 "
              f"saturation {np.mean(sats) if sats else float('nan'):.2f} trace {np.mean(trs) if trs else float('nan'):.4f}", flush=True)
        acts, hits, sats, trs = Counter(), 0, [], []
