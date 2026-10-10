"""
EXP-11 smoke — can an equilibrium Reinforcement creature (the patch-world substrate) (a) learn a
trivial 4-context bandit on current cadence 0.78, and (b) snapshot/from_snapshot to a TRUE twin?

This de-risks the M2-synergy build before committing to it: if the richer substrate can't learn a
toy bandit cheaply, or the twin fork isn't exact, we find out in 30 lines, not 300.
"""
import numpy as np
import cadence
from cadence.experimental.equilibrium import Cortex, Reinforcement

print("cadence", cadence.__version__)
K, A = 4, 2
RULE = [0, 0, 1, 1]
onehot = lambda c: {"senses": [1.0 if i == c else 0.0 for i in range(K)]}


def build(seed=7):
    cx = Cortex(seed=seed, fan_in=9, parameter_prior=0.3, tolerance=1e-3, settle_budget=64)
    s = cx.input("senses", shape=K)
    perc = cx.column("perception", patches=6, inputs=s)
    pol = cx.column("policy", patches=A, inputs=(s, perc))
    for i in range(A):
        cx.output(f"a{i}", shape=1, reads=pol, indices=(i,))
    brain = cx.build()
    return Reinforcement(brain, actions=A, action_input=None,
                         value_output=tuple(f"a{i}" for i in range(A)),
                         discount=0.0, exploration=0.1, reward_scale=4.0,
                         capacity=128, batch_size=4, seed=seed)


def greedy(cr, c):
    """Pure eval: greedy action, no learning (reset discards the pending proposal)."""
    d = cr.act(onehot(c), explore=False)
    cr.reset()
    return d["action"]


def acc(cr):
    return sum(int(greedy(cr, c) == RULE[c]) for c in range(K)) / K


def train(cr, steps):
    reward, pend, c = None, None, 0
    for t in range(steps):
        c = t % K
        d = cr.act(onehot(c))
        if d["action"] is None:
            cr.reset(); continue
        a = d["action"]
        r = 1.0 if a == RULE[c] else -1.0
        cr.feedback(r, onehot((t + 1) % K), decision_id=d["decision_id"], executed_action=a)


cr = build(7)
print("acc before:", acc(cr))
train(cr, 400)
print("acc after 400:", acc(cr))

# twin test: snapshot, fork, both act greedily on all contexts -> identical
snap = cr.snapshot()
twin = Reinforcement.from_snapshot(snap)
a_main = [greedy(cr, c) for c in range(K)]
a_twin = [greedy(twin, c) for c in range(K)]
print("main greedy:", a_main)
print("twin greedy:", a_twin)
print("TWIN EXACT:", a_main == a_twin, "| snapshot bytes:", len(snap))
