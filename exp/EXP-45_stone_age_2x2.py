"""
EXP-45: why did grading solve the Stone Age chain for us (EXP-39, 12/12) and fail in Stone Age V5 (grade_only 0.2%)?
And is V5's in-sequence success a learned chain or search inside an attempt?

Chamber: a faithful re-implementation (our code; theirs was read, not run) of V5's COLD chamber
(ali12mahmood12345-boop/cadence-stone-age @ 6689fe2, benchmarks/cadence_081/v5_mochi_style.py): actions GATHER_WOOD,
GATHER_STONE, CRAFT_FIRE, WARM_UP, WAIT; strict order wood -> stone -> fire -> warm; a wrong action changes nothing;
10 decisions per attempt; world reward +2 on success, -1 on timeout, 0 otherwise; observation = warmth, has wood,
has stone, has fire, wood/2, stone/2, cue (7 inputs, the target action never observed). One continuing life per arm,
V5's event order (the reward of an action arrives with the next observation; done=True at the end of an attempt).

Factor BRAIN, both on the 0.81 composition (working_memory_scale 12, decay 0.2, so the 0.82 context change is not a
factor here):
  ours : EXP-39's brain, the key-door protocol-3 operating point (modules (32,), actor step .1, bias step .01, lam .95,
         gamma .95, critic rate 5, trace amplitude .3, consolidation .25), no arousal.
  v5   : V5's brain, Brain.compose defaults, modules (48, 24), arousal=True (actor step 1.0, critic .3, lam .8, gamma .9).
Factor SIGNAL:
  natural    : world reward only (V5 natural_only).
  grade-v5   : V5 grade_only: +-.5 for agreeing with the right action, only in guided windows (4 of every 12 decisions
               of the life), added to the world reward.
  grade-dense: EXP-39 GRADE: every move graded +1 / -1, and the grade IS the reward (no world reward).
  corrective : V5 corrective_teacher: on an executed mistake in a guided window, the right action as a teacher label
               for the (unchanged) observation.
Readings on frozen copies after EPISODES training attempts:
  acc        : per-state greedy accuracy over the 4 chain states (reset before each).
  greedy     : full-chain success of the greedy policy (reset per attempt).
  sampled    : full-chain success of the sampled policy, 100 attempts (reset per attempt).  V5's headline reading.
  erased     : sampled, with working_memory.reset(1) before every decision (forgets only the carried interpretation).
  memoryless : success predicted from the per-state sampled p(right) (300 samples each, reset) if attempts had no memory.
Chance in this chamber (exact): uniform random .121; avoid-last-failure .178 (simulated); never-repeat-a-failure .304.
PREDICTION: experiments/EXP-45.md (written before the pilot).

    SEEDS=12 EPISODES=120 WORKERS=2 TAG=full python -u EXP-45_stone_age_2x2.py
"""
import json, os, tempfile, time
from dataclasses import replace
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SEEDS = int(os.environ.get("SEEDS", 12))
EPISODES = int(os.environ.get("EPISODES", 120))
WORKERS = int(os.environ.get("WORKERS", 2))
TAG = os.environ.get("TAG", "full")
EVAL = int(os.environ.get("EVAL", 100))
FP_SAMPLES = 300
MAX_DECISIONS, SUCCESS, FAILURE, GRADE_V5 = 10, 2.0, -1.0, 0.5
GUIDED, AUTONOMOUS = 4, 8
WOOD, STONE, FIRE, WARM, WAIT = range(5)
STATES = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1)]          # (wood, stone, fire) at each chain stage
BRAINS = os.environ.get("BRAINS", "ours,v5").split(",")
SIGNALS = os.environ.get("SIGNALS", "natural,grade-v5,grade-dense,corrective").split(",")
OURS = dict(modules=(32,), eta=0.1, eta_bias=0.01, lam=0.95, gamma=0.95, eta_critic=5.0,
            working_memory_amplitude=0.3, consolidation=0.25)


def obs(w, s, f, warmth=0.35):
    return np.array([[warmth, float(w), float(s), float(f), w / 2.0, s / 2.0, 1.0]])


