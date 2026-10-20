# EXP-62g: EXP-62f on a task the cross-family brain cannot solve alone

- Date: pre-registered 2026-10-20 (Will's go 2026-10-20 05:01), before any EXP-62g data | Cadence version: 0.84.3 (`8dc92d8`), record at run time | Program iter: iter41 (EXP-62f closed at its pilot)
- Script: `exp/EXP-62g_budget_cross_family.py` (EXP-62f's script plus a decision-budget knob and a sweep mode) | Evidence: `exp/EXP-62g-sweep.*`, `exp/EXP-62g-pilot.*`, `exp/EXP-62g-full.*`

## Pre-registration (written 2026-10-20, before any EXP-62g data)

**Question.** The same as EXP-62f. Does the order of worth (early knowledge vs late knowledge, equal size) hold when the measuring brain has a different architecture? EXP-62f's pilot could not answer, because D1 (the memory-choice architecture with A's learning rule) solved the task alone. Untaught accuracy was 1.00 for all three pilot students, so a teacher had nothing left to add. EXP-62g makes the task harder, so that D1 alone stays well below 1.00. Then it asks EXP-62f's question again.

**The difficulty knob.** The decision budget per attempt, `MAX_DECISIONS` in EXP-45's chamber (10 today). The chain is wood, stone, fire, warm, in strict order, and a wrong action changes nothing. A student working alone finds the chain by trial and error inside an attempt. A smaller budget leaves less room for that search, so the world's reward (+2 on success) arrives less often. The teachers are untouched: a teacher still labels a mistake at the state where it happens. One side effect is known now. With a smaller budget, a student reaches stages 3 and 4 less often, so it makes fewer late mistakes and know-late-2 gets fewer chances to label. That is part of the task, and every instrument gets the same budget. The effect is not equal, though: a brain that gets further sees more late labels than a brain that stalls early. That was already true at budget 10, and a smaller budget makes it stronger. So a cross-family difference in D can come from how far each brain gets, not only from how it values what it is told. The write-up reports each instrument's late-label count per arm (the labels logged at stages 3-4) next to D. And because the budget can move D for everyone, EXP-62g's D is compared across instruments within this run only, never against EXP-62b or EXP-62f.

**Step 1, the sweep (untaught students only, no teacher arm).** Budgets 10, 8, 6, 5, 4. For each budget, 6 sweep students (seeds 7_280_000 + student, the same seeds at every budget, so the budgets are compared on the same worlds). Arms: untaught D1, plus untaught A, which is reported for information but does not enter the rule. Everything else is the full run's conditions: lesson 80, the 20-attempt alone phase, the same harness and readings. **Selection rule, fixed now:** use the largest budget at which untaught D1's mean accuracy over the 6 sweep students is at most .60. At .60 there is room for a teacher to add more than .10 above the null. If no budget gets D1 to .60 or below, EXP-62g stops after the sweep: D1 solves the chain alone even with 4 decisions (the minimum that can finish it), so this knob cannot make the test, and the next try needs its own registration. The sweep reads untaught accuracy only. It never sees a teacher, a null or D.

**Step 2, the pilot.** 3 students (seeds 7_290_000 + student), all three instruments, all five arms, at the chosen budget and lesson 80. Rule (EXP-62f's, plus the ceiling case it lacked). First, if any instrument's mean untaught accuracy is .90 or more, stop: that is the ceiling again, and the full run is not started. Second, if any instrument's know-4 worth against the null is below .05, the full run doubles the lesson to 160 for all three. Otherwise the lesson stays at 80. The rule looks at untaught accuracy and at know-4, never at D.

**Step 3, the full run.** EXP-62f's design unchanged, except for the budget and the seeds. Teachers: know-early-2, know-late-2, know-4, null (random labels, the zero), untaught. Instruments: A (EXP-58's delayed-credit brain), D1 (`Brain.compose(10, 5, modules=(48, 24), arousal=True, memory_choice=True)` with A's learning rule: basal ganglia eta .1, eta_bias .01, lam .95, gamma .95, eta_critic 5.0), and D2 (D1 with arousal off). **48 fresh students**, seeds 7_200_000 + student. No script in `exp/` uses 7_200_000, 7_280_000 or 7_290_000 (checked by grep). Validity per instrument: know-4 worth against the null of at least .10 and at least 2 SEM, paired by student. D_I = acc(know-early-2) - acc(know-late-2), paired by student. Cross-family verdict pairs: A-D1 and A-D2. D1-D2 is exploratory.

**Predictions (written before any data).**
- The sweep finds a budget at .60 or below: about 75%. Four decisions leave no room for a wrong move, so trial and error alone rarely finishes the chain.
- D1 takes in content at the chosen budget: about 65%.
- If D1 or D2 takes in content, its D has the same sign as A's (early > late): about 80%, for EXP-62f's reason.
- A smaller budget makes early knowledge relatively more valuable for every instrument, because late stages are reached less often. No prediction on any cross-family difference.

**Decision rules (EXP-62f's, unchanged).** Over the cross-family pairs (A with each valid D):
- A blind, or no D valid: INCONCLUSIVE.
- ORDER DEPENDS ON THE ARCHITECTURE: A and some valid D have D of opposite sign, each at least 2 SEM from 0.
- MAGNITUDE ONLY: no opposite-sign cross-family pair, but some |D_A - D_Dx| is above 2 SEM (paired by student).
- ORDER AGREES: no opposite-sign cross-family pair, and every cross-family |D_A - D_Dx| is within 2 SEM.
Loop verdict: ORDER DEPENDS -> CONFIRMED; ORDER AGREES -> REFUTED; MAGNITUDE ONLY or INCONCLUSIVE -> INCONCLUSIVE.

**Cost.** The sweep is 5 budgets x 6 students x 2 untaught twins, a few minutes. The full run is 48 x 3 x 5 = 720 twins. At budget 10 that was about 30-40 min at 4 workers. A smaller budget means shorter attempts, so the full run should take that long or less.

## Sweep
- 2026-10-20 ~05:15, 110 s at 3 workers, Cadence 0.84.3, lesson 80, 6 students (7_280_000+), untaught only (`exp/EXP-62g-sweep.*`). Untaught mean accuracy, D1 | A (A not in the rule): budget 10: .990 | .406; 8: .979 | .542; 6: .562 | .469; 5: .198 | .229; 4: .250 | .292.
- Rule (largest budget with untaught D1 <= .60): **BUDGET = 6.** Nothing else in the design changed.
- What the sweep already says, untaught only: D1 solves the chain alone with 8 or more decisions, about half the time with 6, and almost never with 5 or 4. At budgets 4 and 5 both brains sit near chance (.20), so 6 is the one setting where D1 alone is neither at ceiling nor at the floor. Per-student spread at 6 is wide (one student at 1.00), n 6.

## Pilot
- 2026-10-20 ~05:22, 101 s at 3 workers, BUDGET 6, lesson 80, 3 students (7_290_000+) (`exp/EXP-62g-pilot.*`). Untaught accuracy A .354, D1 .292, D2 .292: no ceiling. know-4 worth vs null: A +.375, D1 +.312, D2 +.312: none below .05. **Rule: full run at lesson 80.** Nothing in the design changed.
- n 3, not a result: all three take in content now, and D has A's sign in every instrument (A +.333, D1 = D2 +.208). D1 and D2 are again identical to the digit, so arousal is inert here too. Late-label events per arm (stages 3-4) show the predicted mechanism: know-early-2 students reach late stages and make late mistakes (A 16.0, D1 30.3 events), know-late-2 students rarely get there (A 3.7, D1 8.3). Against untaught, the null (random labels) is worth +.33 to D1 at this budget, so random labels themselves help this brain; the zero stays the null as registered.

## Summary
- PENDING.

## Reflection
- PENDING.
