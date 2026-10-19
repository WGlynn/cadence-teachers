# EXP-62f: does the order of worth hold when the measuring brain is built differently, not just sized differently?

- Date: pre-registered 2026-10-19 (not run) | Cadence version: 0.84.3 (`8dc92d8`), record at run time | Program iter: iter41 (spawned by EXP-62b)
- Script: `exp/EXP-62f_cross_family_order.py` (EXP-62b's script; only the instruments and seeds change) | Evidence: `exp/EXP-62f-pilot.*`, `exp/EXP-62f-full.*`

## Pre-registration (written 2026-10-19, before any EXP-62f data)

**Question.** EXP-62b found that two brains which take in content rank teachers of equal size the same way (early knowledge worth more than late knowledge), and differ only on the rate. But the two were near relatives: the same delayed-credit brain at two sizes. A sign flip is less likely between relatives than between brains built differently, so that agreement says little in general. Here the second brain has a different architecture: two layers, arousal and recall-memory choice, instead of one layer with working memory and consolidation. If the order still holds, the order of worth survives a change of architecture on this task family. If it flips, whoever picks the architecture sets the order, not just the rate.

**What "built differently" means here, honestly.** All three brains in EXP-62b learn through the same basal-ganglia actor-critic; I have not searched for a `Brain` option that replaces it. EXP-62's harness drives only a `Brain` (`step`, `act`, `reset`). A learner outside `Brain` would need a new adapter, and that would change two things at once. So the cross-family brain here keeps the learning rule and changes the architecture. In EXP-62b the memory-choice brain (B) differed from the delayed-credit brain in its learning rule too, and only its actor step was matched. Its critic stayed 17 times slower (.3 vs 5.0) and its credit traces shorter (lam .8, gamma .9 vs .95, .95; defaults read on 0.84.3 before this registration). It took in almost no content. Matching the whole learning rule tests whether the architecture alone can carry content, and if so, in which order.

**Setup.** EXP-62b's harness and teachers exactly: know-early-2 (right labels on stages 1-2, random elsewhere), know-late-2 (stages 3-4), know-4, null (random labels, the zero), untaught. Lesson 80 (pilot rule below), **48 fresh students** (seeds 7_100_000 + student; no earlier script in `exp/` uses this range, checked by grep). Every arm of a student shares the world seed and the label seed, and every instrument sees the same students.

Instruments, fixed now and not chosen by looking at which brain separates:
- **A**: EXP-58's delayed-credit brain (EXP-62b's A, unchanged), the reference.
- **D1**: the memory-choice architecture (`Brain.compose(10, 5, modules=(48, 24), arousal=True, memory_choice=True)`) with A's whole learning rule: basal ganglia eta .1, eta_bias .01, lam .95, gamma .95, eta_critic 5.0.
- **D2**: D1 with arousal off. A fallback in case arousal is what blocks content, and the next one-gene isolation for upstream #198.

**Validity (per instrument, before any order test).** As in EXP-62b: an instrument takes in content if know-4's worth against the null is at least .10 and at least 2 SEM (paired by student). An instrument that fails is reported as blind and left out of the order test.

**Readings.** Worth = arm accuracy minus the null twin's, same student. Primary quantity: D_I = acc(know-early-2) - acc(know-late-2), paired by student. Cross-family pairs: A-D1 and A-D2. D1-D2 are near relatives (one gene apart), so that pair is exploratory and carries no verdict weight.

**Pilot (before the full run).** 3 students (seeds 7_190_000 + student), all three instruments at lesson 80: cost per student and each instrument's know-4 worth. Rule, as in EXP-62b: if any instrument's pilot know-4 worth is below .05, the full run doubles the lesson to 160 for all three. A longer lesson gives a slow brain a chance to show it takes in content. The rule looks only at know-4, never at D, so the lesson is not picked by peeking at the answer. A longer lesson can still move D (more time to reach late stages), which is why the rule is fixed now. If it fires, compare A and D only within this run, not against EXP-62b's lesson-80 numbers. The pilot cannot change teachers, instruments, seeds, rules or predictions.

**Predictions (written before any data).**
- D1 takes in content: somewhat better than even odds (about 60%). A's content-taking came with its learning rule, which D1 now has.
- D2 takes in content: even odds. No prediction that it beats D1.
- If D1 or D2 takes in content, its D has the same sign as A's (early > late): about 80%. Reason: late knowledge reaches a student only once it gets far enough to make late mistakes, and that does not depend on the architecture.
- No prediction on the size of any cross-family difference.

**Decision rules (written before any data).** Over cross-family pairs (A with each valid D):
- A blind, or no D valid: INCONCLUSIVE (no cross-family comparison); report which were blind and what D1 / D2 read for #198.
- ORDER DEPENDS ON THE ARCHITECTURE: A and some valid D have D of opposite sign, each at least 2 SEM from 0.
- MAGNITUDE ONLY: no opposite-sign cross-family pair, but some |D_A - D_Dx| exceeds 2 SEM (paired by student).
- ORDER AGREES: no opposite-sign cross-family pair and every cross-family |D_A - D_Dx| is within 2 SEM.
- Exploratory, no verdict weight: the D1-D2 pair; each instrument's ranking of the three genuine teachers; untaught vs null per instrument.
Loop verdict: ORDER DEPENDS -> CONFIRMED (the instrument-dependence claim, now across architectures); ORDER AGREES -> REFUTED; MAGNITUDE ONLY or INCONCLUSIVE -> INCONCLUSIVE. Taken together with EXP-62b, MAGNITUDE ONLY or ORDER AGREES here means the order of worth holds across both a change of size and a change of architecture on this task family, while the rate does not (62b).

**Cost.** 48 students x 3 instruments x 5 arms = 720 twins. EXP-62b measured about 37 s per student for A and 66 s for the memory brain at 2 workers, so about 30-40 min at 4 workers (the pilot measures it).

**Pilot (2026-10-19 ~16:05, 108 s at 3 workers; nothing in the design changed).** 3 students (7_190_000+), lesson 80. know-4 worth vs null: A +.52, D1 +.06, D2 +.06. No instrument is below .05, so by the registered rule the full run would stay at lesson 80. But D1 and D2 are not blind, they are at ceiling. Untaught accuracy is 1.00 for all three students, and the null twin scores 1.00, .81 and 1.00. With A's learning rule, the memory-choice architecture solves the task alone inside lesson 80 plus 20 attempts, so a teacher has nothing left to add. D1 and D2 match to the last digit, so arousal has no effect here. The registered pilot rule handles only the too-weak case (lengthen the lesson), not a ceiling. Run as written, the full run would label D1 and D2 "blind" when the true reading is ceiling, and the verdict would be INCONCLUSIVE for a reason the pilot already shows. **Full run NOT started.** The registration is closed at the pilot. The stop is decided by untaught accuracy, which says nothing about the question. It does not rest on D, and D's pilot sign agreed with A's anyway (+.08 vs +.13), so the stop does not dodge an unwelcome answer. The follow-up (EXP-62g) has to make the task hard enough that this brain cannot solve it alone. First sweep the difficulty on untaught D1 students under the exact run conditions. Then pick the setting where they land well below 1.00, and write it down before any teacher data. For upstream #198 this is a reading already, at n 3. The memory-choice brain's near-blindness in EXP-62b came from its learning rule (critic .3, short traces), not from its architecture. Given A's rule, it learns the task on its own. Pilot numbers are n 3, not a result.

## Summary
- PENDING.

## Reflection
- PENDING.
