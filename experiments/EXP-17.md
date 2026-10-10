# EXP-17: Task-pool capture, how much transfer breaks if the adversary supplies scoring tasks (M5)

- Date: 2026-10-08 | Cadence version: 0.78.0 / `750c8ef` (with the #164 per-probe reset) | Program iter: iter11
- Script: `exp/EXP-17_task_capture.py` | Evidence: `exp/EXP-17.out`; statement in `M5-EXOGENOUS-ANCHOR.md`

## Summary
- Question: if an adversary controls a fraction q of the scoring-task pool (filling it with its own rule R), at what q does expected paired worth (genuine minus fake) reach zero?
- Setup: K=8, 2 actions, modules (16, 8), 1600 witness steps, 12 seeds. R agrees with T on exactly half the contexts. Per seed, four transfers: g_T, g_R (genuine witness scored on T and on R), f_T, f_R (fake witness scored on T and on R). E[v_genuine - v_fake] = (1-q)(g_T - f_T) + q(g_R - f_R) is computed from these for q = 0 to 1 in steps of 0.1.
- Prediction: none written before running.
- Result: means g_T +0.385, g_R -0.031, f_T -0.104, f_R +0.458 (12 seeds). Paired worth falls linearly from +0.490 (SEM 0.010) at q=0 to -0.490 (SEM 0.010) at q=1. Exact crossover q* = 0.500.
- Verdict: SUPPORTIVE as logged. M5 is "STATED AS A BOUNDARY (with a number)" (iter11) and not retracted. The result is a boundary, not a construction: transfer needs an honest majority of tasks, just as PP needs an honest majority of references (EXP-15). The cost-bearing task sources it points to (realized-use filter, commit-reveal ordering, bonded task supply) are all unbuilt.

## Reflection
- What it means: transfer does not escape the exogenous-anchor class. It moves the anchor from peers to tasks. A task can be checked and peer collusion buys nothing, but whoever supplies most of the scoring tasks wins.
- Process: q* = 0.500 is close to forced by the design, not discovered. The script computes the curve as a per-seed linear mix (1-q)(g_T - f_T) + q(g_R - f_R) of four measured components, so linearity in q is guaranteed by construction. With R agreeing on exactly half of T and learning near saturation, the fake on its own task mirrors the genuine witness on its own task: the paired worth is +0.490 at q=0 and -0.490 at q=1 (g_T - f_T and f_R - g_R are each +0.5 on 11 of 12 seeds, 0.375 on the other), so the crossover lands at the midpoint. The per-seed differences are nearly constant (+0.5 in most seeds), so the SEMs are tiny because of the design, not because of power. Only one adversary agreement level (0.5) was tested. A ring whose rule is partly right, or a task pool where tasks are not pure copies of R, would move q*, and that was not measured.
- Lesson: when a headline number comes from a formula over a few means under a symmetric design, say that the symmetry sets it. A boundary result is still a result, as long as it is labeled as one.
- Next: wrote `M5-EXOGENOUS-ANCHOR.md`. After this, only M2-SYNERGY was open, which was taken up in EXP-18. Not yet done: an asymmetric adversary sweep (a_R != 0.5) and any built cost-bearing task source.
