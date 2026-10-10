# EXP-11: Reinforcement substrate smoke test (bandit learnability + exact twin fork)

- Date: 2026-10-08 | Cadence version: 0.78.0 / 750c8ef | Program iter: iter6
- Script: `exp/EXP-11_smoke_reinforcement.py` | Evidence: no .out file saved; numbers are from EXPERIMENT-RESULTS.md (EXP-11 entry) and VS-TRANSFER-PROGRAM.md iter6

## Summary
- Question: before building the M2-synergy harness on the equilibrium `Reinforcement` creature, can it (a) learn a trivial 4-context bandit on Cadence 0.78 and (b) snapshot and `from_snapshot` into a twin that acts identically?
- Setup: one creature, seed 7. Cortex fan_in 9, parameter_prior 0.3, settle_budget 64; one-hot input of size 4, perception column with 6 patches, policy column with 2 patches. Reinforcement: 2 actions, discount 0.0, exploration 0.1, reward_scale 4.0, capacity 128, batch 4. Rule [0,0,1,1], reward +1 / -1, 400 act/feedback steps cycling the 4 contexts. Greedy eval resets after each probe. Twin check: greedy actions of the original vs the restored snapshot on all 4 contexts.
- Prediction: none written before running. The docstring states only the pass condition: "if the richer substrate can't learn a toy bandit cheaply, or the twin fork isn't exact, we find out in 30 lines, not 300."
- Result: accuracy 0.75 before training, 1.00 after 400 steps; twin greedy actions identical on all 4 contexts (TWIN EXACT), snapshot 19,337 bytes. One seed, 4 contexts, so accuracy moves in steps of 0.25.
- Verdict: SUPPORTIVE (foundation validated). Still current: the exact twin fork was reconfirmed with multi-input + cue in the EXP-12 smoke. The synergy work it was meant to support did not stay on this creature: iter7 found it does not learn XOR, and the later synergy results (EXP-18, EXP-19) were built on the plain `Brain` and the key-door brains, not on this `Reinforcement` snapshot fork.

## Reflection
- What it means: the equilibrium Reinforcement creature can learn a lookup-style bandit and can be forked into a byte-identical twin, which is the precondition for twin-ablation attribution. It says nothing about whether the creature can learn a non-additive task; that was the open question it set up.
- Process: the output was not saved to an .out file, so the numbers rest on the write-up in EXPERIMENT-RESULTS.md only. Single seed. The bandit starts at 0.75 by chance, so the training effect is one context flipping (0.75 to 1.00) and ends at ceiling; it is a smoke test, not a measurement. The design crux recorded alongside it (synergy does not reduce to twin-ablation, needs an irreducible task, couples to Cadence issue #115) was a reasoning finding, not an experimental one.
- Lesson: smoke-test the substrate and the fork before building a multi-condition harness; save the smoke output to a file so the numbers can be checked against evidence, not prose.
- Next: iter6 recorded "design the XOR-channel scaffolding probe deliberately (fresh session)". What followed was the EXP-12 smoke and then the XOR ceiling series EXP-12b to 12f.
