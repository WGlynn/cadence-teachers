"""
EXP-12 smoke — de-risk the M2-SYNERGY build before committing to the full conditions.

The synergy design needs a factored-input creature with a PERCEPTION BOTTLENECK and a task-cue so
auxiliary witness tasks (copy-b1, copy-b2) and the held-out XOR task can share one brain without a
conflicting-policy collision. Before running the 4 conditions x F-sweep x seeds, verify in ~40 lines:

  (a) copy-b1  (cue=1, correct action = b1)  is LEARNABLE,
  (b) copy-b2  (cue=2, correct action = b2)  is LEARNABLE,
  (c) XOR      (cue=0, correct action = b1^b2) is LEARNABLE FROM SCRATCH (the ceiling — if the
      bottleneck is so tight XOR can't form even with both bits available, the probe is moot),
  (d) the snapshot/from_snapshot twin is still EXACT with multi-input + cue.

If all four hold at some perception-patch count P, the full synergy harness is buildable. Insight is
the number; a failure here is a real finding about the substrate, not something to tune away.
"""
import cadence
from cadence.experimental.equilibrium import Cortex, Reinforcement

print("cadence", cadence.__version__, flush=True)

A = 2
# 4 contexts (b1,b2). cue one-hot(3): 0=XOR(held-out T), 1=copy-b1, 2=copy-b2.
CTX = [(0, 0), (0, 1), (1, 0), (1, 1)]
onehot2 = lambda b: [1.0, 0.0] if b == 0 else [0.0, 1.0]
onehot3 = lambda k: [1.0 if i == k else 0.0 for i in range(3)]


def obs(b1, b2, cue):
    return {"c1": onehot2(b1), "c2": onehot2(b2), "cue": onehot3(cue)}


def target(b1, b2, cue):
    if cue == 1:
        return b1
    if cue == 2:
        return b2
    return b1 ^ b2


def build(P, seed=7):
    cx = Cortex(seed=seed, fan_in=9, parameter_prior=0.3, tolerance=1e-3, settle_budget=64)
    s1 = cx.input("c1", shape=2)
    s2 = cx.input("c2", shape=2)
    cue = cx.input("cue", shape=3)
    # Perception sees ONLY the bit channels (the bottleneck that can lose an un-taught bit).
    perc = cx.column("perception", patches=P, inputs=(s1, s2))
    # Policy reads perception + cue -> can route conditionally without needing raw bits.
    pol = cx.column("policy", patches=A, inputs=(perc, cue))
    for i in range(A):
        cx.output(f"a{i}", shape=1, reads=pol, indices=(i,))
    brain = cx.build()
    return Reinforcement(brain, actions=A, action_input=None,
                         value_output=tuple(f"a{i}" for i in range(A)),
                         discount=0.0, exploration=0.1, reward_scale=4.0,
                         capacity=128, batch_size=4, seed=seed)


def greedy(cr, b1, b2, cue):
    d = cr.act(obs(b1, b2, cue), explore=False)
    cr.reset()
    return d["action"]


def acc(cr, cue):
    return sum(int(greedy(cr, b1, b2, cue) == target(b1, b2, cue)) for b1, b2 in CTX) / len(CTX)


def train(cr, cue, steps, seed=0):
    # cycle the 4 contexts under a fixed cue
    import itertools
    cyc = itertools.cycle(CTX)
    for t in range(steps):
        b1, b2 = next(cyc)
        d = cr.act(obs(b1, b2, cue))
        if d["action"] is None:
            cr.reset(); continue
        a = d["action"]
        r = 1.0 if a == target(b1, b2, cue) else -1.0
        nb1, nb2 = CTX[(t + 1) % 4]
        cr.feedback(r, obs(nb1, nb2, cue), decision_id=d["decision_id"], executed_action=a)


for P in (4, 6, 8):
    print(f"\n=== P(perception patches) = {P} ===", flush=True)
    # (a) copy-b1
    cr = build(P, 7); train(cr, 1, 400); print(f"  copy-b1 acc after 400: {acc(cr,1):.2f}", flush=True)
    # (b) copy-b2
    cr = build(P, 7); train(cr, 2, 400); print(f"  copy-b2 acc after 400: {acc(cr,2):.2f}", flush=True)
    # (c) XOR from scratch (ceiling)
    cr = build(P, 7); train(cr, 0, 800); print(f"  XOR-from-scratch acc after 800: {acc(cr,0):.2f}", flush=True)
    # (d) twin exact
    snap = cr.snapshot(); twin = Reinforcement.from_snapshot(snap)
    m = [greedy(cr, b1, b2, 0) for b1, b2 in CTX]
    tw = [greedy(twin, b1, b2, 0) for b1, b2 in CTX]
    print(f"  twin exact: {m == tw}  (snap bytes {len(snap)})", flush=True)
