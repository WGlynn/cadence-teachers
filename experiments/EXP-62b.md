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

**Pilot (2026-10-19, before the full run; nothing in the design changed).** 3 students (7_090_000+), lesson 80, 234 s at 2 workers (about 37 / 66 / 39 s per student for A / B / C). know-4 worth vs null: A +.52, B +.06, C +.38, so no instrument is below .05 and the full run stays at lesson 80. Pilot numbers are not a result (n 3).

**Cost.** 48 students x 3 instruments x 5 arms = 720 twins; about 25-35 min at 4 workers (pilot measures it).

## Summary
- Question: do differently built brains rank teachers who know the same amount, but different parts of the task, in the same order?
- Setup: as registered. Cadence 0.84.3 (`8dc92d8`), lesson 80 (pilot rule), 48 fresh students (7_000_000+), three instruments, 720 twins, 2,802 s at 2 workers.
- Prediction: A and C agree in sign on D; below even odds that their D differ by more than 2 SEM; B the most likely to be blind; no prediction on the sign of D.
- Result (worth = accuracy minus the random-label null twin, same student):
  - A (delayed-credit): know-early-2 +.264 (SEM .025), know-late-2 +.064 (.023), know-4 +.432 (.026). Takes in content. D = early - late +.201 (.026).
  - B (default memory brain, actor step .1): know-early-2 +.039, know-late-2 +.007, know-4 +.069 (.016). Blind by the registered bar (know-4 below .10).
  - C (delayed-credit, 64 units, critic 2.0): know-early-2 +.339 (.026), know-late-2 +.036 (.022), know-4 +.458 (.031). Takes in content. D = +.302 (.029).
  - A vs C, paired by student: D_A - D_C = -.102 (SEM .036, 2.8 SEM). Same sign, both far from zero.
  - Both valid instruments rank know-4 > know-early-2 > know-late-2; no cycle across instruments (exploratory).
- Verdict: MAGNITUDE ONLY (loop: INCONCLUSIVE). The brain changed how much early knowledge is worth relative to late knowledge, not the order.

## Reflection
- What it means: the judge sets the exchange rate, not the order. Both brains that take in content rank the teachers the same way. They disagree on how much late knowledge is worth next to early knowledge: about a quarter on A (.064 / .264), about a ninth on C (.036 / .339). Late knowledge only reaches a student who gets far enough to make late mistakes, so a brain that progresses less prices it lower. Whoever picks the judge therefore sets that rate even when the order holds. That still argues for committing the judge before the work it prices (Noesis brainstorm idea 1). It also suggests judges can agree on order here (idea 2) while disagreeing on price. B, the default memory brain with only the actor step lowered (EXP-64), barely takes in content (+.069 for full knowledge), so for upstream #198 the actor step alone does not open this brain to content in this protocol; the block is elsewhere (critic, arousal or the vote).
- Process: pre-registered before any data (39ab1a4) and the pilot recorded before the full run (10a35a4); run as written. My prediction that A and C would not differ by more than 2 SEM was wrong (2.8 SEM). Two instruments from one family is a narrow test of order: a sign flip is less likely between near relatives than between unrelated brains, so agreement here says little about brains built differently. B being blind left only that pair.
- Lesson: separate order from magnitude when asking whether a value measure depends on the instrument. They can come apart, and payout rules depend on both.
- Next: a third content-taking instrument from a different family (not a delayed-credit relative) is needed before claiming order agreement in general; candidate EXP-62f. For #198 (EXP-64's question): the next isolation is the critic rate or arousal on the default memory brain, one gene at a time.

## Addendum 2026-10-20: scaled re-read (exploratory, existing data, no verdict change)
- Prompted by EXP-62g, where the cross-family brain absorbed about twice the reference's content and the gap between them vanished once each instrument was scaled by its own know-4 worth. Here, on this run's 48 students (paired bootstrap, 5,000 draws):
  - know-4 worth A .432, C .458: the two absorb about the same, so scale cannot explain their difference.
  - Late/early worth ratio A .241 (95% interval .081 to .394), C .108 (-.014 to .226); difference -.134 (-.340 to +.073).
  - D as a share of know-4: A .464, C .659; difference +.195 (+.013 to +.370).
- Reading: these two near relatives disagree on the exchange rate even at equal scale, while EXP-62g's pair built differently agrees once scaled. Scaling by an instrument's own range is not a general fix. The verdict stays MAGNITUDE ONLY.
