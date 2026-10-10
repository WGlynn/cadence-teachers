# EXP-18: Key/lock (secret-share) witness pair, data-channel synergy (M2-SYNERGY)

- Date: 2026-10-08 | Cadence version: 0.78.0 / `750c8ef` (with the #164 per-probe reset) | Program iter: iter12
- Script: `exp/EXP-18_keylock_synergy.py` | Evidence: `exp/EXP-18.out`

## Summary
- Question: with real learners, does twin-ablation attribution price a purely super-additive pair correctly, and which credit rule (solo, leave-one-out, Shapley) splits it fairly?
- Setup: K=8, 2 actions, modules (16, 8), 1600 witness steps, 12 seeds. A (lock) = rewards masked by a per-step random sign pad. B (key) = the pad. AB = the true reward stream. Fake key B' = an independent pad. Partial key B_p = pad correct with probability p (0.5, 0.625, 0.75, 0.875). v(S) = greedy accuracy on T after ingesting S, minus a twin fed an equal-length pure-noise stream.
- Prediction: none written before running. The docstring states the design intent (solo under-credits, LOO over-credits and sums to about 2x, Shapley is efficient) and the scope ("the synergy is BUILT INTO THE DATA, not composed by the learner").
- Result: v(A) +0.083 (SEM 0.058), v(B) +0.062 (0.103), v(AB) +0.521 (0.070), v(B') +0.115 (0.064), v(AB') +0.031 (0.080). Synergy v(AB) - v(A) - v(B) = +0.375 (SEM 0.090, about 4 sigma). Credits for the genuine pair: solo 0.083 / 0.062 (sum 0.146); LOO 0.458 / 0.438 (sum 0.896, about 1.7x v(AB)); Shapley 0.271 / 0.250 (sum 0.521). With the fake key, Shapley gives A +0.000 and B' +0.031. Partial-key sweep at p = 0.5 / 0.625 / 0.75 / 0.875 / 1.0: -0.052 / +0.188 / +0.365 / +0.479 / +0.521, monotone.
- Verdict: SUPPORTIVE, logged as "M2-SYNERGY CROSSED FOR DATA-CHANNEL SYNERGY ONLY" (iter12). Not retracted. The learned-composition half was then addressed by EXP-19 (iter13). XOR-style representational synergy is still open.

## Reflection
- What it means: when the synergy is real but lives in the data, twin-ablation plus coalition Shapley gives an about even split and gives an honest party nothing when it is paired with a fake. Single leave-one-out ablation double-counts. That Shapley sums to v(AB) is algebra, not a finding. The findings are the even split, the LOO overpayment, and the monotone partial-key curve.
- Process: the zero point is noisy. It is one noise twin per seed, and accN ranges 0.25 to 0.875, so per-seed v values swing (seed 9: v(B) -0.625). The noise floor is visible: the fake key alone, v(B') +0.115, scored higher than the genuine key alone, +0.062. The synergy is built into the reward stream by construction, so this tests the attribution machinery, not whether a Cadence brain composes skills. 12 seeds, one K, one budget. No pilot was run (the RUN GATE did not exist yet); in hindsight v(AB) landed inside the window (+0.521, not at 0 or 1).
- Lesson: price contributions with coalition Shapley over twins, never with single leave-one-out ablation, which overpaid this synergistic pair 1.7x (the log's design note rounds this to ~2x). Average several noise twins for the zero point.
- Next: EXP-19 moved the synergy from the data channel into learned composition on Cadence's key-door world. A pricing question was left open: whether an honest party should be paid on its best coalition rather than the one it landed in (the fake-key case pays honest A 0.00).
