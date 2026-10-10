"""
EXP-14b — deep XOR supervised with ADEQUATE settling. EXP-14: shallow XOR supervised genuinely fails
(linear-inseparable, passed=False, near-constant preds) -- a real representational wall, not an RL
artifact. Deep XOR supervised CRASHED with SettlementError at predict (stationarity 0.00246 vs tol
0.001 at 96 sweeps) -- CLOSE to converged, just settling-limited. That is exactly the Dongyang regime.

Give the deep stack the sweeps it was short of (same tolerance 1e-3, just more budget; predict budget
raised too). Honest: more sweeps = what Dongyang's method makes CHEAP, so this directly tests his
relevance.
  - deep supervised XOR now PASSES / predicts [0,1,1,0]  => substrate CAN represent XOR at depth, it
    was settling-limited => Dongyang's cheap-deep-settling IS our lever; synergy buildable on deep
    supervised. Both threads converge YES.
  - still fails after ample settling         => XOR genuinely hard on this substrate; synergy needs a
    different irreducible task, and Dongyang is still not the lever.
Scope: tiny net, 2-3 seeds, 4-point representability (no held-out; this asks CAN it fit XOR at all).
"""
import cadence
from cadence.experimental.equilibrium import Cortex, bootstrap

print("cadence", cadence.__version__, flush=True)
CTX = [(0, 0), (0, 1), (1, 0), (1, 1)]
oh2 = lambda b: [1.0, 0.0] if b == 0 else [0.0, 1.0]
inp = lambda b1, b2: {"c1": oh2(b1), "c2": oh2(b2)}
xor = lambda b1, b2: b1 ^ b2


def build(P, H, seed, settle_budget):
    cx = Cortex(seed=seed, fan_in=9, parameter_prior=0.3, tolerance=1e-3, settle_budget=settle_budget)
    s1 = cx.input("c1", shape=2); s2 = cx.input("c2", shape=2)
    perc = cx.column("perception", patches=P, inputs=(s1, s2))
    hid = cx.column("hidden", patches=H, inputs=(perc,))
    resp = cx.column("response", patches=2, inputs=(hid,))
    cx.output("answer", shape=1, reads=resp)
    return cx.build()


def run(P, H, seed, settle_budget):
    brain = build(P, H, seed, settle_budget)
    examples = [(inp(b1, b2), {"answer": [float(xor(b1, b2))]}) for b1, b2 in CTX]
    try:
        rep = bootstrap(brain, examples, checks=examples, max_error=0.3, epochs=80, seed=seed)
    except Exception as e:
        print(f"  deep P{P}-H{H} sb{settle_budget} s{seed}: bootstrap {type(e).__name__}: {str(e)[:70]}", flush=True)
        return
    try:
        preds = [brain.predict(inp(b1, b2), budget=settle_budget * 3)["answer"][0] for b1, b2 in CTX]
    except Exception as e:
        print(f"  deep P{P}-H{H} sb{settle_budget} s{seed}: passed={rep.get('passed')} predict {type(e).__name__}: {str(e)[:60]}", flush=True)
        return
    hard = [1 if p >= 0.5 else 0 for p in preds]
    acc = sum(int(hard[i] == xor(*CTX[i])) for i in range(4)) / 4
    print(f"  deep P{P}-H{H} sb{settle_budget} s{seed}: passed={rep.get('passed')} acc={acc:.2f} "
          f"preds={['%.2f'%p for p in preds]} target={[xor(*c) for c in CTX]}", flush=True)


print("XOR targets", [xor(*c) for c in CTX], flush=True)
print("\n[deep XOR supervised, ample settling]", flush=True)
for (P, H) in ((6, 6), (12, 12)):
    for sb in (256, 512):
        for sd in (7, 11):
            run(P, H, sd, sb)
