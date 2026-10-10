"""
EXP-12d — THE discriminator: is deep-XOR failure (EXP-12c: 0.00) credit-STARVATION-at-depth, or
fundamental? This decides whether Dongyang's method is our lever.

EXP-12c: deep creatures (perc->hidden->policy, settle_budget=48) hit XOR acc 0.00 -- systematically
wrong, WORSE than shallow chance 0.50. 0.00 is the signature of the front (perception) column never
learning the bit-features -> the exact "front layers barely learn" deep-credit-propagation problem
Dongyang's holographic/linearised method dissolves (settled credit = e_l = J^T e_{l+1}, reached only
after ~L^2 sweeps; a finite settle_budget starves it).

Test: hold the deep arch fixed, SWEEP settle_budget. More settling = better credit propagation to the
front = the expensive thing Dongyang makes cheap. If XOR acc RISES with budget -> credit-starvation
confirmed -> deep synergy needs cheap-deep-credit = Dongyang's method is directly our lever. If it
stays ~0 at large budget -> not a settling problem; his method is not our lever, synergy needs a
different substrate. Per-context action dump (seed 7, top budget) distinguishes degenerate-constant
from inverted-eval from genuinely-wrong. Insight is the number; either outcome is a real result.
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


def build(P, H, seed, settle_budget):
    cx = Cortex(seed=seed, fan_in=9, parameter_prior=0.3, tolerance=1e-3, settle_budget=settle_budget)
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


P, H, STEPS, SEEDS = 6, 6, 3000, (7, 11, 23)
print(f"deep P{P}-H{H}, steps={STEPS}, XOR targets per ctx {[xor(b1,b2) for b1,b2 in CTX]}", flush=True)
print(f"{'settle_budget':>13} {'xor per-seed':>24} {'mean':>6}", flush=True)
for sb in (48, 120, 240):
    accs = []
    for sd in SEEDS:
        cr = build(P, H, sd, sb)
        train_xor(cr, STEPS)
        accs.append(accxor(cr))
        if sd == 7 and sb == 240:
            acts = [greedy(cr, b1, b2) for b1, b2 in CTX]
            print(f"   [seed7 sb240 action dump] ctx{CTX} -> actions {acts} (target {[xor(b1,b2) for b1,b2 in CTX]})", flush=True)
    print(f"{sb:>13} {str(['%.2f'%a for a in accs]):>24} {sum(accs)/len(accs):>6.2f}", flush=True)
