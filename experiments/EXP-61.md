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
- Result: (pending)
