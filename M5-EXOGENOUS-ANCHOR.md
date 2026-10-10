# M5: what transfer still needs from outside (2026-10-08)

Program milestone M5 from `VS-TRANSFER-PROGRAM.md`: say exactly what exogenous ingredient the transfer
measure still assumes, and whether any of it can come from a cost-bearing real signal.

**Verdict: M5 ends as a stated boundary with a measured number, not a construction.** Transfer does not
remove the need for something from outside the system. It moves that need to a different place, where it
can be sourced from real use and where it can be measured.

## The number (EXP-17)

The scoring task is drawn from a pool. The adversary controls a fraction q of that pool and fills it with
tasks matching its own rule (which its witness always aces). 12 seeds, Cadence 0.78.0 clone `750c8ef`,
with the #164 per-probe reset.

| component | mean |
|---|---|
| genuine witness on honest task (g_T) | +0.385 |
| genuine witness on adversary task (g_R) | -0.031 |
| fake witness on honest task (f_T) | -0.104 |
| fake witness on adversary task (f_R) | +0.458 |

Expected paired worth, genuine minus fake, falls linearly from +0.490 at q=0 to -0.490 at q=1.
**Crossover q\* = 0.500.** Whoever supplies the majority of the scoring tasks wins.

## The boundary, stated precisely

- **Peer-prediction needs an honest majority of REFERENCES.** EXP-15: it flips at c ~ 0.5 of the
  reference pool coordinated.
- **Transfer needs an honest majority of TASKS.** EXP-17: it flips at q = 0.5 of the task pool captured.
- Both are majority assumptions about one exogenous input. Transfer does not escape that class. This is
  the same thing `noesis/docs/research/WASH-PROBLEM-INDEX.md:213` says from the graph side: "we are
  missing one exogenous, cost-bearing signal."

What transfer does buy, honestly:
1. **The thing that must be honest is a task, not a person or a peer.** A task can be checked
   (it has an answer). A peer report cannot.
2. **Collusion among peers buys nothing** given an honest task pool (EXP-15: unaffected by c).
3. **A fake that passes an honest task had to carry real task information** (EXP-08 own-task diagnostic,
   EXP-09 proportional curve). Faking collapses into contributing.

## Where honest tasks can come from (cost-bearing sources)

None of these is built. Ranked by how hard they are to capture.

1. **Realized use, revealed after the fact.** The scoring task is drawn from what real users actually
   asked brains to do in a later window. The adversary would have to predict or buy future demand.
   This is the transfer version of Noesis `vesting::independent_use_gate` (`node/src/lib.rs:7323`),
   which vests value only on use by a capital-independent mind. The same capital-cluster oracle that
   gate needs (itself unbuilt) would filter who can supply tasks.
2. **Commit-reveal ordering.** Tasks are committed by hash BEFORE witnesses are submitted and revealed
   after. This stops a witness from being fitted to known tasks, but does not stop the adversary from
   supplying tasks. Necessary, not sufficient.
3. **Task supply bonded by capital.** Each submitted task carries a bond, slashed if the task turns out
   to be unanswerable or to favour one witness only. Raises the price of q, does not bound it.

## What is still assumed after all this

- An honest majority of the scoring task pool (q < 0.5), sourced from independent capital or realized
  use. Not built.
- The capital-cluster oracle that decides "independent". Not built (same gap as Noesis).
- Only measured on a small 8-context bandit. The 0.5 crossover is symmetric here because genuine and fake
  each ace their own task equally. With asymmetric task difficulty the crossover will move.

## Design consequence for Cadence pedigree / teaching market

The brain score used for pricing must name where its test tasks come from. "Held-out tests released
after commit" (flowchart v3) handles the ordering (source 2) but not the supply. The pedigree design needs
a task-supply rule: realized use by independent users, or bonded task submission, with the q < 0.5
assumption stated openly.

Evidence: `exp/EXP-17.out`, `exp/EXP-15.out`, `exp/EXP-08-fixed.out`.
