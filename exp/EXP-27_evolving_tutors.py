"""
EXP-27 — does selecting on TEACHING evolve better teachers than selecting on DOING?

Builds on EXP-26 (the `focus` gene = share of drills on the student's current mistakes; it raises
child accuracy, child cannot exceed teacher, doing score is blind to it).
Population P brains, each carries a focus gene. Each generation each member teaches K children
(EXP-26 teach, M steps, using its own greedy answers and its own focus). Child inherits
focus + N(0, MUT) clipped to [0,1]. Member's TEACHING score = mean child accuracy on the true rule.
Selection to the next population (P of P*K children):
  DO    : highest own accuracy (the child's doing)
  TEACH : highest parent teaching score, then own accuracy  (pedigree price)
PREDICTION (written before running): focus rises in both arms (good teaching shows up in children's
doing); faster / knowledge better preserved in TEACH. Equal arms = honest null.
"""
import os, sys, json, time, importlib.util
import numpy as np
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
P = int(os.environ.get("P", 8))
KIDS = int(os.environ.get("KIDS", 3))
GENS = int(os.environ.get("GENS", 8))
MUT = float(os.environ.get("MUT", 0.15))
OUT = os.path.join(HERE, "exp27_brains")


def m26():
    spec = importlib.util.spec_from_file_location("e26", os.path.join(HERE, "EXP-26_tutor_focus.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


RULE = np.random.default_rng(1234).integers(0, 2, size=32)


def founder_job(i):
    e26 = m26()
    b = e26.train_teacher(700 + i, RULE)
    reward = None  # extra training for a higher ceiling
    for t in range(e26.K * 400):
        c = t % e26.K
        a = b.live(e26.onehot(c)) if reward is None else b.live(e26.onehot(c), reward=reward, done=np.array([True]))
        a = int(np.asarray(a).reshape(-1)[0])
        reward = np.array([1.0 if a == RULE[c] else -1.0])
    path = b.save(os.path.join(OUT, f"founder_{i}.npz"))
    return path, float(np.mean(e26.greedy_all(b) == RULE))


def child_job(args):
    parent_path, focus, cseed, tag = args
    e26 = m26()
    from cadence import Brain
    parent = Brain.load(parent_path)
    answers = e26.greedy_all(parent)
    st = e26.make(cseed)
    e26.M = int(os.environ.get("TEACH_M", e26.M))
    e26.teach(st, answers, focus, np.random.default_rng(cseed + 7))
    path = st.save(os.path.join(OUT, f"{tag}.npz"))
    return path, float(np.mean(e26.greedy_all(st) == RULE))


def main():
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    with get_context("spawn").Pool(int(os.environ.get("WORKERS", 6))) as pool:
        founders = pool.map(founder_job, range(P))
        print(f"founder acc {[round(a, 2) for _, a in founders]}  ({time.time()-t0:.0f}s)", flush=True)
        log = {}
        for arm in os.environ.get("ARMS", "DO,TEACH,BOTH").split(","):
            grng = np.random.default_rng(99)
            pop = [dict(path=p, acc=a, focus=float(f), pteach=0.0)
                   for (p, a), f in zip(founders, grng.random(P))]
            hist = []
            for g in range(GENS):
                kid_focus = [float(np.clip(m["focus"] + grng.normal(0, MUT), 0, 1)) for m in pop for _ in range(KIDS)]
                jobs = [(m["path"], m["focus"], 300_000 + 1000 * g + 10 * i + k, f"{arm}_g{g}_p{i}_c{k}")
                        for i, m in enumerate(pop) for k in range(KIDS)]
                res = pool.map(child_job, jobs)
                kids = []
                for i, m in enumerate(pop):
                    mine = res[i * KIDS:(i + 1) * KIDS]
                    m["teach"] = float(np.mean([a for _, a in mine]))
                    for k, (p, a) in enumerate(mine):
                        kids.append(dict(path=p, acc=a, focus=kid_focus[i * KIDS + k], pteach=m["teach"]))
                hist.append(dict(gen=g, focus=float(np.mean([m["focus"] for m in pop])),
                                 acc=float(np.mean([m["acc"] for m in pop])),
                                 teach=float(np.mean([m["teach"] for m in pop]))))
                noise = grng.random(len(kids))
                if arm == "DO":
                    order = sorted(range(len(kids)), key=lambda j: (kids[j]["acc"], noise[j]), reverse=True)
                elif arm == "TEACH":
                    order = sorted(range(len(kids)), key=lambda j: (kids[j]["pteach"], kids[j]["acc"], noise[j]), reverse=True)
                else:  # BOTH: racehorse rule = own doing + parent's teaching (pedigree), equal weight
                    order = sorted(range(len(kids)), key=lambda j: (kids[j]["acc"] + kids[j]["pteach"], noise[j]), reverse=True)
                pop = [kids[j] for j in order[:P]]
                print(f"{arm} gen {g}: focus {hist[-1]['focus']:.2f}  pop acc {hist[-1]['acc']:.3f}  "
                      f"teaching {hist[-1]['teach']:.3f}  ({time.time()-t0:.0f}s)", flush=True)
            hist.append(dict(gen=GENS, focus=float(np.mean([m["focus"] for m in pop])),
                             acc=float(np.mean([m["acc"] for m in pop])), teach=None))
            print(f"{arm} final: focus {hist[-1]['focus']:.2f}  pop acc {hist[-1]['acc']:.3f}", flush=True)
            log[arm] = hist
            json.dump(dict(P=P, KIDS=KIDS, GENS=GENS, MUT=MUT, founders=[a for _, a in founders], log=log),
                      open(os.path.join(HERE, "EXP-27.json"), "w"))


if __name__ == "__main__":
    main()
