# EXP-20b: learning teacher brains play the measured lesson game (EXP-21 table) under three credit rules

- Date: 2026-10-09 | Cadence version: 0.78.0 / `750c8ef` (iter14 header; not stamped in the output) | Program iter: iter14
- Script: `exp/EXP-20b_teachers_on_table.py` | Evidence: `exp/EXP-20b.out` (table built from `exp/EXP-21-s*.json`)

## Summary
- Question: do two teacher brains, paid only by a credit rule on their students' measured gains, discover the complementary key + door split and drop lamp/spam, how fast, and at what payout budget, under Shapley vs leave-one-out (LOO) vs equal split?
- Setup: two teacher brains (Brain.compose, 1 constant input, 5-way lesson menu: null, key, door, lamp, spam; `step` learning). Each round a student row is drawn at random from the 12 measured EXP-21 students and coalition values are looked up. Rules: shapley phi_i = 1/2 v(i) + 1/2 (v(12) - v(j)); loo = v(12) - v(j); equal = v(12)/2. Reward = 2 x credit. 1500 rounds, 12 runs per rule, same seeds across rules. "Converged" = first 50-round window with at least 80% key/door.
- Prediction: none written in this script before running (its docstring states a question only). The parent EXP-20 docstring predicted "teachers converge on complementary {key, door} and never on spam".
- Result (`exp/EXP-20b.out`, 12 runs per rule, no SEM computed):
  - shapley: greedy end policy key/door in 10/12 runs; last-300 key/door 0.96, lamp/spam 0.02; converged 12/12, median round 39; payout/value 1.00.
  - loo: greedy end key/door 10/12; last-300 key/door 0.96, lamp/spam 0.02; converged 12/12, median round 47; payout/value 1.83.
  - equal: greedy end key/door 11/12; last-300 key/door 0.96, lamp/spam 0.02; converged 12/12, median round 54; payout/value 1.00.
  - Per-run convergence rounds spread widely (shapley 1 to 104, loo 4 to 97, equal 0 to 123).
- Verdict: SUPPORTIVE (iter14: "rung 1 of the teaching game WORKS"). Not retracted. Limited to a lookup table, and it does not separate the credit rules on anything except payout budget.

## Reflection
- What it means: on this table, learning teacher brains reliably come to give key and door and stop giving lamp and spam under every rule tested. LOO overpays (1.83x the value created). Shapley and equal split paying exactly 1.00x is true by construction (both rules sum to v(12)), not a measured finding.
- Process: (1) the iter14 line "converged to key/door 12/12" is the sliding-window convergence count; the greedy end policy is key/door in only 10/12 (shapley), 10/12 (loo), 11/12 (equal), with some runs ending door/spam and one (loo run 3) ending lamp/spam despite 0.93 key/door play in the last 300 rounds. The log does not mention this gap. (2) "Shapley fastest" rests on medians 39 / 47 / 54 from 12 runs each with spreads of roughly 0 to 120 rounds and no SEM or test: within noise, not a ranking. (3) The table is a pure-complement game (only key+door pays; see EXP-21), so all three rules reward the same choices with the same sign and late per-run behavior is nearly identical across rules. The rules were never put where they could disagree; iter14 itself notes free-riding was not testable. (4) Payoffs are looked up from 12 students, not re-measured live; teachers choose from a fixed menu and do not author lessons.
- Lesson: a credit-rule comparison needs a payoff table where the rules give different incentives (for example one lesson that teaches the whole task alone, so free-riding pays under equal split). Report the greedy end state alongside any convergence metric.
- Next: iter14 queued (a) a free-rider game to separate Shapley from equal split, (b) generations (became EXP-22), (c) the inheritance test (became EXP-23). Item (a) is not recorded as run in the sources.