class Chamber:
    def __init__(self):
        self.w = self.s = self.f = 0
        self.warmth, self.t, self.done, self.success = 0.35, 0, False, False

    def x(self):
        return obs(self.w, self.s, self.f, self.warmth)

    def right(self):
        return WARM if self.f else CRAFT_OR(self)

    def execute(self, a):
        ok = a == self.right()
        if ok:
            if a == WOOD: self.w = 1
            elif a == STONE: self.s = 1
            elif a == FIRE: self.f = 1
            elif a == WARM: self.warmth, self.success, self.done = 0.9, True, True
        self.t += 1
        if not self.done and self.t >= MAX_DECISIONS:
            self.done = True
        r = (SUCCESS if self.success else FAILURE) if self.done else 0.0
        return ok, r


def CRAFT_OR(c):
    return FIRE if (c.w and c.s) else (STONE if c.w else WOOD)


def make_brain(kind, seed):
    import cadence as cd
    wm = dict(working_memory_scale=12.0, working_memory_decay=0.2)        # the 0.81 composition
    if kind == "v5":
        return cd.Brain.compose(7, 5, modules=(48, 24), seed=seed, arousal=True, **wm)
    b = cd.Brain.compose(7, 5, modules=OURS["modules"], seed=seed, consolidation=OURS["consolidation"],
                         working_memory_amplitude=OURS["working_memory_amplitude"], **wm)
    b.basal_ganglia.config = replace(b.basal_ganglia.config, **{k: OURS[k] for k in ("eta", "eta_bias", "lam", "gamma", "eta_critic")})
    return b


def train(brain, signal):
    """One continuing life, V5's event order. Returns training stats."""
    c, g, hits, wins, teach = Chamber(), 0, 0, 0, 0
    a = int(brain.step(c.x())[0])
    for _ in range(EPISODES):
        while True:
            guided = (g % (GUIDED + AUTONOMOUS)) < GUIDED
            right = c.right()
            ok, world = c.execute(a)
            hits += ok
            if signal == "grade-dense":
                r = 1.0 if ok else -1.0
            elif signal == "grade-v5" and guided:
                r = world + (GRADE_V5 if ok else -GRADE_V5)
            else:
                r = world
            teacher = None
            if signal == "corrective" and guided and not ok and not c.done:
                teacher = np.array([right]); teach += 1
            g += 1
            if c.done:
                wins += c.success
                c = Chamber()
                a = int(brain.step(c.x(), reward=np.array([r]), done=np.array([True]))[0])
                break
            a = int(brain.step(c.x(), reward=np.array([r]), done=np.array([False]), teacher=teacher)[0])
    brain.reset()
    return dict(train_success=wins / EPISODES, train_agree=hits / g, teacher_labels=teach, decisions=g)


def attempt(b, greedy, erase):
    b.reset()
    c = Chamber()
    while not c.done:
        if erase:
            b.working_memory.reset(1)
        c.execute(int(b.act(c.x(), greedy=greedy)[0]))
    return c.success


def memoryless(p):
    """P(finish 4 stages within MAX_DECISIONS) if each decision at stage k is right with prob p[k], independently."""
    dist = np.zeros(5); dist[0] = 1.0
    for _ in range(MAX_DECISIONS):
        nxt = np.zeros(5); nxt[4] = dist[4]
        for k in range(4):
            nxt[k + 1] += dist[k] * p[k]; nxt[k] += dist[k] * (1 - p[k])
        dist = nxt
    return float(dist[4])


