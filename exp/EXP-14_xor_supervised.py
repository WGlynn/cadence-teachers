"""
EXP-14 — can the equilibrium substrate learn XOR via SUPERVISED admission (bootstrap/observe), where
RL-reward collapsed to a constant action (EXP-12f)? This separates "substrate CANNOT represent XOR"
from "RL-reward cannot TEACH it" -- the honest caveat left open in the iter7 verdict.

Supervised: teach input->target directly (bootstrap replays (input, target) pairs until settle-based
readiness passes), then predict + threshold. If XOR passes and predicts correctly -> the substrate
CAN represent XOR; RL reward was the blocker (synergy is buildable, just not via act/feedback). If
bootstrap won't converge / predicts wrong -> XOR is genuinely hard for this substrate, and the
XOR-channel synergy design needs replacing.

Controls: copy-b1 supervised (must pass -> harness sane) and a linear-vs-XOR contrast. Sweep
perception width P and depth (with/without hidden column). Honest scope: tiny net, few seeds; a clean
pass/fail is enough to decide. report["passed"] is cadence's own readiness verdict.
"""
import cadence
from cadence.experimental.equilibrium import Cortex, bootstrap

print("cadence", cadence.__version__, flush=True)
CTX = [(0, 0), (0, 1), (1, 0), (1, 1)]
oh2 = lambda b: [1.0, 0.0] if b == 0 else [0.0, 1.0]
inp = lambda b1, b2: {"c1": oh2(b1), "c2": oh2(b2)}
xor = lambda b1, b2: b1 ^ b2


def build(P, H, seed, depth):
    cx = Cortex(seed=seed, fan_in=9, parameter_prior=0.3, tolerance=1e-3, settle_budget=96)
    s1 = cx.input("c1", shape=2); s2 = cx.input("c2", shape=2)
    perc = cx.column("perception", patches=P, inputs=(s1, s2))
    if depth == 2:
        hid = cx.column("hidden", patches=H, inputs=(perc,))
        resp = cx.column("response", patches=2, inputs=(hid,))
    else:
        resp = cx.column("response", patches=2, inputs=(perc,))
    cx.output("answer", shape=1, reads=resp)
    return cx.build()


def run(fn, P, H, seed, depth, label):
    brain = build(P, H, seed, depth)
    examples = [(inp(b1, b2), {"answer": [float(fn(b1, b2))]}) for b1, b2 in CTX]
    checks = examples  # dev set = the 4 (XOR has no held-out points; this tests representability)
    try:
        rep = bootstrap(brain, examples, checks=checks, max_error=0.3, epochs=60, seed=seed)
    except Exception as e:
        print(f"  {label:22s} P{P} H{H} d{depth} s{seed}: bootstrap RAISED {type(e).__name__}: {str(e)[:60]}", flush=True)
        return
    preds = [brain.predict(inp(b1, b2))["answer"][0] for b1, b2 in CTX]
    hard = [1 if p >= 0.5 else 0 for p in preds]
    acc = sum(int(hard[i] == fn(*CTX[i])) for i in range(4)) / 4
    passed = rep.get("passed")
    print(f"  {label:22s} P{P} H{H} d{depth} s{seed}: passed={passed} acc={acc:.2f} "
          f"preds={['%.2f'%p for p in preds]} target={[fn(*c) for c in CTX]}", flush=True)


print("\n[CONTROL: copy-b1 supervised — must pass if harness is sane]", flush=True)
for sd in (7, 11):
    run(lambda b1, b2: b1, 6, 0, sd, 1, "copy-b1")

print("\n[XOR supervised — shallow, width sweep]", flush=True)
for P in (4, 6, 12):
    for sd in (7, 11):
        run(xor, P, 0, sd, 1, "XOR shallow")

print("\n[XOR supervised — deep (perc->hidden->response)]", flush=True)
for (P, H) in ((6, 6), (12, 12)):
    for sd in (7, 11):
        run(xor, P, H, sd, 2, "XOR deep")
