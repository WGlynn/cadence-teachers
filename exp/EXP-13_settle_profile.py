"""
EXP-13 — profile the settle bottleneck BEFORE reverse-engineering Dongyang's algorithmic speedup.

Dongyang's 15x came from linearised (beta->0) settling that cuts settle sweeps; the holographic
channel only helps DEEP stacks (ours are 2-3 columns). cadence's own ACCELERATION.md is GPU/batch
(orthogonal). So the question is: what does our per-step cost actually look like, and does cadence's
EXISTING settle_budget / tolerance knob already buy most of the speedup on OUR shallow creatures?

Measure, per settle_budget, on the equilibrium Reinforcement creature used in EXP-11/12:
  - ms per training step (the thing multiplied by 1600 x seeds in witness ingest)
  - learn quality: copy-b1 accuracy after a fixed step budget (fast proxy for "did it still learn")

If low settle_budget is ~as accurate and much faster, that is the 1-line speedup and Dongyang's
algorithmic port is unnecessary at our depth. If accuracy collapses as budget drops, the sweeps are
load-bearing and the linearised mode is worth porting. Insight is the number.
"""
import time, itertools
import cadence
from cadence.experimental.equilibrium import Cortex, Reinforcement

print("cadence", cadence.__version__, flush=True)
A = 2
CTX = [(0, 0), (0, 1), (1, 0), (1, 1)]
oh2 = lambda b: [1.0, 0.0] if b == 0 else [0.0, 1.0]
oh3 = lambda k: [1.0 if i == k else 0.0 for i in range(3)]
obs = lambda b1, b2, cue: {"c1": oh2(b1), "c2": oh2(b2), "cue": oh3(cue)}


def build(settle_budget, seed=7):
    cx = Cortex(seed=seed, fan_in=9, parameter_prior=0.3, tolerance=1e-3, settle_budget=settle_budget)
    s1 = cx.input("c1", shape=2); s2 = cx.input("c2", shape=2); cue = cx.input("cue", shape=3)
    perc = cx.column("perception", patches=6, inputs=(s1, s2))
    pol = cx.column("policy", patches=A, inputs=(perc, cue))
    for i in range(A):
        cx.output(f"a{i}", shape=1, reads=pol, indices=(i,))
    return Reinforcement(cx.build(), actions=A, action_input=None,
                         value_output=tuple(f"a{i}" for i in range(A)),
                         discount=0.0, exploration=0.1, reward_scale=4.0,
                         capacity=128, batch_size=4, seed=seed)


def greedy(cr, b1, b2, cue):
    d = cr.act(obs(b1, b2, cue), explore=False); cr.reset(); return d["action"]


def acc_copyb1(cr):
    return sum(int(greedy(cr, b1, b2, 1) == b1) for b1, b2 in CTX) / 4


def train_copyb1(cr, steps):
    cyc = itertools.cycle(CTX)
    for t in range(steps):
        b1, b2 = next(cyc)
        d = cr.act(obs(b1, b2, 1))
        if d["action"] is None:
            cr.reset(); continue
        a = d["action"]
        r = 1.0 if a == b1 else -1.0
        nb1, nb2 = CTX[(t + 1) % 4]
        cr.feedback(r, obs(nb1, nb2, 1), decision_id=d["decision_id"], executed_action=a)


STEPS = 300
print(f"{'settle_budget':>13} {'ms/step':>9} {'copyb1_acc':>11}", flush=True)
for sb in (64, 32, 16, 8, 4, 2):
    cr = build(sb)
    t0 = time.perf_counter()
    train_copyb1(cr, STEPS)
    dt = (time.perf_counter() - t0) / STEPS * 1000
    print(f"{sb:>13} {dt:>9.1f} {acc_copyb1(cr):>11.2f}", flush=True)
