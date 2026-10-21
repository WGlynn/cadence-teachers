"""EXP-69b: EXP-69 (salience mark vs cost on the reward-only hidden chain) replicated at lateral = 0.0.

Upstream #220 recommends resolving an unset motor `lateral` to 0.0 in 0.85 (it is -0.5 at up to 8 neurons today).
EXP-67/68/69 pinned -0.5, so their numbers describe today's default, not 0.85's. This run repeats EXP-69's four arms
on fresh seeds 69_500+ with `lateral=0.0` set explicitly. Same harness: EXP-69's life, imported unchanged.
Registered to run on the 0.85 release (record the SHA at run time). The check refuses to run if the code paths EXP-69's
pre-registration read (step -> learn -> _received / _record_outcome / _remember, _extend_paths, _replay, memory.py)
differ from `be372b8` beyond docstrings: then the reading has to be redone and re-registered.

    MODE=check WORKERS=4 python -u EXP-69b_salience_mark_lateral0.py
    WORKERS=4 python -u EXP-69b_salience_mark_lateral0.py
"""
import ast, importlib.util, json, os, subprocess, time
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("e69", os.path.join(HERE, "EXP-69_salience_mark.py"))
E69 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E69)

# ============ Overrides (module top level, so spawned workers apply them too) ============
E69.LATERAL[0] = 0.0
E69.SEED_BASE, E69.CHECK_SEED = 69_500, 69_995
MODE = os.environ.get("MODE", "run")
WORKERS = int(os.environ.get("WORKERS", 4))
ARMS, N = E69.ARMS, E69.N            # unchanged: ctx5 96, pen@.005 48, sal@.005 96, sal@1 48
REF_SHA = "be372b8"                  # where EXP-69's code reading was done
STUDY = os.path.expanduser("~/_cadence_study")
GATED = ("step", "learn", "_received", "_extend_paths", "_record_outcome", "_remember", "_replay")


# ============ Code gate: the salience / replay path must be the one EXP-69 read ============
def _strip(tree):
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(body, list) and body and isinstance(body[0], ast.Expr) \
                and isinstance(getattr(body[0], "value", None), ast.Constant) and isinstance(body[0].value.value, str):
            node.body = body[1:] or [ast.Pass()]
    return tree


def _fns(src):
    out = {}
    for node in ast.walk(_strip(ast.parse(src))):
        if isinstance(node, ast.FunctionDef) and node.name in GATED:
            out.setdefault(node.name, []).append(ast.dump(node, include_attributes=False))
    return out


def code_gate(pkg_dir):
    ref = lambda p: subprocess.run(["git", "-C", STUDY, "show", f"{REF_SHA}:src/cadence/{p}"], capture_output=True,
                                   text=True, encoding="utf-8", check=True).stdout
    now = lambda p: open(os.path.join(pkg_dir, p), encoding="utf-8").read()
    a, b = _fns(ref("generic.py")), _fns(now("generic.py"))
    changed = [f for f in GATED if a.get(f) != b.get(f)]
    mem_same = ast.dump(_strip(ast.parse(ref("memory.py")))) == ast.dump(_strip(ast.parse(now("memory.py"))))
    return changed, mem_same


# ============ Workers (defined here so spawn can pickle them) ============
def run(job):
    return E69.run(job)


def _check_job(job):
    tag, arm, size = job
    E69.LATERAL[0] = None if tag == "unset" else 0.0
    t0 = time.time()
    stats, rd, diag = E69.life(arm, E69.CHECK_SEED, size)
    return job, {**stats, **rd, "diag": diag, "secs": time.time() - t0}