def run(job):
    brain_kind, signal, seed = job
    import cadence as cd
    t0 = time.time()
    brain = make_brain(brain_kind, seed)
    stats = train(brain, signal)
    with tempfile.TemporaryDirectory() as d:
        path = brain.save(os.path.join(d, "b.npz"))
        b = cd.Brain.load(path)
        greedy_ans, p_right, rights = [], [], [WOOD, STONE, FIRE, WARM]     # the right action at each of STATES
        for (w, s, f), right in zip(STATES, rights):
            b.reset()
            greedy_ans.append(int(b.act(obs(w, s, f), greedy=True)[0]))
            hits = 0
            for _ in range(FP_SAMPLES):
                b.reset()
                hits += int(b.act(obs(w, s, f), greedy=False)[0]) == right
            p_right.append(hits / FP_SAMPLES)
        acc = float(np.mean([ga == r for ga, r in zip(greedy_ans, rights)]))
        greedy = attempt(cd.Brain.load(path), True, False)
        bs = cd.Brain.load(path); sampled = float(np.mean([attempt(bs, False, False) for _ in range(EVAL)]))
        be = cd.Brain.load(path); erased = float(np.mean([attempt(be, False, True) for _ in range(EVAL)]))
    row = dict(brain=brain_kind, signal=signal, seed=seed, episodes=EPISODES, **stats, acc=acc, greedy_answers=greedy_ans,
               p_right=p_right, greedy=bool(greedy), sampled=sampled, erased=erased, memoryless=memoryless(p_right),
               secs=round(time.time() - t0, 1), cadence=cd.__version__)
    print(f"  {brain_kind:4s} {signal:11s} s{seed}: acc {acc:.2f} greedy {int(greedy)} sampled {sampled:.2f} "
          f"erased {erased:.2f} memoryless {row['memoryless']:.2f} p_right {[round(x, 2) for x in p_right]} "
          f"train {stats['train_success']:.2f} ({row['secs']}s)", flush=True)
    return row


def main():
    t0 = time.time()
    ckpt = os.path.join(HERE, f"EXP-45-{TAG}.jsonl")
    rows = [json.loads(l) for l in open(ckpt)] if os.path.exists(ckpt) else []
    done = {(r["brain"], r["signal"], r["seed"]) for r in rows}
    jobs = [(bk, sg, 42 + s) for s in range(SEEDS) for bk in BRAINS for sg in SIGNALS if (bk, sg, 42 + s) not in done]
    print(f"EXP-45: {len(jobs)} runs to go ({len(done)} done); episodes {EPISODES}; brains {BRAINS}; signals {SIGNALS}",
          flush=True)
    if jobs:
        with get_context("spawn").Pool(max(1, min(WORKERS, len(jobs)))) as pool:
            for r in pool.imap_unordered(run, jobs):
                rows.append(r)
                with open(ckpt, "a") as f:
                    f.write(json.dumps(r) + "\n")
    sem = lambda x: float(np.std(x, ddof=1) / np.sqrt(len(x))) if len(x) > 1 else 0.0
    print(f"\nEXP-45 summary, {SEEDS} seeds, {EPISODES} episodes ({time.time() - t0:.0f}s). Chance: random .121, "
          f"avoid-last .178, never-repeat .304")
    summary = {}
    for bk in BRAINS:
        for sg in SIGNALS:
            rs = [r for r in rows if r["brain"] == bk and r["signal"] == sg and r["seed"] < 42 + SEEDS and r["episodes"] == EPISODES]
            if not rs:
                continue
            m = {k: float(np.mean([r[k] for r in rs])) for k in ("acc", "sampled", "erased", "memoryless", "train_success")}
            m.update(greedy_solved=sum(r["greedy"] for r in rs), all4=sum(r["acc"] == 1.0 for r in rs), n=len(rs),
                     acc_sem=sem([r["acc"] for r in rs]), sampled_sem=sem([r["sampled"] for r in rs]))
            summary[f"{bk}/{sg}"] = m
            print(f"  {bk:4s} {sg:11s} n={m['n']:2d}  acc {m['acc']:.2f} (SEM {m['acc_sem']:.2f}, all-4 {m['all4']})  "
                  f"greedy solved {m['greedy_solved']}  sampled {m['sampled']:.3f} (SEM {m['sampled_sem']:.3f})  "
                  f"erased {m['erased']:.3f}  memoryless {m['memoryless']:.3f}  train {m['train_success']:.2f}")
    json.dump(dict(rows=rows, summary=summary, episodes=EPISODES), open(os.path.join(HERE, f"EXP-45-{TAG}.json"), "w"))


if __name__ == "__main__":
    main()
