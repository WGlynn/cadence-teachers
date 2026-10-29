"""EXP-05b: is a mid-stream snapshot of a learning brain a byte-identical continuation? (EXP-05 redone)

EXP-05 (experiments/EXP-05.md) was VOID by its own check k4: after youth its brains answered with one
fixed action, so "identical" was too cheap to count. EXP-05b keeps the three arms and changes three
things (experiments/EXP-05b.md): the task is chosen by a behaviour pilot (MODE=pilot, reference lives
only, pilot seeds) so the policy keeps moving after every cut; `last_arousal` is compared only at
`live` events (a load clears it by documentation); fresh seeds. A third brain (two regions with the
apical compartment, 0.90+) is added. One stream, one composed brain with arousal learning a
4-cue / 3-action map through `live`,
with delayed outcomes (`wait`), a reversal at moment 200 and three episode resets. Every life is
run in fresh `python` processes with fixed, different PYTHONHASHSEEDs:

  R, R2  the uninterrupted reference, twice (determinism control)
  P1     the same life, saving a checkpoint + environment state at every cut and living on (A0)
  P2     per cut: load the cut in a fresh process and continue to the end      (arms A and B)
  F      per cut: live to the cut, fork deepcopy D / save-load S / diverging X (arm C)

Compared exactly: every event's record (action, decision_id, pending_feedback, last_arousal,
last_settlement; floats as float.hex) and the SHA-256 of the final checkpoint's bytes.

    MODE=pilot TASKS=T0,T1 python exp/EXP-05b_snapshot_restore.py  # behaviour pilot, pilot seeds, no comparison
    MODE=check TASK=Tn python exp/EXP-05b_snapshot_restore.py   # life 99, harness gates k1..k5
    MODE=full  TASK=Tn python exp/EXP-05b_snapshot_restore.py   # lives 0, 1, 2 (+ the check life's results)
    MODE=diagnose python exp/EXP-05b_snapshot_restore.py  # reads stored traces, prints differing fields
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import threading
import time
from collections.abc import Mapping
from concurrent.futures import ThreadPoolExecutor

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_k, "1")     # registered: one BLAS thread in every process (asserted in main)
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "EXP-05b_brains")          # git-ignored (/exp/*_brains/)
CADENCE = os.path.expanduser("~/_cadence_study")

# ============ Pinned design (experiments/EXP-05b.md) ============
SEED_BRAIN, SEED_ENV = 9_055_000, 9_055_200
PILOT_BRAIN, PILOT_ENV = 9_056_000, 9_056_200     # pilot lives only (MODE=pilot), never data
PILOT_LIVES = (0, 1, 2, 3)
DATA_LIVES, CHECK_LIFE = (0, 1, 2), 99
INPUTS, ACTIONS, WAIT_FRAME, END_FRAME = 6, 3, 4, 5
MOMENTS, REVERSAL, MARK = 300, 200, 0.5
WAIT_P = (0.7, 0.2, 0.1)
RESETS = {100: ("slots",), 175: None, 250: ("slots",)}   # None = the default reset()
BRAINS = {"plain": {"modules": (16,)}, "code": {"modules": (16,), "learned_code": 16},
          "apical": {"modules": (16, 8), "apical": 0.25}}
# Pilot candidates (experiments/EXP-05b.md): the paid / unpaid outcome values and genes added to the founder.
NURSERY = {"consolidation": 0.25, "actor_eta": 0.1, "actor_eta_bias": 0.01}   # docs/start.md live example
TASKS = {
    "T0": {"win": 1.0, "lose": 0.0, "genes": {}},                            # EXP-05's task
    "T1": {"win": 1.0, "lose": -1.0, "genes": {}},
    "T2": {"win": 1.0, "lose": -1.0, "genes": dict(NURSERY)},
    "T3": {"win": 1.0, "lose": -1.0, "genes": {**NURSERY, "arousal_need": 0.5}},
}
TASK = os.environ.get("TASK")              # MODE=check / full require the registered task (asserted in main)
REGISTERED_TASK, REGISTERED_SHA = "T3", "c9c8080"
COVER_SHARE = 0.10                          # coverage: >= 2 actions each >= 10% of the continuation's lives
CUT_TYPES = ("A1", "A2", "A3", "A4", "A5", "A6", "B1", "B2", "B3")
WORKERS = 4
PERTURB = 1e-9


def compose(brain: str, life: int, task: str = None, pilot: bool = False):
    from cadence import Brain
    t = TASKS[task or TASK]
    return Brain.compose(INPUTS, ACTIONS, seed=(PILOT_BRAIN if pilot else SEED_BRAIN) + life, lateral=0.0,
                         arousal=True, memory_choice=True, recall=True, **BRAINS[brain], **t["genes"])


def schedule(life: int, pilot: bool = False):
    """The environment, fixed by its seed: a cue per moment and the waits after each `live`."""
    rng = np.random.default_rng((PILOT_ENV if pilot else SEED_ENV) + life)
    cues = rng.integers(4, size=MOMENTS)
    waits = rng.choice(3, size=MOMENTS, p=WAIT_P)
    events = []
    for m in range(MOMENTS):
        if m in RESETS:
            events += [("E", m, 0), ("R", m, 0)]
        events.append(("L", m, 0))
        if m < MOMENTS - 1:
            events += [("W", m, j) for j in range(int(waits[m]))]
    return [int(c) for c in cues], events


def paying(cue: int, m: int) -> int:
    return cue % 3 if m < REVERSAL else (cue + 1) % 3


def frame(i: int) -> np.ndarray:
    x = np.zeros((1, INPUTS))
    x[0, i] = 1.0
    return x


def canon(v):
    """Exact, JSON-safe: floats as float.hex, arrays element by element."""
    if isinstance(v, (bool, np.bool_)):
        return bool(v)
    if isinstance(v, (int, np.integer)):
        return int(v)
    if isinstance(v, (float, np.floating)):
        return float(v).hex()
    if isinstance(v, np.ndarray):
        return [canon(x) for x in v.tolist()] if v.ndim else canon(v.item())
    if isinstance(v, (list, tuple)):
        return [canon(x) for x in v]
    if isinstance(v, Mapping):
        return {str(k): canon(v[k]) for k in sorted(v, key=str)}
    if v is None or isinstance(v, str):
        return v
    return repr(v)


def event(brain, ev, cues, env, shift=0, task=None):
    """Run one event on one brain; `env` holds the pending action, its moment and its id.
    `last_arousal` is recorded at `live` events only (E and L): docs/api.md says it is None after
    construction, reset or load, and `wait` does not set it (EXP-05's diagnosis)."""
    t = TASKS[task or TASK]
    kind, m, j = ev
    action = None
    if kind == "W":
        brain.wait(frame(WAIT_FRAME))
    elif kind == "R":
        keep = RESETS[m]
        brain.reset() if keep is None else brain.reset(keep=keep)
        env.update(action=None, moment=None, id=None)
    else:
        kw = {}
        if env["action"] is not None:
            cue = (cues[env["moment"]] + shift) % 4
            paid = env["action"] == paying(cue, env["moment"])
            reward = t["win"] if paid else t["lose"]
            if env.get("perturb"):
                reward += env.pop("perturb")
            kw = {"reward": [reward], "decision_id": env["id"]}
            if not paid:
                kw["salience"] = [MARK]
            if kind == "E":
                kw["done"] = [True]
        obs = frame(END_FRAME) if kind == "E" else frame((cues[m] + shift) % 4)
        action = int(brain.live(obs, **kw)[0])
        if kind == "E":
            env.update(action=None, moment=None, id=None)    # the reset drops it
        else:
            env.update(action=action, moment=m, id=brain.decision_id)
    la, ls = brain.last_arousal, brain.last_settlement
    rec = {"ev": [kind, m, j], "action": action, "id": brain.decision_id,
           "pending": bool(brain.pending_feedback),
           "arousal": "not compared" if kind in ("W", "R") else None if la is None else canon(dict(la)),
           "settle": None if ls is None else canon(dict(ls))}
    return json.dumps(rec, sort_keys=True)


def file_digest(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def member_digest(path: str) -> str:
    h = hashlib.sha256()
    with np.load(path, allow_pickle=False) as z:
        for name in sorted(z.files):
            a = z[name]
            h.update(name.encode() + b"|" + str(a.dtype).encode() + b"|" + str(a.shape).encode() + b"|")
            h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()


def digests(path: str) -> dict:
    return {"bytes": file_digest(path), "members": member_digest(path)}


def groups(path: str) -> dict:
    """Which continuation groups a checkpoint carries (the k1 reading)."""
    with np.load(path, allow_pickle=False) as z:
        files = set(z.files)
        meta = json.loads(str(z["brain"]))
    lived = meta.get("lived")
    return {"pending": any(f.startswith("pending/") for f in files),
            "lived": lived is not None, "sampled": None if lived is None else bool(lived["sampled"]),
            "awaiting": "awaiting" in meta}


def member_diff(a: str, b: str) -> list:
    """Names of members that differ, and for the metadata the top-level keys that differ."""
    out = []
    with np.load(a, allow_pickle=False) as za, np.load(b, allow_pickle=False) as zb:
        for name in sorted(set(za.files) | set(zb.files)):
            if name not in za.files or name not in zb.files:
                out.append(name + " (only in one)")
            elif name in ("brain", "meta"):
                ma, mb = json.loads(str(za[name])), json.loads(str(zb[name]))
                out += [f"{name}.{k}" for k in sorted(set(ma) | set(mb)) if ma.get(k) != mb.get(k)]
            elif za[name].dtype != zb[name].dtype or za[name].shape != zb[name].shape or \
                    za[name].tobytes() != zb[name].tobytes():
                out.append(name)
    return out


# ============ Roles (each runs in its own fresh process) ============

def role_life(a: dict) -> dict:
    """R / R2 (no cuts) or P1 (save at every cut and live on)."""
    t0 = time.time()
    cues, events = schedule(a["life"])
    brain = compose(a["brain"], a["life"])
    env = {"action": None, "moment": None, "id": None}
    trace, cuts, error, final_d, final = [], {}, None, None, None
    try:
        for k, ev in enumerate(events):
            trace.append(event(brain, ev, cues, env))
            if k in a["cuts"]:
                name = a["cuts"][k]
                rc = getattr(brain, "recall", None)   # reading: 0.91.1's content cache at the cut
                cache = None if rc is None else {"contents": len(getattr(rc, "_contents", []) or []),
                                                 "keys_none": getattr(rc, "_content_keys", None) is None}
                path = os.path.join(a["dir"], f"cut-{name}.npz")
                brain.save(path)
                with open(os.path.join(a["dir"], f"cut-{name}.env.json"), "w") as f:
                    json.dump({"event": k, **env}, f)
                cuts[name] = {"event": k, **digests(path), "groups": groups(path), "cache": cache}
        final = os.path.join(a["dir"], f"final-{a['tag']}.npz")
        brain.save(final)
        final_d = digests(final)
    except Exception as exc:  # recorded: R / R2 raising voids the run, P1 raising refutes arm A
        error = f"{type(exc).__name__}: {exc}"
    return {"trace": trace, "final": final_d, "final_path": final, "cuts": cuts, "error": error,
            "seconds": time.time() - t0, "pid": os.getpid(), "hashseed": os.environ.get("PYTHONHASHSEED")}


def role_restore(a: dict) -> dict:
    """P2: load the cut in this fresh process; a separate load is saved at once (round trip)."""
    from cadence import Brain
    t0 = time.time()
    cues, events = schedule(a["life"])
    with open(a["env"]) as f:
        env = json.load(f)
    k0 = env.pop("event")
    if a.get("perturb"):
        env["perturb"] = PERTURB
    out = {"pid": os.getpid(), "hashseed": os.environ.get("PYTHONHASHSEED"), "trace": [], "error": None}
    try:
        roundtrip = Brain.load(a["cut"])
        rt = os.path.join(a["dir"], f"roundtrip-{a['tag']}.npz")
        roundtrip.save(rt)
        out["roundtrip"] = digests(rt)
        out["roundtrip_diff"] = member_diff(a["cut"], rt) if file_digest(rt) != file_digest(a["cut"]) else []
        del roundtrip
        brain = Brain.load(a["cut"])
        out["loaded_id"] = brain.decision_id
        for ev in events[k0 + 1:]:
            out["trace"].append(event(brain, ev, cues, env))
        final = os.path.join(a["dir"], f"final-{a['tag']}.npz")
        brain.save(final)
        out["final"], out["final_path"] = digests(final), final
    except Exception as exc:  # recorded, never hidden: a raise is a failed continuation
        out["error"] = f"{type(exc).__name__}: {exc}"
    out["seconds"] = time.time() - t0
    return out


def role_fork(a: dict) -> dict:
    """F: live from moment 0 to the cut in this process, fork D / S / X, run all four to the end."""
    from cadence import Brain
    t0 = time.time()
    cues, events = schedule(a["life"])
    k0 = a["event"]
    o = compose(a["brain"], a["life"])
    env = {"action": None, "moment": None, "id": None}
    for ev in events[:k0 + 1]:
        event(o, ev, cues, env)
    out = {"pid": os.getpid(), "hashseed": os.environ.get("PYTHONHASHSEED"), "error": None}
    brains, envs, traces, at_fork = {"O": o}, {"O": env}, {}, {}
    try:
        brains["D"] = copy.deepcopy(o)              # forked before any save: D itself is never saved
        brains["X"] = copy.deepcopy(o)              # until the end of the life
        path = os.path.join(a["dir"], f"fork-{a['tag']}-O.npz")
        o.save(path)
        brains["S"] = Brain.load(path)
        for name in ("D", "S", "X"):
            envs[name] = dict(env)
        at_fork["O"] = digests(path)
        for name in ("D", "S"):                     # fork-time bytes from a throwaway copy, so the
            p = os.path.join(a["dir"], f"fork-{a['tag']}-{name}.npz")   # continuing twin is not saved
            copy.deepcopy(brains[name]).save(p)
            at_fork[name] = digests(p)
        traces = {name: [] for name in brains}
        for ev in events[k0 + 1:]:
            for name in ("O", "D", "S", "X"):
                traces[name].append(event(brains[name], ev, cues, envs[name], shift=1 if name == "X" else 0))
        out["final"] = {}
        for name, b in brains.items():
            p = os.path.join(a["dir"], f"forkfinal-{a['tag']}-{name}.npz")
            b.save(p)
            out["final"][name] = digests(p)
            out.setdefault("final_path", {})[name] = p
    except Exception as exc:
        out["error"] = f"{type(exc).__name__}: {exc}"
    out.update(traces=traces, at_fork=at_fork, seconds=time.time() - t0)
    return out


ROLES = {"life": role_life, "restore": role_restore, "fork": role_fork}

# ============ Orchestration ============
_slots = threading.Semaphore(WORKERS)


def run_role(role: str, args: dict, hashseed: int, name: str) -> dict:
    os.makedirs(args["dir"], exist_ok=True)
    arg_path = os.path.join(args["dir"], f"args-{name}.json")
    out_path = os.path.join(args["dir"], f"out-{name}.json")
    with open(arg_path, "w") as f:
        json.dump(args, f)
    env = {**os.environ, "PYTHONHASHSEED": str(hashseed)}
    for attempt in (1, 2):   # registered: a process that dies is rerun once; dying twice voids the run
        with _slots:
            p = subprocess.run([sys.executable, os.path.abspath(__file__), "role", role, arg_path, out_path],
                               env=env, capture_output=True, text=True)
        if p.returncode == 0:
            break
        print(f"[{name}] exited {p.returncode} on attempt {attempt}: {p.stderr[-500:]}", flush=True)
    else:
        raise RuntimeError(f"{name} exited {p.returncode} twice: {p.stderr[-2000:]}")
    with open(out_path) as f:
        out = json.load(f)
    out["attempts"] = attempt
    return out


def find_cuts(events, trace) -> dict:
    """The registered cut rules, applied to the reference trace (event index per cut type)."""
    cuts, mode = {}, None
    for k, (ev, line) in enumerate(zip(events, trace)):
        kind, m, _ = ev
        rec = json.loads(line)
        if kind == "L":
            mode = rec["arousal"]["mode"]
        rules = {
            "A1": kind == "L" and m == 40,
            "A2": kind == "W" and 60 <= m < 100,
            "A3": kind == "L" and 130 <= m < 175 and mode == "routine",
            "A4": kind == "W" and 130 <= m < 175 and mode == "routine",
            "A5": kind == "L" and 200 <= m < 250 and mode == "aroused",
            "A6": kind == "W" and 200 <= m < 250 and mode == "aroused",
            "B1": kind == "R" and m == 100, "B2": kind == "R" and m == 175, "B3": kind == "R" and m == 250,
        }
        for name, hit in rules.items():
            if hit and name not in cuts:
                cuts[name] = k
    return cuts


EXPECTED = {  # k1: the groups each cut type's checkpoint must carry
    "A1": {"pending": True, "lived": True, "sampled": True, "awaiting": False},
    "A2": {"pending": True, "lived": True, "sampled": True, "awaiting": True},
    "A3": {"pending": False, "lived": True, "sampled": False, "awaiting": False},
    "A4": {"pending": False, "lived": True, "sampled": False, "awaiting": True},
    "A5": {"pending": True, "lived": True, "sampled": True, "awaiting": False},
    "A6": {"pending": True, "lived": True, "sampled": True, "awaiting": True},
    **{b: {"pending": False, "lived": False, "sampled": None, "awaiting": False} for b in ("B1", "B2", "B3")},
}


def first_diff(a: list, b: list):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return None if len(a) == len(b) else min(len(a), len(b))


def readings(cues, events, trace) -> dict:
    """Accuracy by phase, modes and waits on the reference (printed so the learning is visible)."""
    acc = {"0-99": [], "100-199": [], "200-299": []}
    modes = {"aroused": 0, "routine": 0}
    for ev, line in zip(events, trace):
        kind, m, _ = ev
        if kind != "L":
            continue
        rec = json.loads(line)
        modes[rec["arousal"]["mode"]] = modes.get(rec["arousal"]["mode"], 0) + 1
        key = "0-99" if m < 100 else "100-199" if m < 200 else "200-299"
        acc[key].append(rec["action"] == paying(cues[m], m))
    return {"accuracy": {k: round(float(np.mean(v)), 3) for k, v in acc.items()}, "modes": modes,
            "waits": sum(1 for e in events if e[0] == "W"), "events": len(events)}


def coverage(name: str, ref: list) -> dict:
    """Registered coverage of one continuation (reference events after the cut), `live` moments only
    (L events; an end frame's action is dropped): at least 2 actions each taken on >= 10% of them, and
    at least one aroused (learning) moment, except after B3, whose continuation is routine by design."""
    recs = [json.loads(t) for t in ref]
    acts = [r["action"] for r in recs if r["ev"][0] == "L"]
    counts = {a: acts.count(a) for a in set(acts)}
    shares = sorted((round(c / len(acts), 3) for c in counts.values()), reverse=True) if acts else []
    aroused = sum(1 for r in recs if r["ev"][0] == "L" and r["arousal"]["mode"] == "aroused")
    ok = sum(1 for x in shares if x >= COVER_SHARE) >= 2 and (aroused >= 1 or name == "B3")
    return {"distinct_actions_after": len(counts), "action_shares_after": shares,
            "aroused_lives_after": aroused, "coverage_ok": ok}


def unit(brain: str, life: int, check: bool) -> dict:
    d = os.path.join(WORK, f"{brain}-{life}")
    cues, events = schedule(life)
    base = {"brain": brain, "life": life, "dir": d}
    with ThreadPoolExecutor(2) as ex:
        fr = ex.submit(run_role, "life", {**base, "cuts": {}, "tag": "R"}, 1, "R")
        fr2 = ex.submit(run_role, "life", {**base, "cuts": {}, "tag": "R2"}, 2, "R2")
        R, R2 = fr.result(), fr2.result()
    if R["error"] or R2["error"]:
        raise RuntimeError(f"reference life raised ({brain} {life}): {R['error'] or R2['error']} -> VOID")
    cuts = find_cuts(events, R["trace"])
    P1 = run_role("life", {**base, "cuts": {str(k): n for n, k in cuts.items()}, "tag": "P1"}, 3, "P1")
    if P1["error"]:   # a save that raises: arm A REFUTED (A0); cuts P1 never reached cannot be restored
        cuts = {n: k for n, k in cuts.items() if n in P1["cuts"]}
    # json keys are strings: role_life reads `k in a["cuts"]` with int k, so pass str and convert there
    jobs = {}
    with ThreadPoolExecutor(2 * len(cuts) + 1) as ex:
        for i, (name, k) in enumerate(sorted(cuts.items())):
            cut = os.path.join(d, f"cut-{name}.npz")
            envf = os.path.join(d, f"cut-{name}.env.json")
            jobs[("P2", name)] = ex.submit(run_role, "restore", {**base, "cut": cut, "env": envf, "tag": f"P2-{name}"},
                                           100 + i, f"P2-{name}")
            jobs[("F", name)] = ex.submit(run_role, "fork", {**base, "event": k, "tag": name}, 200 + i, f"F-{name}")
        if check:
            sens = next((n for n in ("A3", "A1") if n in cuts), None)
            if sens:
                jobs[("SENS", sens)] = ex.submit(
                    run_role, "restore", {**base, "cut": os.path.join(d, f"cut-{sens}.npz"),
                                          "env": os.path.join(d, f"cut-{sens}.env.json"),
                                          "tag": f"SENS-{sens}", "perturb": True}, 150, f"SENS-{sens}")
        res = {key: f.result() for key, f in jobs.items()}

    out = {"brain": brain, "life": life, "check_life": life == CHECK_LIFE, "cuts": cuts,
           "unavailable": [c for c in CUT_TYPES if c not in cuts], "reading": readings(cues, events, R["trace"]),
           "seconds": {"R": R["seconds"], "R2": R2["seconds"], "P1": P1["seconds"]}}
    out["control"] = {"R2_trace_equal": R2["trace"] == R["trace"], "R2_final_equal": R2["final"] == R["final"],
                      "first_diff": first_diff(R["trace"], R2["trace"])}
    out["A0"] = {"trace_equal": P1["trace"] == R["trace"], "final_equal": P1["final"] == R["final"],
                 "first_diff": first_diff(R["trace"], P1["trace"]), "error": P1["error"]}
    if P1["final"] and P1["final"]["bytes"] != R["final"]["bytes"]:
        out["A0"]["members"] = member_diff(R["final_path"], P1["final_path"])
    per_cut = {}
    for name, k in sorted(cuts.items()):
        ref = R["trace"][k + 1:]
        p2, f = res[("P2", name)], res[("F", name)]
        c = {"event": k, "groups": P1["cuts"][name]["groups"], "groups_ok": P1["cuts"][name]["groups"] == EXPECTED[name],
             "state_moves": P1["cuts"][name]["bytes"] != R["final"]["bytes"],
             "cache_at_cut": P1["cuts"][name].get("cache"), **coverage(name, ref)}
        c["restore"] = {"error": p2["error"], "trace_equal": p2["trace"] == ref, "first_diff": first_diff(ref, p2["trace"]),
                        "final_equal": p2.get("final") == R["final"], "loaded_id_ok": None,
                        "roundtrip_bytes_equal": p2.get("roundtrip", {}).get("bytes") == P1["cuts"][name]["bytes"],
                        "roundtrip_members_equal": p2.get("roundtrip", {}).get("members") == P1["cuts"][name]["members"],
                        "roundtrip_diff": p2.get("roundtrip_diff"), "seconds": p2["seconds"], "pid": p2["pid"]}
        with open(os.path.join(d, f"cut-{name}.env.json")) as fh:
            c["restore"]["loaded_id_ok"] = p2.get("loaded_id") == json.load(fh)["id"]
        if p2.get("final") and p2["final"]["bytes"] != R["final"]["bytes"]:
            c["restore"]["members"] = member_diff(R["final_path"], p2["final_path"])
        fk = {"error": f["error"], "seconds": f["seconds"]}
        for nm in ("O", "D", "S"):
            fk[nm] = {"trace_equal": f["traces"].get(nm) == ref, "first_diff": first_diff(ref, f["traces"].get(nm, [])),
                      "final_equal": f.get("final", {}).get(nm) == R["final"]}
            if f.get("final", {}).get(nm) and f["final"][nm]["bytes"] != R["final"]["bytes"]:
                fk[nm]["members"] = member_diff(R["final_path"], f["final_path"][nm])
        fk["X_differs"] = f["traces"].get("X") != ref
        fk["fork_bytes_equal"] = len({v["bytes"] for v in f["at_fork"].values()}) == 1 and len(f["at_fork"]) == 3
        fk["fork_equals_P1_cut"] = f["at_fork"].get("O", {}).get("bytes") == P1["cuts"][name]["bytes"]
        c["fork"] = fk
        per_cut[name] = c
    out["per_cut"] = per_cut
    if ("SENS", next((n for n in ("A3", "A1") if n in cuts), "")) in res:
        sname = next(n for n in ("A3", "A1") if n in cuts)
        s = res[("SENS", sname)]
        ref_s, p2_s = R["trace"][cuts[sname] + 1:], res[("P2", sname)]
        trace_flag, final_flag = s["trace"] != ref_s, s.get("final") != R["final"]
        clean = s["error"] is None and p2_s["error"] is None and p2_s["trace"] == ref_s and p2_s.get("final") == R["final"]
        out["sensitivity"] = {"cut": sname, "error": s["error"], "unperturbed_equal": clean,
                              "trace_flag": trace_flag, "final_flag": final_flag,
                              "flagged": clean and trace_flag and final_flag}
    out["seconds"]["P2"] = sum(res[("P2", n)]["seconds"] for n in cuts)
    out["seconds"]["F"] = sum(res[("F", n)]["seconds"] for n in cuts)
    return out


def ulp_probe(path: str) -> bool:
    """k3b: the member digest moves when one float in a copy of a checkpoint moves by one ULP."""
    with np.load(path, allow_pickle=False) as z:
        arrays = {n: z[n].copy() for n in z.files}
    name = next(n for n, v in arrays.items() if v.dtype.kind == "f" and v.size)
    before_tmp = os.path.join(WORK, "ulp-a.npz")
    after_tmp = os.path.join(WORK, "ulp-b.npz")
    np.savez_compressed(before_tmp, **arrays)
    flat = arrays[name].reshape(-1)
    flat[0] = np.nextafter(flat[0], np.inf)
    np.savez_compressed(after_tmp, **arrays)
    return member_digest(before_tmp) == member_digest(path) and member_digest(after_tmp) != member_digest(path)


def describe_genes(brain: str, life: int) -> dict:
    b = compose(brain, life)
    d = b.describe()
    return {"genes": d["genes"], "composition": d["layout"].get("composition")}


def arm_verdicts(units: list) -> dict:
    """Registered rules (experiments/EXP-05b.md). Any failing cut refutes, covered or not; CONFIRMED also
    needs, on every brain, at least one covered instance of every cut type of the arm."""
    brains = sorted({u["brain"] for u in units})
    items = [(u, n, u["per_cut"][n]) for u in units for n in u["per_cut"]]
    ok = lambda c: c["restore"]["error"] is None and c["restore"]["trace_equal"] and c["restore"]["final_equal"]
    fork_ok = lambda c: c["fork"]["error"] is None and all(c["fork"][n]["trace_equal"] and c["fork"][n]["final_equal"]
                                                           for n in ("O", "D", "S")) and c["fork"]["fork_bytes_equal"]
    a0 = all(u["A0"]["trace_equal"] and u["A0"]["final_equal"] and not u["A0"].get("error") for u in units)

    def gap(types):
        return {b: [t for t in types if not any(u["brain"] == b and n == t and c["coverage_ok"] for u, n, c in items)]
                for b in brains}

    def arm(types, test, extra=True, empty_reading=False):
        sel = [c for _, n, c in items if n in types]
        g = gap(types)
        if not extra or not all(test(c) for c in sel):
            return "REFUTED", g
        if any(g.values()) or empty_reading:
            return "INCONCLUSIVE", g
        return "CONFIRMED", g

    arm_a, gap_a = arm(CUT_TYPES[:6], ok, extra=a0)
    arm_b, gap_b = arm(CUT_TYPES[6:], ok)
    x_all = all(c["fork"]["X_differs"] for _, _, c in items)
    arm_c, gap_c = arm(CUT_TYPES, fork_ok, empty_reading=not x_all)
    uncovered = sorted(f"{u['brain']}-{u['life']}-{n}" for u, n, c in items if not c["coverage_ok"])
    return {"arms": {"A": arm_a, "B": arm_b, "C": arm_c}, "A0": a0, "X_differs_everywhere": x_all,
            "coverage_gap": {"A": gap_a, "B": gap_b, "C": gap_c}, "uncovered_cuts": uncovered}


def verdicts(units: list) -> dict:
    pooled = arm_verdicts(units)
    arms = pooled["arms"]
    control = all(u["control"]["R2_trace_equal"] and u["control"]["R2_final_equal"] for u in units if not u["check_life"])
    if not control:
        overall, loop = "VOID", "VOID"
    elif "REFUTED" in arms.values():
        overall = "BOUNDARY" if "CONFIRMED" in arms.values() else "NULL"
        loop = "REFUTED"
    else:
        overall = "SUPPORTIVE"
        loop = "CONFIRMED" if all(v == "CONFIRMED" for v in arms.values()) else "INCONCLUSIVE"
    per_brain = {b: arm_verdicts([u for u in units if u["brain"] == b])["arms"] for b in sorted({u["brain"] for u in units})}
    return {**pooled, "per_brain": per_brain, "control": control, "overall": overall, "loop": loop}


def env_info() -> dict:
    import cadence
    sha = subprocess.run(["git", "-C", CADENCE, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    desc = subprocess.run(["git", "-C", CADENCE, "describe", "--tags"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", CADENCE, "status", "--porcelain", "--untracked-files=no"],
                           capture_output=True, text=True).stdout.strip()
    return {"cadence": cadence.__version__, "sha": sha, "describe": desc, "dirty": bool(dirty),
            "file": cadence.__file__, "python": sys.version.split()[0], "numpy": np.__version__,
            "threads": {k: os.environ.get(k) for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")},
            "installed": {m: importlib.util.find_spec(m) is not None for m in ("numba", "torch")}}


def summarize(u: dict) -> str:
    lines = [f"[{u['brain']} life {u['life']}{' (check)' if u['check_life'] else ''}] reading {json.dumps(u['reading'])}",
             f"  control R==R2: trace {u['control']['R2_trace_equal']} final {u['control']['R2_final_equal']}"
             f" | A0 P1==R: trace {u['A0']['trace_equal']} final {u['A0']['final_equal']}"
             f" | unavailable {u['unavailable']} | seconds {json.dumps({k: round(v, 1) for k, v in u['seconds'].items()})}"]
    for name, c in u["per_cut"].items():
        r, f = c["restore"], c["fork"]
        lines.append(
            f"  {name} ev {c['event']:>3} groups_ok {c['groups_ok']} moves {c['state_moves']} acts {c['distinct_actions_after']}"
            f" shares {c['action_shares_after']} aroused-after {c['aroused_lives_after']} covered {c['coverage_ok']}"
            f" cache {c['cache_at_cut']}"
            f" | restore trace {r['trace_equal']} final {r['final_equal']} id {r['loaded_id_ok']} err {r['error']}"
            f" rt-bytes {r['roundtrip_bytes_equal']} rt-members {r['roundtrip_members_equal']}"
            f" | fork O {f['O']['trace_equal'] and f['O']['final_equal']} D {f['D']['trace_equal'] and f['D']['final_equal']}"
            f" S {f['S']['trace_equal'] and f['S']['final_equal']} X-differs {f['X_differs']} at-fork-equal {f['fork_bytes_equal']}"
            f" =P1 {f['fork_equals_P1_cut']} err {f['error']}")
        for tag, info in (("restore", r), *[(f"fork {n}", f[n]) for n in "ODS"]):
            if info.get("first_diff") is not None or info.get("members"):
                lines.append(f"    {tag}: first differing event after the cut {info.get('first_diff')}, members {info.get('members')}")
        if r.get("roundtrip_diff"):
            lines.append(f"    round trip differs in: {r['roundtrip_diff']}")
    if "sensitivity" in u:
        sv = u["sensitivity"]
        lines.append(f"  k3 sensitivity at {sv['cut']}: flagged {sv['flagged']} (unperturbed restore equal {sv['unperturbed_equal']},"
                     f" trace flag {sv['trace_flag']}, final-bytes flag {sv['final_flag']}) err {sv['error']}")
    return "\n".join(lines)


def diagnose():
    """MODE=diagnose (added after the check, reads its stored outputs, runs nothing): for every
    continuation whose trace differs from the reference, the differing events and fields."""
    for unit_dir in sorted(os.listdir(WORK)):
        d = os.path.join(WORK, unit_dir)
        if not os.path.isdir(d) or not os.path.exists(os.path.join(d, "out-P1.json")):
            continue
        with open(os.path.join(d, "out-R.json")) as f:
            ref_all = json.load(f)["trace"]
        with open(os.path.join(d, "out-P1.json")) as f:
            p1 = json.load(f)
        for name, cut in sorted(p1["cuts"].items()):
            ref = ref_all[cut["event"] + 1:]
            with open(os.path.join(d, f"out-P2-{name}.json")) as f:
                p2 = json.load(f)
            with open(os.path.join(d, f"out-F-{name}.json")) as f:
                fk = json.load(f)
            for who, tr in (("restore", p2["trace"]), *[(f"fork {n}", fk["traces"][n]) for n in "ODS"]):
                bad = [i for i, (x, y) in enumerate(zip(ref, tr)) if x != y] + \
                      ([min(len(ref), len(tr))] if len(ref) != len(tr) else [])
                for i in bad:
                    a, b = json.loads(ref[i]), json.loads(tr[i])
                    fields = {k: {"reference": a[k], "continuation": b[k]} for k in a if a[k] != b.get(k)}
                    print(f"{unit_dir} cut {name} (event {cut['event']}, {json.loads(ref_all[cut['event']])['ev']}) {who}:"
                          f" event +{i} {a['ev']} differs in {sorted(fields)} of {len(ref)} events;"
                          f" {json.dumps(fields, sort_keys=True)}")
                if not bad:
                    print(f"{unit_dir} cut {name} {who}: all {len(ref)} events identical")


def pilot_life(job):
    """MODE=pilot: one reference life on pilot seeds, in this worker process; behaviour only, no save."""
    task, brain, life = job
    t0 = time.time()
    cues, events = schedule(life, pilot=True)
    b = compose(brain, life, task=task, pilot=True)
    env = {"action": None, "moment": None, "id": None}
    trace = [event(b, ev, cues, env, task=task) for ev in events]
    recs = [json.loads(t) for t in trace]
    cuts = find_cuts(events, trace)
    phases = {"0-99": (0, 100), "100-199": (100, 200), "200-249": (200, 250), "250-299": (250, 300)}
    aroused = {k: sum(1 for ev, r in zip(events, recs) if ev[0] == "L" and lo <= ev[1] < hi
                      and r["arousal"]["mode"] == "aroused") for k, (lo, hi) in phases.items()}
    per_cut = {name: {"event": k, "moment": events[k][1], **coverage(name, trace[k + 1:])}
               for name, k in sorted(cuts.items())}
    return {"task": task, "brain": brain, "life": life, "reading": readings(cues, events, trace),
            "aroused_by_phase": aroused, "unavailable": [c for c in CUT_TYPES if c not in cuts],
            "per_cut": per_cut, "seconds": round(time.time() - t0, 1)}


def pilot():
    from concurrent.futures import ProcessPoolExecutor
    tasks = os.environ.get("TASKS", ",".join(TASKS)).split(",")
    jobs = [(t, b, life) for t in tasks for b in BRAINS for life in PILOT_LIVES]
    with ProcessPoolExecutor(WORKERS) as ex:
        rows = list(ex.map(pilot_life, jobs))
    for r in rows:
        weakest = min(((c["action_shares_after"][1] if len(c["action_shares_after"]) > 1 else 0.0,
                        c["aroused_lives_after"], n) for n, c in r["per_cut"].items()), default=None)
        print(f"{r['task']} {r['brain']:>6} life {r['life']} acc {r['reading']['accuracy']} aroused {r['aroused_by_phase']}"
              f" unavailable {r['unavailable']} weakest-cut (2nd action share, aroused-after, cut) {weakest}"
              f" uncovered {[n for n, c in r['per_cut'].items() if not c['coverage_ok']]} {r['seconds']} s", flush=True)
    for t in tasks:
        sub = [r for r in rows if r["task"] == t]
        full = sum(1 for r in sub if not r["unavailable"])
        moving = sum(1 for r in sub if all(c["distinct_actions_after"] >= 2 for c in r["per_cut"].values()))
        learning = sum(1 for r in sub if all(c["aroused_lives_after"] >= 1 for c in r["per_cut"].values()))
        covered = sum(1 for r in sub if not r["unavailable"] and all(c["coverage_ok"] for c in r["per_cut"].values()))
        print(f"SUMMARY {t}: lives with all 9 cut types {full}/{len(sub)}; every cut followed by >= 2 live actions"
              f" {moving}/{len(sub)}; every cut followed by >= 1 aroused live {learning}/{len(sub)};"
              f" all 9 cut types and every cut covered (registered rule) {covered}/{len(sub)}", flush=True)
    out = os.environ.get("PILOT_OUT", "EXP-05b-pilot")
    with open(os.path.join(HERE, out + ".json"), "w") as f:
        json.dump({"env": env_info(), "rows": rows}, f, indent=1, sort_keys=True)


def main():
    mode = os.environ.get("MODE", "check")
    if mode == "diagnose":
        return diagnose()
    if mode == "pilot":
        info = env_info()
        print(f"EXP-05b MODE=pilot | Cadence {info['cadence']} {info['describe']} ({info['sha']}) dirty={info['dirty']}"
              f" | Python {info['python']} NumPy {info['numpy']} | threads {info['threads']} | {info['installed']}", flush=True)
        return pilot()
    os.makedirs(WORK, exist_ok=True)
    info = env_info()
    print(f"EXP-05b MODE={mode} TASK={TASK} {json.dumps(TASKS.get(TASK), sort_keys=True)} | Cadence {info['cadence']}"
          f" {info['describe']} ({info['sha']}) dirty={info['dirty']} | Python {info['python']} NumPy {info['numpy']}"
          f" | threads {info['threads']} | {info['installed']}", flush=True)
    assert TASK == REGISTERED_TASK, f"TASK must be the registered {REGISTERED_TASK}, got {TASK!r}"
    assert info["sha"].startswith(REGISTERED_SHA) and not info["dirty"], "Cadence clone is not the registered clean c9c8080"
    assert all(v == "1" for v in info["threads"].values()), f"thread variables must be 1: {info['threads']}"
    t0 = time.time()
    if mode == "check":
        for b in BRAINS:
            print(f"genes[{b}] {json.dumps(describe_genes(b, CHECK_LIFE), sort_keys=True)}", flush=True)
        lives = [CHECK_LIFE]
    else:
        lives = list(DATA_LIVES)
    jobs = [(b, life) for life in lives for b in BRAINS]
    with ThreadPoolExecutor(len(jobs)) as ex:
        units = list(ex.map(lambda j: unit(j[0], j[1], mode == "check"), jobs))
    wall = time.time() - t0
    for u in units:
        print(summarize(u), flush=True)
    result = {"mode": mode, "env": info, "task": TASK, "task_spec": TASKS[TASK], "wall_seconds": wall, "units": units}
    if mode == "check":
        k1 = all(len(u["cuts"]) == len(CUT_TYPES) and all(c["groups_ok"] for c in u["per_cut"].values()) for u in units)
        k2 = all(u["control"]["R2_trace_equal"] and u["control"]["R2_final_equal"] for u in units)
        k3 = all(u.get("sensitivity", {}).get("flagged") for u in units) and \
            ulp_probe(os.path.join(WORK, f"plain-{CHECK_LIFE}", "cut-B1.npz"))
        k4 = all(c["state_moves"] and c["coverage_ok"] for u in units for c in u["per_cut"].values())
        # one check life = 3 units; the full run is 3 lives at the same per-unit work, 4 workers either way
        projected = wall * len(DATA_LIVES)
        k5 = projected <= 15 * 60
        result["gates"] = {"k1": k1, "k2": k2, "k3": k3, "k4": k4, "k5": k5, "projected_full_seconds": projected}
        result["verdicts_on_check_life"] = verdicts(units)
        print(f"GATES k1 {k1} k2 {k2} k3 {k3} k4 {k4} k5 {k5} (projected full {projected:.0f} s) -> "
              f"{'PASS' if all((k1, k2, k3, k4, k5)) else 'FAIL'} | wall {wall:.0f} s", flush=True)
        print(f"seen in the check (counts in the verdict, flagged): {json.dumps(result['verdicts_on_check_life'])}")
        out = os.path.join(HERE, "EXP-05b-check.json")
    else:
        check_path = os.path.join(HERE, "EXP-05b-check.json")
        with open(check_path) as f:
            check = json.load(f)
        assert check["gates"] and all(v for k, v in check["gates"].items() if k.startswith("k")), "check did not pass"
        assert check["task"] == TASK and check["env"]["sha"] == info["sha"], "check ran another task or Cadence commit"
        result["verdicts"] = verdicts(units + check["units"])
        print(f"VERDICTS (data lives + check life): {json.dumps(result['verdicts'])} | wall {wall:.0f} s")
        out = os.path.join(HERE, "EXP-05b-full.json")
    for u in result["units"]:
        u.pop("traces", None)
    with open(out, "w") as f:
        json.dump(result, f, indent=1, sort_keys=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "role":
        role, arg_path, out_path = sys.argv[2], sys.argv[3], sys.argv[4]
        with open(arg_path) as f:
            args = json.load(f)
        if role == "life":
            args["cuts"] = {int(k): v for k, v in args["cuts"].items()}
        result = ROLES[role](args)
        with open(out_path, "w") as f:
            json.dump(result, f)
    else:
        main()