# ============ Check ============
def check():
    import cadence as cd
    pkg = os.path.dirname(cd.__file__)
    print(f"EXP-69b check: cadence {cd.__version__} from {pkg}", flush=True)
    changed, mem_same = code_gate(pkg)
    ok = not changed and mem_same
    print(f"  (gate) salience/replay path AST-identical to {REF_SHA} (docstrings stripped): {ok} "
          f"(changed functions {changed or 'none'}, memory.py identical {mem_same})", flush=True)
    if not ok:
        print("  CHECK FAILED: redo the code reading and re-register before any data.", flush=True)
        return
    d = E69.compose("ctx5", E69.CHECK_SEED).describe()["initialization"]["composition"]
    print(f"  pinned brain: lateral {d.get('lateral')}, working_memory_scale {d.get('working_memory_scale')}", flush=True)
    jobs = [("unset", "ctx5", 0.0), ("ours", "ctx5", 0.0), ("ours", "sal", 0.0), ("ours", "sal", 0.005),
            ("ours", "sal", 1.0), ("ours", "pen", 0.005), ("unset", "pen", 0.005)]
    with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
        got = dict(pool.map(_check_job, jobs))
    F = E69.E67.E66.READ_FIELDS
    same = lambda a, b: all(got[a][f] == got[b][f] for f in F)
    print(f"  (info) ctx5 / pen@.005 with lateral 0.0 explicit identical to lateral unset on this release: "
          f"{same(jobs[1], jobs[0])} / {same(jobs[5], jobs[6])} (True iff the release resolves unset to 0.0 here)",
          flush=True)
    m = got[jobs[2]]["diag"]["marks"]
    s = same(jobs[2], jobs[1]) and m["marked"] == m["misses"] > 0 and m["written"] == 0
    print(f"  (b) sal@0 identical to ctx5, nothing written: {s} ({m})", flush=True)
    ok &= s
    for j in (jobs[3], jobs[4]):
        m, r, saw = got[j]["diag"]["marks"], got[j]["diag"]["reach"], got[j]["diag"]["memory_saw"]
        s = (m["marked"] == m["misses"] == m["written"] > 0 and saw["path"] == 0 and saw["outcome"] == 0
             and r["successes"] > 0 and r["stopped"] == 0)
        print(f"  (c) sal@{j[2]:g}: every miss marked and written, no nonzero miss reward reached the memory, replay never "
              f"stopped at a miss: {s} (marks {m}, memory saw {saw}, replay {r})", flush=True)
        ok &= s
    r, saw = got[jobs[5]]["diag"]["reach"], got[jobs[5]]["diag"]["memory_saw"]
    s = saw["path"] > 0 and r["stopped"] > 0
    print(f"  (d) pen@.005: the memory saw the cost and replay stopped at a charged miss: {s} (memory saw {saw}, "
          f"replay {r})", flush=True)
    ok &= s
    per = float(np.mean([v["secs"] for v in got.values()]))
    lives = sum(n for _, _, n in ARMS)
    print(f"  (time) {per:.1f} s per life; full run {lives} lives, about {per * lives / max(1, WORKERS) / 60:.0f} min at "
          f"{WORKERS} workers", flush=True)
    print(f"  CHECK {'PASS' if ok else 'FAILED'}", flush=True)


# ============ Run ============
def main():
    t0 = time.time()
    ckpt = os.path.join(HERE, "EXP-69b-full.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["arm"], r["size"], r["seed"]) for r in rows}
    jobs = [(a, p, i) for i in range(N) for a, p, m in ARMS if i < m and (a, p, i) not in done]
    print(f"EXP-69b: {len(jobs)} lives to go ({len(done)} done); workers {WORKERS}; lateral {E69.LATERAL[0]}; "
          f"seeds {E69.SEED_BASE}+", flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as fh:
                    fh.write(json.dumps(r) + "\n")
    print(f"\nEXP-69b done in {time.time() - t0:.0f}s", flush=True)
    s = E69.summary(rows)
    if not s["p0"]:                    # registered: at lateral 0.0 a missing cost harm is a finding, not a void
        s["verdict"] = "NO COST HARM AT 0.0"
        print(f"  VERDICT (EXP-69b rule): {s['verdict']}", flush=True)
    json.dump(dict(summary=s), open(os.path.join(HERE, "EXP-69b-full.json"), "w"))


if __name__ == "__main__":
    check() if MODE == "check" else main()
