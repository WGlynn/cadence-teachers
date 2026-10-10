"""
EXP-12f — THE Dongyang-relevance decider. Deep XOR at sb=48 returns None on every context (never
qualifies an action -> never gets feedback -> never trains; EXP-12e). copy-b1 deep learns fine, so
the deep stack is not broken generally -- XOR specifically won't settle to an action.

Question: does MORE settling budget let the (untrained) deep creature qualify an action on XOR, start
getting feedback, and learn? Instrument the ACTUAL diagnostic: the None-rate during training.
  - None-rate drops with budget AND acc climbs  => settling-bound => Dongyang's cheap-settling IS our
    lever (his method makes the expensive deep convergence cheap).
  - None-rate stays ~1.0 at high budget          => XOR un-settleable on this arch; his method
    accelerates a convergence that does not exist here -> NOT our lever; synergy needs a different task.

Lean: sb in {100, 220}, 1 seed, 800 steps. Report None-rate (first half / second half of training),
final greedy actions, acc. Honest: 1 seed, small net; a clear direction is enough to decide the port.
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


def build(P, H, seed, sb):
    cx = Cortex(seed=seed, fan_in=9, parameter_prior=0.3, tolerance=1e-3, settle_budget=sb)
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


def train_xor_track_none(cr, steps):
    cyc = itertools.cycle(CTX)
    none_first = none_second = 0
    half = steps // 2
    for t in range(steps):
        b1, b2 = next(cyc)
        d = cr.act(obs(b1, b2, 0))
        if d["action"] is None:
            if t < half: none_first += 1
            else: none_second += 1
            cr.reset(); continue
        a = d["action"]
        r = 1.0 if a == xor(b1, b2) else -1.0
        nb1, nb2 = CTX[(t + 1) % 4]
        cr.feedback(r, obs(nb1, nb2, 0), decision_id=d["decision_id"], executed_action=a)
    return none_first / half, none_second / (steps - half)


STEPS = 800
print(f"deep P6-H6, XOR, {STEPS} steps. XOR targets {[xor(*c) for c in CTX]}", flush=True)
print(f"{'settle_budget':>13} {'None%_1stHalf':>13} {'None%_2ndHalf':>13} {'final_actions':>16} {'acc':>5}", flush=True)
for sb in (100, 220):
    cr = build(6, 6, 7, sb)
    nf, ns = train_xor_track_none(cr, STEPS)
    acts = [greedy(cr, b1, b2) for b1, b2 in CTX]
    acc = sum(int(acts[i] == xor(*CTX[i])) for i in range(4)) / 4
    print(f"{sb:>13} {nf*100:>12.0f}% {ns*100:>12.0f}% {str(acts):>16} {acc:>5.2f}", flush=True)
