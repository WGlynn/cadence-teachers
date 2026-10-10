"""EXP-35b pilot (iter28): print every link of knob -> signal -> estimate -> choice -> outcome per arm at full run
length, BEFORE any full run. Run gate: the full run is allowed only if per-move Discover return moves with ALPHA."""
import os, sys, json, numpy as np
from multiprocessing import get_context
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location("e", os.path.join(os.path.dirname(os.path.abspath(__file__)), "EXP-35b_pedigree_controller.py"))
e = importlib.util.module_from_spec(spec); spec.loader.exec_module(e)

def job(x):
    return e.run(x)

def main():
    jobs = [(a, s) for a in e.ARMS for s in range(e.SEEDS)]
    out = os.path.join(e.HERE, f"EXP-35b-pilot-{e.CREDIT}-P{e.PRIOR}.jsonl")
    with get_context("spawn").Pool(int(os.environ.get("WORKERS", 6))) as pool:
        res = list(pool.imap_unordered(job, jobs))
    with open(out, "w") as f:
        for r in res: f.write(json.dumps(r) + "\n")
    print(f"PILOT credit={e.CREDIT} PRIOR={e.PRIOR} rounds={e.ROUNDS} seeds={e.SEEDS}")
    for a in e.ARMS:
        rs = [r for r in res if r["arm"] == a]
        f = lambda k: np.array([np.sum(r[k]) for r in rs], float)
        dD = f("found_pay") / np.maximum(f("nD"), 1)
        dT = (f("direct") + f("royalty") - f("found_pay")) / np.maximum(f("nT"), 1)
        sem = lambda x: x.std(ddof=1) / len(x) ** .5 if len(x) > 1 else 0
        print(f"  alpha {a:4s} | per-move pay D {dD.mean():.4f}+-{sem(dD):.4f}  T {dT.mean():.4f}+-{sem(dT):.4f}"
              f" | est D/T {np.mean([r['estD'][-1] for r in rs]):.4f}/{np.mean([r['estT'][-1] for r in rs]):.4f}"
              f" | discovering {np.mean([np.mean(r['disc']) for r in rs]):.2f} (last10 {np.mean([np.mean(r['disc'][-10:]) for r in rs]):.2f})"
              f" | novel {np.mean([np.sum(r['novel']) for r in rs]):.1f}  final {np.mean([r['acc'][-1] for r in rs]):.3f}  mot {np.mean([np.mean(r['acc']) for r in rs]):.3f}")

if __name__ == "__main__":
    main()
