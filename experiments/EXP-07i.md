# EXP-07i: does the episodic memory carry anything to an unseen situation when similar situations share answers, and how does it compare with a plain lookup table?

- Date: pre-registered 2026-11-18 (`b8c12ce`, before any data; stamp line: "stamped EXP-07i b8c12ce on 3 calendars", OpenTimestamps via `stamp_commit.py`, anchor `b19dcf2` in WGlynn/provenance); run 2026-11-18 | Cadence version: 0.101.0 (clone `~/_cadence_study` at `3961509` = origin/main, v0.101.0 plus #350 docs; CPU NumPy loop; BLAS threads pinned to 1 inside the script) | Program iter: iter61 (generic queue; off the V(S) ladder, which waits on Will-gated CAL-1c)
- Script: `exp/EXP-07i_neighbours.py` | Evidence: `exp/EXP-07i-3961509.out`, `.json`, `.err`, `.time`; pilot `exp/EXP-07i-pilot-3961509.out`; rule-level checks `exp/EXP-07i-check-3961509.out`

## Summary
- Question: EXP-07h found that the episodic memory (`memory_choice=True`) beats what any sum of inputs allows on
  XOR feature-and-context rules up to 128 situations, and that on those rules every arm scored within 2 SEM
  of chance on situations held out of training (EXP-07h, 10 seeds at 32 and at 128).
  But on an XOR rule a situation's neighbours are half right and half wrong, so a strict lookup and a
  similarity-weighted recall both predict chance there. Here the neighbours are informative. Two questions: does
  the memory carry anything to an unseen situation when similar situations share answers, and how does the brain
  compare with a plain lookup table on the same closed set?
- Setup:
  - Task family (regular rule with context exceptions): F features and C contexts; a situation (f, c) is a 2-hot
    input over F + C inputs. g is balanced over the features, h over the contexts, drawn per seed. EXP-07h's tiling
    pairs the g = 0 with the g = 1 features and the h = 0 with the h = 1 contexts into quadruples {a, b} x {x, y}.
    The regular rule is t(f, c) = g(f): the answer follows the feature. In a quarter of the quadruples (the
    exception quadruples) the context y reverses it for both features, t(a, y) = 1 and t(b, y) = 0, so inside them
    t = g XOR h. Sizes (8, 4) and (16, 8): 32 and 128 situations (12 and 24 inputs), 2 and 8 exception quadruples
    (4 and 16 exception cells), 1 and 4 held-out quadruples (4 and 16 situations) drawn from the regular ones.
    Trained: 28 and 112 situations.
  - Held out: every held-out situation is regular, its targets are half 1 and half 0 (chance .5; one answer for
    every cue scores exactly .5), and every held-out feature and context also appears in training (asserted per
    seed). A plain lookup has nothing for these cells and predicts .5. The trained cells that share a held-out
    cell's feature share its answer unless they are exceptions.
  - Rule-level references, computed before any brain ran (`exp/EXP-07i-check-3961509.out`): the majority answer
    of the trained cells sharing the feature scores .850 on the held-out cells at 32 (a held-out row keeps only 2
    trained cells at C = 4, and on some seeds one of them is an exception, a tie) and 1.000 at 128; the majority of
    those sharing the feature or the context scores the same (.850, 1.000).
  - Ceiling, exact per seed: a sum of input weights with a threshold on these 2-hot inputs answers 1 where
    w_f + v_c + b > 0, which is exactly a table whose rows are prefixes of one common column order. The script
    tries every column order (C! of them; each row then takes its best prefix), so the ceiling on the trained cells
    is exact. The search reproduces 3/4 on every EXP-07h XOR rule at 8, 32 and 128, and agrees with EXP-07b's
    integer-weight search on 40 of 40 random 4 x 2 tables. Ceilings: .929 (26 of 28) on all 10 seeds at 32; .929
    (104 of 112) on 4 seeds and .920 (103 of 112) on 6 at 128. Bounds: g alone gets .857; one error per exception
    quadruple would be .929. The regular rule g(f) is itself additive and gets every held-out cell right, so an
    additive learner could carry the held-out cells fully.
  - Arms, all on the same cue stream per seed:
    - TABLE: a plain table keyed on the situation: it answers the last rewarded answer for that situation, and a
      random answer (seeded, from its own stream) when it has none; a -1 on its kept answer would clear it (never
      happens on a fixed rule). The lookup-only baseline.
    - FOUNDER: `Brain.compose(inputs=F + C, actions=2, arousal=True, seed=...)`, nothing added.
    - MEMCTX0: the same plus `memory_choice=True, memory_context=0.0` (EXP-07g and EXP-07h's MEMCTX0).
    - MEMORY (a diagnostic read, not an arm): at each MEMCTX0 exam, the place records alone: the sign of the
      records' vote for action 1 minus action 0 on each cue, read on a copy through `brain._episodic.vote(
      brain._placed(x), None)` (the same read the choice adds to the readout; pure, but private attributes); an
      exact tie scores 1/2 and ties are counted. The records key on a fixed random 1024-wide code of the input
      (24 winners), so situations that share a feature or a context have overlapping keys; a strict lookup on
      separate keys would read a tie on every unseen cell.
  - Training through `live` (EXP-07g's moment helper and refusal contract, unchanged): each moment draws a trained
    situation uniformly; +1 right, -1 wrong, given with the next moment. Budget 50 moments per trained situation
    (1,400 at 32, 5,600 at 128; EXP-07h's budget). Greedy exam of every situation, trained and held out, each cue
    on a fresh deepcopy with `act(greedy=True)`, at 25%, 50% and 100% of the budget.
  - Seeds: 10 per size, 7_090_000 + 100 x size index + s (rule, tiling, exception and held-out draws and the cue
    stream from it; the brain seed is the same number).
  - Optional arm (XOR, from the queue item): MEMCTX0 at 128 situations on EXP-07h's own XOR rules and seeds, run
    through EXP-07h's own `run` function with 100 moments per trained situation (11,200), exams at 2,800, 5,600
    and 11,200. Its first 5,600 moments are EXP-07h's run, so its answers at 2,800 and 5,600 should repeat
    EXP-07h's (reported, not a gate). It separates budget from interference in EXP-07h's drop (.963 at 8
    situations to .863 at 128, both at 50 per situation).
  - Version: unchanged since EXP-07h (0.101.0, `3961509`), so no version re-read. The API smoke run (30 moments of
    one seed per arm and size, no scores) passed: every arm composes, trains and answers at both sizes, the
    records' read works, and settings read back as eta 1.0, bias 0.05, memory off (FOUNDER) and on with context
    share 0.0 (MEMCTX0).
  - Budget rule, fixed before the pilot: the pilot times one FOUNDER and one MEMCTX0 life at 128 for 2,000 moments
    in chunks of 500 plus one exam, and prints timings only, no scores. Projection: each arm's mean seconds per
    moment over the 2,000 (warm-up included) times every moment of that arm, plus 3 exams per life. The optional
    XOR arm runs if the projected total is at most 75 minutes; otherwise it is skipped and said so. The pilot may
    change nothing else: not the budget per situation, the seeds, the sizes, the arms, the rules or the criteria.
- Prediction (written before any data):
  - TABLE: trained 1.000 on 10 of 10 seeds at both sizes at the full budget (each trained cell gets at least about
    30 visits), so above the ceiling on every seed; held out at chance by construction. Near certain.
  - FOUNDER: at most 2 of 10 seeds above the ceiling at either size, high confidence (about 90%; no founder has
    beaten a sum-of-inputs ceiling in EXP-07d to EXP-07h). Held out: lean CARRIES at both sizes (about 60%): the
    rule is mostly additive and EXP-07d's founders learned context-alone rules perfectly; the risk is the one-answer
    collapse the combination cells caused in EXP-07d and EXP-07h.
  - MEMCTX0: beating the ceiling needs at most 1 error of 28 at 32 and at most 7 or 8 of 112 at 128. I predict it
    does not LEARN at 128 (fewer than 7 of 10 above), about 65%; no lean at 32. Held out: CARRIES at both sizes,
    about 70%.
  - MEMORY (the records alone): held out CARRIES at both sizes, about 65%, because the records' keys for
    situations that share a feature overlap and those situations mostly share the answer.
  - TABLE above MEMCTX0 on the trained cells by more than 2 SEM (paired) at both sizes, about 90%.
  - XOR arm: the gap is not closed (mean at 100 per situation below .963 - 2 SEM), about 75%; no lean on whether the
    gain from 50 to 100 per situation is detectable. Answers identical to EXP-07h at 2,800 and 5,600 on 10 of 10
    seeds, about 90%.
- Pre-registered rules (all at the full budget, per size):
  - Carry-over, per arm and for MEMORY: held-out mean over seeds with its SEM. CARRIES if above .5 + 2 SEM; CHANCE
    if within .5 +- 2 SEM (consistent with a lookup, not a proof of one); BELOW if under .5 - 2 SEM.
  - Ceiling, per arm and for MEMORY: LEARNS if at least 7 of 10 seeds score above their own seed's ceiling on the
    trained cells; PARTIAL if 3 to 6; FAILS if at most 2.
  - Loop verdict on the prediction, from three parts: (A) MEMORY CARRIES; (B) MEMCTX0 CARRIES; (C) TABLE minus
    MEMCTX0 on the trained cells, paired over seeds, above 2 SEM. CONFIRMED if A, B and C all hold at both sizes;
    REFUTED if any of them fails at both sizes (named); INCONCLUSIVE otherwise (a part that holds at one size only).
    VOID if any arm errors or refuses beyond the 5-try contract.
  - XOR arm readings: the gap CLOSES if the mean at 11,200 is at least .963 - 2 SEM; NO HELP if the paired gain from
    5,600 to 11,200 is within 2 SEM of zero or below; PARTIAL otherwise (more practice helps but the gap stays). NO
    HELP says the drop with size is not a shortfall of practice at this budget; CLOSES says it was.
  - Reported with them (registered secondary, no effect on the verdict): trained mean with SEM, seeds at all right,
    one-answer seeds, accuracy on the exception cells and on the regular trained cells, the curve at 25% and 50%,
    FOUNDER's carry-over, the paired differences MEMCTX0 minus FOUNDER (held out and trained) and MEMORY minus
    MEMCTX0 (held out), MEMORY's ties, and the fewest and most visits any trained situation got.
- Result (2026-11-18; pilot 72 s, run 1,820 s wall, exit 0, stderr empty):
  - Pilot and budget: at 128 FOUNDER took 18.5 s and MEMCTX0 18.2 s for 2,000 moments (first chunk of 500 the
    slowest, 6.5 and 6.8 s), and about 1 s for an exam of 128 cues. Projected total 40 minutes (main 22.6, XOR arm
    17.4), so by the registered rule the XOR arm ran. It took 30 minutes. The pilot changed nothing else. Fewest and
    most visits to any trained situation: 34 to 68 at 32, 29 to 71 at 128.
  - Settings read back: FOUNDER eta 1.0, bias 0.05, memory off; MEMCTX0 the same with memory on, context share 0.0,
    at both sizes.
  - At the full budget, per arm: trained mean (SEM); seeds above their own ceiling out of 10 and the ceiling verdict;
    seeds all right; accuracy on the exception cells and on the regular trained cells; then the held-out mean (SEM)
    and the carry reading:
    - size 32 (1,400 moments): TABLE 1.000 (.000), 10, LEARNS, 10 all right; exceptions 1.000, regular 1.000; held
      .650 (.055) CARRIES (see below: a coin). FOUNDER .779 (.034), 0, FAILS, 0; exceptions .375, regular .846; one
      answer on 1 seed; held .750 (.091) CARRIES. MEMCTX0 .889 (.026), 1, FAILS, 1; exceptions .650, regular .929;
      held .750 (.053) CARRIES. MEMORY (records alone) .939 (.014), 4, PARTIAL, 2; exceptions .775, regular .967;
      held .800 (.062) CARRIES; 0 ties.
    - size 128 (5,600): TABLE 1.000 (.000), 10, LEARNS, 10; exceptions 1.000, regular 1.000; held .537 (.046)
      CHANCE. FOUNDER .770 (.037), 0, FAILS, 0; exceptions .237, regular .858; held .819 (.060) CARRIES. MEMCTX0
      .900 (.014), 3, PARTIAL, 0; exceptions .575, regular .954; held .869 (.027) CARRIES. MEMORY .905 (.010), 3,
      PARTIAL, 0; exceptions .569, regular .961; held .856 (.026) CARRIES; 0 ties.
  - Paired over seeds (registered): TABLE minus MEMCTX0 on trained +.111 (SEM .026) at 32, +.100 (.014) at 128.
    MEMCTX0 minus FOUNDER on held out +.000 (.112) at 32, +.050 (.071) at 128; on trained +.111 (.019) and +.130
    (.041). MEMORY minus MEMCTX0 on held out +.050 (.062) and -.013 (.008).
  - Curves, trained / held-out mean at 25%, 50%, 100%: TABLE .993/.475, 1.000/.575, 1.000/.650 (32) and .999/.475,
    1.000/.531, 1.000/.537 (128). FOUNDER .675/.525, .750/.650, .779/.750 (32) and .671/.731, .801/.881, .770/.819
    (128). MEMCTX0 .779/.675, .839/.700, .889/.750 (32) and .862/.756, .882/.800, .900/.869 (128). MEMORY .900/.775,
    .921/.775, .939/.800 (32) and .883/.794, .889/.800, .905/.856 (128).
  - XOR arm (MEMCTX0, 128 situations, EXP-07h's rules and seeds): trained .835 (SEM .017) at 2,800, .863 (.018) at
    5,600, .927 (.009) at 11,200; paired gain from 50 to 100 per situation +.063 (SEM .013). Answers identical to
    EXP-07h's at 2,800 and at 5,600 on 10 of 10 seeds.
  - The TABLE's held-out score at 32 is a coin: by construction its answers on unseen cells are seeded coin flips
    (expectation .5). It got 26 of 40 right (one-sided chance .040 for a fair coin). It passed the registered rule
    because the sample SEM over 10 seeds (.055) came out below a fair coin's true SEM (.079; with it the bar is .658).
    Checked after the run, not registered: under the same fair-coin model the brain arms' held-out counts at 32 are
    30, 30 and 32 of 40 (FOUNDER, MEMCTX0, MEMORY; one-sided chance .0011, .0011, .0001). At 128, with 16 held-out
    cells per seed, the TABLE sat at chance as built.
  - Exploratory: MEMCTX0's greedy choice agreed with the sign of its records' vote on .938 (32) and .981 (128) of
    all cues; MEMORY minus MEMCTX0 on trained +.050 (SEM .032) at 32 and +.005 (.005) at 128.
- Verdict: by the pre-registered rules, (A) MEMORY CARRIES at 32 and 128; (B) MEMCTX0 CARRIES at both; (C) TABLE
  beats MEMCTX0 on the trained cells by more than 2 SEM at both. Loop verdict on the prediction: CONFIRMED. The rest
  of the prediction: TABLE 1.000 on 10 of 10 as predicted. Its held-out reads CHANCE at 128 and, by the letter of
  the rule, CARRIES at 32, a chance draw of its coin (above). FOUNDER FAILS the ceiling at both sizes (0 of 10) and
  CARRIES at both, as leaned. MEMCTX0 does not LEARN at 128 (PARTIAL, 3 of 10), as predicted, and FAILS at 32
  (1 of 10). XOR arm PARTIAL: more practice helps (gain +.063, SEM .013) but the gap is not closed (.927, below
  .963 - 2 SEM = .945), as predicted, with answers repeating EXP-07h's exactly. Atlas category: SUPPORTIVE.

## Reflection
- What it means:
  - The place records are not a strict lookup. On situations they never stored, the records alone answered the
    held-out cells at .800 (32) and .856 (128). They never read a tie, so every unseen situation read its
    neighbours' records. So EXP-07h's chance on held-out situations came from the XOR rule, not from a lookup.
  - But the memory is not what carried the brain to unseen situations here. The founder, with no episodic memory,
    carried as far: .750 and .819, MEMCTX0 minus FOUNDER +.000 and +.050, both well inside their SEMs. The regular
    part of this rule is a sum of inputs, and the founder's actor learns sums. A likely reason the two match, argued
    from the construction and not measured: on 2-hot inputs, a recall that sums over records whose keys overlap is
    in expectation a row term plus a column term, so it can carry only what a sum of inputs carries.
  - What the memory adds is on situations it has seen: +.111 and +.130 over the founder on the trained cells. Most
    of it is the exceptions: .650 and .575 of them, against the founder's .375 and .237. It still did not beat the
    best sum of inputs on most seeds (1 and 3 of 10). It held about 6 in 10 exceptions and lost a few regular cells.
    That fits the similarity that carries the rule to unseen cells also pulling each exception toward its
    neighbours' answer (records alone: .569 of exceptions against .961 of regular cells at 128), but this run does
    not prove that cause.
  - The plain table got every trained cell right by a quarter of the budget at both sizes. It beat the brain with
    the memory by .10 to .11 on the trained cells and had nothing for unseen ones. On a closed set of situations, a
    table is more accurate and far cheaper.
  - EXP-07h's drop with size is partly a matter of practice. At 128 situations, twice the practice (100 per
    situation) lifted MEMCTX0 from .863 to .927 on EXP-07h's own rules and seeds. That closes about two thirds of
    the gap to the .963 it reached on 8 situations with 50, but not all of it. More situations need more than their
    share of moments.
  - For our learned policies: use a table for situations seen before. Cadence carries a regular rule to unseen
    situations, but on this family the founder did that as well as the brain with the memory. The memory's own
    contribution was holding exceptions in seen situations, and it held only about 6 in 10. A table for seen
    situations and a brain for unseen ones would beat either alone here; that is an inference from these numbers,
    not something this run tested.
- Process:
  - Pre-registered, committed (`b8c12ce`), pushed and Bitcoin-timestamped before any data. The rule-level checks and
    the API smoke run (no scores) came before the pre-registration, the timing pilot (no scores) after it. The
    pilot changed nothing; by the registered rule it ran the optional arm (projected 40 minutes, took 30).
  - The carry rule passed a coin. With 4 held-out cells per seed at 32, the sample SEM over 10 seeds is itself
    noisy, and the table's coin-flip answers cleared .5 + 2 SEM by luck. The brain arms at 32 also clear a fair-coin
    binomial (p .001 or smaller, checked after the run), and 128, with 16 cells per seed, is the clearer reading.
    But the registered rule alone would not have caught a coin.
  - The additive ceiling here is high by design (.920 to .929, a quarter of the quadruples exceptions). Beating it
    needed at most 1 error in 28, or 7 to 8 in 112. So the exception-cell accuracy is the more telling lookup
    reading than the ceiling count.
  - The records-alone read uses private attributes (`_episodic`, `_placed`). It is the vote the choice adds, and
    the choice agreed with its sign on .94 and .98 of cues, but it is not a public API and could move in a release.
  - One version (0.101.0), one task family, one budget per situation in the main arms, 10 seeds. Held-out means
    rest on 4 cells per seed at 32 and 16 at 128.
- Lesson: a carry-over test needs two controls, not one. A rule where neighbours share answers lets a
  similarity-weighted recall show itself. An arm with the same access to the rule's additive part but without the
  memory shows whether the memory is what carries. And when a baseline's null is known exactly (a coin), test
  against that null, not against a SEM estimated from 10 seeds.
- Next: queue item marked done. Queued EXP-07j (ready): can the memory carry what a sum of inputs cannot? It needs
  situation codes whose overlap is graded and not additive, where near situations share answers but no sum of
  inputs fits, with the same arms and the records-alone read.
