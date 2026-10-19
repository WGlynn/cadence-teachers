# EXP-62b: does the order of worth among genuine teachers depend on which brain measures it?

- Date: pre-registered 2026-10-19 (not run) | Cadence version: 0.84.3 (`8dc92d8`), record at run time | Program iter: iter40 (VS program NEXT ITERATIONS item 2; absorbs EXP-64)
- Script: `exp/EXP-62b_instrument_order.py` (EXP-62's harness; only the brain and two new teachers change) | Evidence: `exp/EXP-62b-pilot.*`, `exp/EXP-62b-full.*`

## Pre-registration (written 2026-10-19, before any EXP-62b data)

**Question.** Teachers who know the same amount but different parts of the task: do differently built brains rank them in the same order? EXP-58 vs EXP-61 already showed that changing only the brain moves measured worth by about .45 (5.8 combined SEM) with the same contributions, task and oracle. If the ORDER of worth also depends on the brain, v(S) is defined only relative to a committed instrument, and whoever picks the instrument sets the price. That is the premise behind two Noesis design ideas (Desktop noesis-design-brainstorm-2026-10-19.md, ideas 1 and 2: a judge frozen before the round, and several judges paid only where they agree).

**Setup.** EXP-62's harness exactly (live world through `step`, corrective labels after mistakes, lesson then 20 attempts alone, per-state greedy accuracy over 16 states on unseen weather), lesson 80, **48 fresh students** (seeds 7_000_000 + student, disjoint from every earlier run). Every arm of a student shares the world seed and the label seed, as in EXP-62.

Teachers (labels after the student's mistakes, as in EXP-62):
- `know-early-2`: knows the right action at stages 1 and 2 (RIGHTS[0], RIGHTS[1]); a random label elsewhere.
- `know-late-2`: knows stages 3 and 4 (RIGHTS[2], RIGHTS[3]); a random label elsewhere.
- `know-4`: knows all four.
- `null`: random labels (the zero; its labels name the right action at chance, 1 in 5, measured in EXP-62..62e).
- `untaught`: no labels (reported).
Late knowledge reaches a student only if that brain gets far enough to make late mistakes, which is where brains should disagree.

Instruments, fixed now and not chosen by looking at which brain separates:
- **A**: EXP-58's delayed-credit brain (EXP-62's instrument): modules (32,), actor eta .1, eta_bias .01, lam .95, gamma .95, critic 5.0, working-memory amplitude .3, consolidation .25.
- **B**: EXP-61's default memory brain (`Brain.compose(10, 5, modules=(48, 24), arousal=True, memory_choice=True)`) with ONLY the actor step changed, basal ganglia eta 1.0 -> .1 and eta_bias .05 -> .01 (defaults read on 0.84.3 before this registration). This is EXP-64 and gives upstream #198 its reading at the same time.
- **C**: a delayed-credit variant: A with modules (64,) and critic rate 2.0 instead of 5.0.

**Validity (per instrument, before any order test).** An instrument takes in content if know-4's worth against the null is at least .10 and at least 2 SEM (paired by student). An instrument that fails is reported as blind and left out of the order test (not counted as agreeing or disagreeing).

**Readings.** Worth = arm accuracy minus the null twin's, same student. The primary quantity needs no zero: D_I = acc(know-early-2) - acc(know-late-2), paired by student, per instrument I. Pairwise D_I - D_J, paired by student index (shared seeds).

**Pilot (before the full run).** 3 students (seeds 7_090_000 + student), all three instruments at lesson 80: cost per student and each instrument's know-4 worth. Rule: if any instrument's pilot know-4 worth is below .05, the full run uses lesson 160 for all three instruments instead of 80 (a validity window, chosen on know-4 alone, never on D). The pilot cannot change teachers, instruments, seeds, rules or predictions.

**Predictions (written before any data).**
- A and C (same family) agree in sign on D; below even odds that their D differ by more than 2 SEM.
- B is the instrument most likely to be blind (EXP-61's default brain took in no content: +.016) or to disagree; even odds that B takes in content with the actor step at .1.
- No prediction on the sign of D itself.

**Decision rules (written before any data).** Over the instruments that take in content:
- Fewer than two: INCONCLUSIVE (no comparison possible); report which were blind.
- ORDER DEPENDS ON THE INSTRUMENT: some pair I, J has D_I and D_J of opposite sign, each at least 2 SEM from 0. Then v(S) is instrument-relative on this task family; for Noesis the judge must be committed before the work it prices (brainstorm idea 1) and multi-judge disagreement is a real signal (idea 2).
- MAGNITUDE ONLY: no opposite-sign pair, but some |D_I - D_J| exceeds 2 SEM. The brain changes how much the parts are worth, not their order.
- ORDER AGREES: no opposite-sign pair and every |D_I - D_J| is within 2 SEM. A worth independent of the instrument may exist here.
- Exploratory, no verdict weight: each instrument's ranking of the three genuine teachers; whether a majority vote across instruments ranks them in a cycle; untaught vs null per instrument.
Loop verdict: ORDER DEPENDS -> CONFIRMED (the instrument-dependence claim); ORDER AGREES -> REFUTED; MAGNITUDE ONLY or INCONCLUSIVE -> INCONCLUSIVE.

**Cost.** 48 students x 3 instruments x 5 arms = 720 twins; about 25-35 min at 4 workers (pilot measures it).

## Summary
PENDING (after the run)

## Reflection
PENDING (after the run)
