"""Setup check (~10 s): Cadence imports, a brain learns a 4-context bandit, the key-door benchmark loads,
and every experiment has its write-up. Run: python exp/smoke_test.py"""
import os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cadence
from cadence import Brain
print(f"cadence {getattr(cadence, '__version__', '?')} from {os.path.dirname(cadence.__file__)}")

K, RULE = 4, np.array([0, 1, 1, 0])
b = Brain.compose(inputs=K, actions=2, modules=(16, 8), seed=1, arousal=True)
reward = None
for t in range(1600):
    c = t % K
    x = np.eye(K)[[c]]
    a = b.live(x) if reward is None else b.live(x, reward=reward, done=np.array([True]))
    a = int(np.asarray(a).reshape(-1)[0])
    reward = np.array([1.0 if a == RULE[c] else -1.0])
acc = np.mean([int(np.asarray(b.act(np.eye(K)[[c]], greedy=True)).reshape(-1)[0]) == RULE[c] for c in range(K)])
print(f"bandit accuracy after training: {acc:.2f} (expect >= 0.75)")

from _cadence_src import KEYDOOR
sys.path.insert(0, KEYDOOR)
import key_door  # noqa: F401
print(f"key-door benchmark found at {KEYDOOR}")

rc = subprocess.call([sys.executable, os.path.join(HERE, "..", "experiments", "check.py")])
ok = acc >= 0.75 and rc == 0
print("SMOKE TEST", "PASSED" if ok else "FAILED")
sys.exit(0 if ok else 1)
