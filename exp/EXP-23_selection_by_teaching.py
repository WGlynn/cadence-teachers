"""
EXP-23 — rung 3: is TEACHING ability heritable, and does selecting on it beat selecting on doing?

Population of P brains. Each generation every member raises K children by parent-grading (EXP-22
run B, M trips). A parent's TEACHING score = fraction of its children that pass the clean full task.
Next population = P of the P*K children, by one of two rules (same founders, same seeds per arm):
  DO    : child's own pass, ties broken at random
  TEACH : child's own pass, ties broken by the parent's teaching score (pedigree price), then random
Recorded per generation: pop pass rate, mean teaching score of the pop (revealed by ITS children),
and parent-teaching vs child-teaching pairs (heritability of teaching).
"""
import os, sys, json, time, importlib.util
import numpy as np
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
P = int(os.environ.get("P", 6))
K = int(os.environ.get("K", 3))
M = int(os.environ.get("M", 200))
GENS = int(os.environ.get("GENS", 5))
WORKERS = int(os.environ.get("WORKERS", 6))
OUT = os.path.join(HERE, "exp23_brains")


def _mod():
    spec = importlib.util.spec_from_file_location("e22", os.path.join(HERE, "EXP-22_generation_chains.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def founder_job(i):
    e22 = _mod(); e19, e20 = e22.e19, e22.e20
    f = e19.make_brain(e19.POINT, 80_000 + i, None, True)
    rng = np.random.default_rng(5000 + i)
    if i % 2 == 0:
        e20.teach(f, e19.interleave("A" * 300, "B" * 300), rng)
    else:
        e22.train_end_to_end(f, 600, rng)
    path = f.save(os.path.join(OUT, f"founder_{i}.npz"))
    return path, e19.test_fed(path, 80_000 + i)


def child_job(args):
    parent_path, cseed, tag = args
    e22 = _mod(); e19 = e22.e19
    c = e19.make_brain(e19.POINT, cseed, None, True)
    e22.teach_by_grading(c, parent_path, M, np.random.default_rng(cseed + 1))
    path = c.save(os.path.join(OUT, f"{tag}.npz"))
    return path, e19.test_fed(path, cseed)


def main():
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    ctx = get_context("spawn")
    with ctx.Pool(WORKERS) as pool:
        cands = pool.map(founder_job, range(2 * P))
        print(f"founder candidates do: {[round(d, 2) for _, d in cands]}  ({time.time()-t0:.0f}s)", flush=True)
        founders = [c for c in cands if c[1] >= .9][:P]   # founding population = doers
        assert len(founders) == P, f"only {len(founders)} passing founders"
        log = {}
        for arm in ("DO", "TEACH"):
            rng = np.random.default_rng(42)
            pop = [dict(path=p, do=d, pteach=None) for p, d in founders]
            hist, pairs = [], []
            for g in range(GENS):
                jobs = [(m["path"], 100_000 * (g + 1) + 10 * i + k, f"{arm}_g{g+1}_p{i}_c{k}")
                        for i, m in enumerate(pop) for k in range(K)]
                res = pool.map(child_job, jobs)
                kids = []
                for i, m in enumerate(pop):
                    mine = res[i * K:(i + 1) * K]
                    teach = float(np.mean([d >= .9 for _, d in mine]))
                    m["teach"] = teach
                    if m["pteach"] is not None:
                        pairs.append((m["pteach"], teach))
                    kids += [dict(path=p, do=d, pteach=teach) for p, d in mine]
                hist.append(dict(gen=g, pop_pass=float(np.mean([m["do"] >= .9 for m in pop])),
                                 pop_teach=float(np.mean([m["teach"] for m in pop]))))
                noise = rng.random(len(kids))
                if arm == "DO":
                    key = lambda j: (kids[j]["do"] >= .9, noise[j])
                else:
                    key = lambda j: (kids[j]["do"] >= .9, kids[j]["pteach"], noise[j])
                pop = [kids[j] for j in sorted(range(len(kids)), key=key, reverse=True)[:P]]
                print(f"{arm} gen {g}: pop pass {hist[-1]['pop_pass']:.2f}  pop teaching {hist[-1]['pop_teach']:.2f}"
                      f"  -> next pop pass {np.mean([m['do'] >= .9 for m in pop]):.2f}  ({time.time()-t0:.0f}s)",
                      flush=True)
            log[arm] = dict(hist=hist, pairs=pairs)
            json.dump(dict(P=P, K=K, M=M, GENS=GENS, log=log), open(os.path.join(HERE, "EXP-23.json"), "w"))
    for arm in log:
        pr = np.array(log[arm]["pairs"]) if log[arm]["pairs"] else np.zeros((0, 2))
        r = np.corrcoef(pr.T)[0, 1] if len(pr) > 2 and pr.std(0).min() > 0 else float("nan")
        print(f"{arm}: teaching by gen {[round(h['pop_teach'], 2) for h in log[arm]['hist']]}  "
              f"parent->child teaching corr {r:.2f} (n={len(pr)})")


if __name__ == "__main__":
    main()
