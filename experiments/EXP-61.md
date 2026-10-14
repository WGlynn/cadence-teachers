# EXP-61: is it the default brain, or the time alone through `live`, that hides a teacher's content?

- Date: 2026-10-14 | Cadence version: 0.83.0 (`23dba71`, `~/_cadence_study`) | Program iter: none (teaching track; splits EXP-58's stated confound)
- Script: `exp/EXP-61_default_brain_step_alone.py` (EXP-58's protocol with EXP-53's brain) | Evidence: `exp/EXP-61-full.json/.jsonl/.out`

## Summary
- Question: EXP-58 found content (+.47 at 120 attempts) on the delayed-credit brain, where EXP-53 found none (+.11) on the default memory brain. Two things differed: the brain, and the 20 attempts alone (through `step` in EXP-58, because that brain has no arousal genes; through `live` in EXP-53). Here the default memory brain runs EXP-58's exact protocol, alone phase through `step` without labels.
- Setup: EXP-58 exactly (EXP-48's weather chamber, V5's corrective schedule, EXP-53's seeds and world draws, know-4 / random / untaught twins, 40 and 120 attempts, 24 students per length, alone phase through `step`), with EXP-53's brain: `Brain.compose(10, 5, modules=(48, 24), arousal=True, memory_choice=True)`.
- RUN GATE: (1) prediction below, written before any run. (2) Window: no pilot; EXP-53 is this brain on this chamber at these lengths (know-4 .714 / .742, random .701 / .635, untaught .453 / .695). (3) Variance: paired twins. (4) Metric: content = know-4 minus random. (5) Chain: if the brain blocks content, changing only the alone phase leaves content near EXP-53's; if `live` after teaching erased content, `step` keeps it.
- Prediction (written before any run):
  - (P1, headline) The brain is what blocks content: at 120, content stays below .20 (EXP-58's delayed-credit brain had .47), and below half of EXP-58's at 40 (.097).
  - (P2) Being corrected at all still helps this brain: random minus untaught at 40 is above +.10 (EXP-53: +.247).
- Decision rule (written before any run): P1 holds -> the default brain's operating point blocks content, so Noesis-lite v2 runs on the delayed-credit brain and the finding for upstream is about the composed brain, not the teaching path. P1 fails (content near EXP-58's) -> it was `live` after teaching that washed content out on the default brain; that is the finding, and it is about the continuing-life path.
- Result (24 students per length, paired twins; per-state accuracy on unseen weather after 20 attempts alone through `step`; `exp/EXP-61-full.*`), with EXP-53 (same brain, alone phase through `live`) and EXP-58 (delayed-credit brain, alone phase through `step`) for comparison:

  | lesson | know-4 | random labels | untaught | content = know-4 - random (SEM) | know-4 - untaught (SEM) | random - untaught (SEM) |
  |---|---|---|---|---|---|---|
  | 40 | .654 | .703 | .435 | -.049 (.085) | +.219 (.080) | +.268 (.064) |
  | 120 | .669 | .654 | .706 | +.016 (.066) | -.036 (.078) | -.052 (.060) |
  | EXP-53, 40 (`live`) | .714 | .701 | .453 | +.013 (.061) | +.260 | +.247 |
  | EXP-53, 120 (`live`) | .742 | .635 | .695 | +.107 (.064) | +.047 | -.060 |
  | EXP-58, 120 (other brain) | .932 | .464 | .542 | +.469 (.041) | +.391 (.041) | -.078 (.032) |

  P1 HELD: content at 120 is +.016, below .20, and at 40 is -.049, below .097. Against EXP-58 at 120 the gap is .45 (5.8 combined SEM). P2 HELD: being corrected at all is worth +.268 at 40 (4.2 SEM), as in EXP-53 (+.247).
- Verdict: SUPPORTIVE, 2 of 2. Running the alone phase through `step` instead of `live` barely moves the default memory brain: every arm lands within about .06 of EXP-53, and content stays at zero at both lengths. So the default brain's operating point is what blocks a teacher's content. `live` after teaching was not washing it out. Decision rule: P1 held, so Noesis-lite v2 (EXP-62) runs on the delayed-credit brain, and the note for upstream is about the composed default brain, not the teaching path.
- Side observation (not pre-registered): per student, the default brain's outcome is much noisier than the delayed-credit brain's. A know-4 student ends anywhere from .25 to 1.00, and the content SEM is about twice EXP-58's (.085 and .066 against .033 and .041). Two stray lines in the log are the source line of a Python warning raised inside `self.learner.step`; EXP-58's log has the same two, and no row is missing.

## Reflection
- What it means: EXP-58's confound is resolved in favour of the brain. On the default composed brain with episodic memory, labels work as a nudge: being corrected at all helps at 40 attempts (+.27), whatever the labels say, and by 120 the untaught twin catches up and the teacher adds nothing. On the delayed-credit brain, the same labels through the same `step(teacher=...)` call carry almost all of their content. This fits EXP-55's side check (on the default brain, behaviour follows the episodic vote, not the cortex the labels train). For Noesis-lite: a teacher market built on the default brain would be pricing jolts, not knowledge, so v2 runs on the delayed-credit brain.
- Process: pre-registered with no pilot, because EXP-53 already fixed the window for this brain on this chamber at these lengths. Ran on two workers in about nine minutes. Limits: one chamber, the corrective schedule only, 24 students per length, the same seeds and world draws as EXP-53 (so this is a path swap on the same students, not a fresh sample), and P1's .20 bar is loose. The comparison that carries the weight is +.016 against EXP-58's +.469.
- Lesson: when two things differ between a null and a hit, swap one of them alone before writing the story. Here it took a nine-minute run to move the claim from "this brain or this path" to "this brain".
- Next: EXP-62 (Noesis-lite v2 on the delayed-credit brain, priced against the random-label null).
