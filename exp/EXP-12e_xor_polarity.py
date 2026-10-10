"""
EXP-12e — is deep-XOR acc 0.00 actually PERFECT XNOR (inverted readout), not a representation/credit
failure? XOR targets = [0,1,1,0]; acc 0.00 => actions [1,0,0,1] = XNOR = the exact complement.

Representing XNOR requires the SAME joint-two-bit computation as XOR. So acc 0.00 (if it is clean
XNOR) means the deep creature DID learn the relation and reads it out inverted -> depth CAN represent
XOR, synergy is buildable on depth, and Dongyang's deep-credit speedup becomes relevant. Contrast:
acc ~0.50 with mixed/constant actions = genuine non-learning.

Cheap + decisive: train deep XOR (sb=48, 1500 steps), dump per-context greedy actions per seed, and
report both acc and (1 - acc) = "acc if readout were flipped". Also train deep copy-b1 as a control:
if the deep stack learns a 1-bit task fine, raw credit starvation is ruled out.
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


def build(P, H, seed, sb=48):
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


def greedy(cr, b1, b2, cue):
    d = cr.act(obs(b1, b2, cue), explore=False); cr.reset(); return d["action"]


def train(cr, cue, fn, steps):
    cyc = itertools.cycle(CTX)
    for t in range(steps):
        b1, b2 = next(cyc)
        d = cr.act(obs(b1, b2, cue))
        if d["action"] is None:
            cr.reset(); continue
        a = d["action"]
        r = 1.0 if a == fn(b1, b2) else -1.0
        nb1, nb2 = CTX[(t + 1) % 4]
        cr.feedback(r, obs(nb1, nb2, cue), decision_id=d["decision_id"], executed_action=a)


print("XOR targets per ctx", [xor(b1, b2) for b1, b2 in CTX], flush=True)
print("\n[deep XOR, P6-H6, sb48, 1500 steps] — action dump + acc + flipped-acc", flush=True)
for sd in (7, 11, 23):
    cr = build(6, 6, sd); train(cr, 0, xor, 1500)
    acts = [greedy(cr, b1, b2, 0) for b1, b2 in CTX]
    acc = sum(int(acts[i] == xor(*CTX[i])) for i in range(4)) / 4
    clean_xnor = all(acts[i] == 1 - xor(*CTX[i]) for i in range(4))
    print(f"  seed{sd:>2}: actions {acts}  acc {acc:.2f}  flipped_acc {1-acc:.2f}  clean_XNOR={clean_xnor}", flush=True)

print("\n[control: deep copy-b1, P6-H6, sb48, 600 steps] — does the deep stack learn a 1-bit task?", flush=True)
for sd in (7, 11):
    cr = build(6, 6, sd); train(cr, 1, (lambda b1, b2: b1), 600)
    acts = [greedy(cr, b1, b2, 1) for b1, b2 in CTX]
    acc = sum(int(acts[i] == CTX[i][0]) for i in range(4)) / 4
    print(f"  seed{sd:>2}: actions {acts}  copyb1_acc {acc:.2f}", flush=True)
