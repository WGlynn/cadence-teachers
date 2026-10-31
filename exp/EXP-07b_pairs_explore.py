"""EXP-07b exploratory (not pre-registered): after B, does the brain give A cue i and B cue i the same answer?
Same seeds and code path as EXP-07b; records each exam answer instead of only the score."""
import copy, importlib.util, json, os
import numpy as np
spec = importlib.util.spec_from_file_location("m", os.path.join(os.path.dirname(__file__), "EXP-07b_overlap_forgetting.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def answers(brain, cues, pending):
    return [m.live(copy.deepcopy(brain), c, pending) for c in cues]

out = []
for s in range(m.SEEDS):
    rng = np.random.default_rng(m.BASE + s)
    rule_a = m.rule_for(rng); rule_b = {i: 1 - a for i, a in rule_a.items()}
    brain = m.Brain.compose(inputs=6, actions=2, arousal=True, seed=m.BASE + s)
    m.exam(brain, m.B_CUES, rule_b, None)                     # same calls as run(), so the same state
    owed = m.train(brain, rng, m.A_CUES, rule_a, m.N_A, None)
    learner = copy.deepcopy(brain)
    owed_b = m.train(learner, rng, m.B_CUES, rule_b, m.N_B, owed)
    a_ans, b_ans = answers(learner, m.A_CUES, owed_b), answers(learner, m.B_CUES, owed_b)
    same = sum(int(x == y) for x, y in zip(a_ans, b_ans))
    out.append(dict(seed=m.BASE + s, a=a_ans, b=b_ans, same_pairs=same, constant=len(set(a_ans + b_ans)) == 1))
    print(f"seed {m.BASE + s}: A answers {a_ans} B answers {b_ans} same on {same}/4 pairs constant={out[-1]['constant']}", flush=True)
print("pairs answered alike, per seed:", sorted(r["same_pairs"] for r in out))
print("seeds answering one action to all 8 cues:", sum(r["constant"] for r in out))
json.dump(out, open(os.path.join(os.path.dirname(__file__), "EXP-07b-pairs-f84125e.json"), "w"), indent=1)
