"""EXP-55 side check: with memory_choice=True, how often does the answer #197's surprise rule reads (the cortex settle's
argmax, generic.py _choices) differ from the action the brain takes (greedy act, which adds the episodic memory's vote)?
Students: EXP-55's know-4 every-decision demonstrations, rule on, 120 attempts; read on the 16 seen situations from reset."""
import importlib.util, os, sys, tempfile
sys.path.insert(0, os.path.expanduser("~/_cadence_197/src"))
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("e55", os.path.join(HERE, "EXP-55_every_decision_demonstrations.py"))
E = importlib.util.module_from_spec(spec); spec.loader.exec_module(E)
E48 = E.E49.E48
import cadence as cd
tot = diff = cortex_right = act_right = 0
for k in range(4):
    seed = 5_000_000 + 1000 * 120 + k
    s = E.compose(seed, True)
    E.live_demo(s, 120, np.random.default_rng(seed), label=E.labeller("know-4", np.random.default_rng(seed + 1)))
    with tempfile.TemporaryDirectory() as d:
        path = s.save(os.path.join(d, "s.npz"))
        for wx in E.SEEN:
            for st, right in zip(E48.STATES, E48.RIGHTS):
                x = E48.x_of(st, wx)
                b = cd.Brain.load(path); b.reset()
                cortex = int(np.asarray(b._choices(b._qualified(b.stimulus(x), b._activity(), operation="act"))).reshape(-1)[0])
                b = cd.Brain.load(path); b.reset()
                act = int(np.asarray(b.act(x, greedy=True)).reshape(-1)[0])
                tot += 1; diff += cortex != act; cortex_right += cortex == right; act_right += act == right
    print(f"student {k}: so far {tot} situations, cortex != behaviour {diff}, cortex right {cortex_right}, behaviour right {act_right}", flush=True)
print(f"cortex answer differs from greedy behaviour in {diff}/{tot} ({diff/tot:.2f}); right: cortex {cortex_right/tot:.2f}, behaviour {act_right/tot:.2f}")
