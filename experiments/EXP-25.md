# EXP-25: The memory door, a skill meant to be hard to teach

- Date: 2026-10-09 | Cadence version: unrecorded (iter17 carries no stamp; iter16 and iter25 both stamp 0.78.0 / 750c8ef) | Program iter: iter17
- Script: `exp/EXP-25_memory_door.py` | Evidence: `exp/EXP-25-found-F1000.out`, `exp/EXP-25-found-F3000-d0.out`, `exp/EXP-25-found-F3000-d2.out`

## Summary
- Question: can founder brains learn a blind memory-door task (chest present only half the time, door press without the key costs 0.25, no pouch sense) at all, so that grading strategies could later be compared on it?
- Setup: blind key-door, chest present with p=0.5, wrong presses cost 0.25, a memoryless policy can score at most 0.50. Founders trained end-to-end with `step` reward, scored on 40 test trips (half chest, half no-chest). Runs: F=1000 trips, delay 2, 6 founders; F=3000, delay 0, 3 founders; F=3000, delay 2, 3 founders. Only Step 1 (founders) was run; Step 2 (teaching strategies) is described in the docstring but not implemented in the script and was never run.
- Prediction: none written before running (the docstring states the 0.50 memoryless ceiling, not an expected outcome).
- Result: F=1000 delay 2: founder scores 0.50, 0.50, 0.00, 0.50, 0.50, 0.00, mean 0.33. Each 0.50 founder solved one trip type only (2 founders all chest trips, 2 founders all no-chest trips). F=3000 delay 0: 0.00, 0.00, 0.00 (mean 0.00). F=3000 delay 2: 0.00, 0.00, 0.00 (mean 0.00). No founder beat the memoryless ceiling.
- Verdict: NULL (founders never learned the task; the teaching step was never reached). Program log iter17 frames it as a boundary on this setup, not a Cadence capability claim. Not later retracted; superseded as the teaching-trait testbed by EXP-26 (tutor focus on a bandit).

## Reflection
- What it means: with plain `step` RL and this reward, our founders do not learn to carry a memory of the chest to the door; at best they pick one memoryless policy (always press or never press). Longer training made it worse (0.00 at 3000 trips; the program log reads this as a collapse to pressing, which the .out files do not show directly). We still do not know whether Cadence can learn this task with another training route; the log notes benchmark memory results use `live` plus arousal, which this script did not use.
- Process: the setup was checked cheaply first (founder step before any teaching runs), which is what the iter17 pilot rule asked for, and it saved a long teaching run. But the runs are small (6 founders at F=1000, only 3 per F=3000 run, 40 test trips each), it never tried a longer delay or intermediate training lengths, and it did not try the `live` plus arousal training path that is known to support memory, so the negative result is about our training choice as much as the task.
- Lesson: a "hard to teach" task must first be learnable by the teacher; confirm the founder can do it, using the training route the library's own memory benchmarks use, before designing teaching arms.
- Next: abandoned this task; moved to EXP-26 (a teaching trait on a K-context bandit that the teacher's own doing cannot see).
