"""
EXP-12c — does DEPTH let an equilibrium creature learn XOR? The pivot experiment.

Shallow (2-column) creature caps at XOR acc 0.50 (EXP-12/12b). This decides TWO threads at once:
  - synergy: a combination-only (XOR) worth probe needs the substrate to represent XOR at all;
  - Dongyang speedup relevance: his method dissolves DEEP-stack settling cost. We only go deep if
    depth is the XOR fix -> only then is his method our lever.

Deep configs only (shallow already answered 0.50). Added hidden column: perc(P) -> hidden(H) ->
policy(2), policy reads (hidden, cue). 3 seeds, 2000 steps. Honest: still single-task XOR from
scratch, small nets, few seeds; a clean ~1.0 means depth represents XOR, a stuck ~0.5 means this
substrate/rule can't and synergy needs a different design (and Dongyang's speedup is not our lever).
"""
import cadence
from cadence.experimental.equilibrium import Cortex, Reinforcement
import itertools

print("cadence", cadence.__version__, flush=True)
A = 2
CTX = [(0, 0), (0, 1), (1, 0), (1, 1)]
oh2 = lambda b: [1.0, 0.0] if b == 0 else [0.0, 1.0]
oh3 = lambda k: [1.0 if i == k else 0.0 for i in range(3)]
obs = lambda b1, b2, cue: {"c1": oh2(b1), "c2": oh2(b2), "cue": oh3(cue)}
xor = lambda b1, b2: b1 ^ b2


def build(P, H, seed):
    cx = Cortex(seed=seed, fan_in=9, parameter_prior=0.3, tolerance=1e-3, settle_budget=48)
    s1 = cx.input("c1", shape=2); s2 = cx.input("c2", shape=2); cue = cx.input("cue", shape=3)
    perc = cx.column("perception", patches=P, inputs=(s1, s2))
    hid = cx.column("hidden", patches=H, inputs=(perc,))
    pol = cx.column("policy", patches=A, inputs=(hid, cue))
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


CONFIGS = [("deep P6-H6", 6, 6), ("deep P8-H8", 8, 8), ("deep P12-H12", 12, 12)]
STEPS = 2000
SEEDS = (7, 11, 23)
print(f"{'config':16s} {'xor per-seed':>24} {'mean':>6}", flush=True)
for name, P, H in CONFIGS:
    accs = []
    for sd in SEEDS:
        cr = build(P, H, sd)
        train_xor(cr, STEPS)
        accs.append(accxor(cr))
    print(f"{name:16s} {str(['%.2f'%a for a in accs]):>24} {sum(accs)/len(accs):>6.2f}", flush=True)
