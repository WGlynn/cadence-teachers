# EXP-39: teaching a prerequisite chain (the "Stone Age COLD" problem)

- Date: 2026-10-10 | Cadence version: 0.80.0 (`19bee92`) | Program iter: iter30
- Script: `exp/EXP-39_prerequisite_chain.py` | Evidence: `exp/EXP-39-full.out`, `exp/EXP-39-full-B*.json/.jsonl`, pilot `exp/EXP-39-pilot-B*.jsonl`

## Summary
- Question: a developer reported that Cadence collapses onto one action instead of learning gather wood -> gather stone -> craft fire -> warm up. Does putting the inventory in the observation, grading every move, and teaching backwards (our advice, based on a 2-step chain) fix a 4-step chain?
- Setup: inventory state (wood, stone, fire), 4 actions, at most 8 moves per episode; Cadence brain at the key-door protocol-3 operating point living through `step`; budgets B = 40 / 150 / 500 / 1500 episodes; 12 seeds; arms SPARSE-FWD, SPARSE-BWD, GRADE-FWD, GRADE-BWD, GRADE-BWD-BLIND (see the script docstring). Test: a frozen copy acts greedily from empty; success = warmed up within 6 moves; policy accuracy over the 5 reachable states.
- Prediction (pre-registered; revised after the 4-seed pilot, before the full run): "GRADE-FWD >= GRADE-BWD at B=40 (dense grading makes backward starts unnecessary); both graded arms solve >= 11/12 from B=150. SPARSE-BWD stays near 0/12 at every budget and collapses onto WARM/CRAFT (the reported failure mode, caused by the reverse curriculum under sparse reward); SPARSE-FWD rises only at the largest budget (6-11/12 at B=1500). BLIND 0/12 everywhere."
- Result (students solving the chain, of 12; budgets B = 40 / 150 / 500 / 1500 episodes):
  SPARSE-FWD 0 / 0 / 1 / 11 (policy accuracy .45 / .60 / .70 / .95); SPARSE-BWD 0 / 0 / 0 / 0 (policy .35 / .35 / .38 / .52;
  the most-used move takes .42-.44 of all moves, i.e. collapse onto WARM/CRAFT); GRADE-FWD 12 / 12 / 12 / 12; GRADE-BWD
  8 / 12 / 12 / 12 (policy .87 at B=40); GRADE-BWD-BLIND 0 / 0 / 0 / 0 (policy .20-.28). Pilot (4 seeds) agreed on every cell's
  direction.
- Verdict: SUPPORTIVE. All five pre-registered predictions held (prediction revised after the pilot, before the full
  run). A grading teacher gets the 4-step chain solved by 12/12 students within 40 episodes; the same brain learning alone
  from sparse world reward needs about 1500 (1/12 at 500, 11/12 at 1500). Hiding the inventory makes it unlearnable at
  every budget. Teaching backwards is unnecessary with grading (8/12 vs 12/12 at B=40) and harmful without it.

## Reflection
- What it means: for prerequisite chains the teacher's value is the per-move signal, worth roughly a 37x saving in
  experience here (12/12 at 40 episodes vs 11/12 at 1500). The observation must carry the chain state (inventory); no
  amount of grading rescues a blind brain. And a reverse curriculum under sparse reward is a trap: starting next to the
  fire teaches "warm" first, the brain latches onto the late-chain moves (craft / warm) and never recovers, which is the
  collapse the developer reported. Plain sparse reward from empty does eventually learn the chain with this brain
  configuration (key-door protocol-3 operating point), so "Cadence cannot learn prerequisite chains" is not supported;
  it needs either more experience or a grading teacher.
- Process: pre-registered and pushed before the full run (599756b); the 2-round-style trap was avoided with a real pilot
  that swept the budget (the window) and printed each link (per-move reward -> policy accuracy -> rollout). The pilot
  overturned part of our own earlier advice ("teach backwards", from a 2-step chain), and the prediction was revised in
  the open before the full run. Caveats: our toy chain, not the developer's environment; one brain configuration; their
  "progressive prefix curriculum" (forward prefixes) was not tested; 12 seeds per cell; the test is one greedy rollout
  per student (deterministic), so "solved" is binary per seed.
- Lesson: test advice before giving it; a mechanism that works on a 2-step chain can invert on a longer one. And give
  credit to the dense signal, not to the curriculum shape.
- Next: correct the reply to the developer (drop "teach backwards"); make prerequisite chains an Arena track (teacher
  submissions choose which moves to grade and in what order, scored by episodes-to-solve); test their forward-prefix
  curriculum; longer chains (6-8 steps) where grading budget and over-drilling (EXP-30) may matter.
