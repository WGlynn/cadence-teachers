"""
EXP-12b — XOR-ceiling search. The smoke (EXP-12) showed copy-b1/b2 learn to 1.0 but XOR-from-scratch
caps at 0.5-0.75. Synergy is unmeasurable without a solid XOR ceiling (both+few-shot needs headroom).

XOR is non-linearly-separable: it needs a hidden representation that makes the two bits jointly
readable. The smoke's policy column had only patches=A=2 reading perception directly -- likely too
shallow. Here we search architecture x budget for a config where XOR-from-scratch reaches ~1.0:

  - depth: add a hidden column between perception and policy (perc -> hidden -> policy)
  - width: vary perception/hidden patch counts
  - budget: up to 2000 steps
  - 3 seeds each (XOR learnability is seed-sensitive at this scale)

If some config hits ~1.0 reliably, that is the substrate for the synergy harness. If nothing clears
~0.8 across seeds, that is the honest boundary: this substrate cannot cleanly represent XOR, so a
combination-only worth probe is inconclusive ON IT -- a real datapoint on Cadence #115, not a tuning
failure to hide.
"""
import cadence
from cadence.experimental.equilibrium import Cortex, Reinforcement
import itertools

print("cadence", cadence.__version__, flush=True)

A = 2
CTX = [(0, 0), (0, 1), (1, 0), (1, 1)]
onehot2 = lambda b: [1.0, 0.0] if b == 0 else [0.0, 1.0]
onehot3 = lambda k: [1.0 if i == k else 0.0 for i in range(3)]
obs = lambda b1, b2, cue: {"c1": onehot2(b1), "c2": onehot2(b2), "cue": onehot3(cue)}
xor = lambda b1, b2: b1 ^ b2


def build(P, H, seed, depth):
    cx = Cortex(seed=seed, fan_in=9, parameter_prior=0.3, tolerance=1e-3, settle_budget=64)
    s1 = cx.input("c1", shape=2); s2 = cx.input("c2", shape=2); cue = cx.input("cue", shape=3)
    perc = cx.column("perception", patches=P, inputs=(s1, s2))
    if depth == 2:
        hid = cx.column("hidden", patches=H, inputs=(perc,))
        pol = cx.column("policy", patches=A, inputs=(hid, cue))
    else:
        pol = cx.column("policy", patches=A, inputs=(perc, cue))
    for i in range(A):
        cx.output(f"a{i}", shape=1, reads=pol, indices=(i,))
    return Reinforcement(cx.build(), actions=A, action_input=None,
                         value_output=tuple(f"a{i}" for i in range(A)),
                         discount=0.0, exploration=0.1, reward_scale=4.0,
                         capacity=128, batch_size=4, seed=seed)


def greedy(cr, b1, b2):
    d = cr.act(obs(b1, b2, 0), explore=False); cr.reset(); return d["action"]


def accxor(cr):
    return sum(int(greedy(cr, b1, b2) == xor(b1, b2)) for b1, b2 in CTX) / 4


def train_xor(cr, steps):
    cyc = itertools.cycle(CTX)
    for t in range(steps):
        b1, b2 = next(cyc)
        d = cr.act(obs(b1, b2, 0))
        if d["action"] is None:
            cr.reset(); continue
        a = d["action"]
        r = 1.0 if a == xor(b1, b2) else -1.0
        nb1, nb2 = CTX[(t + 1) % 4]
        cr.feedback(r, obs(nb1, nb2, 0), decision_id=d["decision_id"], executed_action=a)


CONFIGS = [
    ("shallow P6",       dict(P=6,  H=0, depth=1)),
    ("shallow P12",      dict(P=12, H=0, depth=1)),
    ("deep P6-H6",       dict(P=6,  H=6, depth=2)),
    ("deep P8-H8",       dict(P=8,  H=8, depth=2)),
    ("deep P12-H12",     dict(P=12, H=12, depth=2)),
]
STEPS = 2000
SEEDS = (7, 11, 23)

for name, kw in CONFIGS:
    accs = []
    for sd in SEEDS:
        cr = build(seed=sd, **kw)
        train_xor(cr, STEPS)
        accs.append(accxor(cr))
    mean = sum(accs) / len(accs)
    print(f"  {name:16s} steps={STEPS}  xor_acc per-seed {['%.2f'%a for a in accs]}  mean {mean:.2f}", flush=True)
