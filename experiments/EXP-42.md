# EXP-42: can a Cadence brain learn text one character at a time from grades alone?

- Date: 2026-10-10 | Cadence version: 0.80.0 (`19bee92`) | Program iter: iter32 (pending)
- Script: `exp/EXP-42_char_language.py` | Evidence: `exp/EXP-42-full.json/.jsonl`, `exp/EXP-42-full.out` | Text: `exp/data/alice-ch1.txt` (train), `exp/data/alice-ch2.txt` (held out), from Project Gutenberg #11 (public domain)

## Summary
- Question (Will: "can we make an llm style chat bot with cadence brains"): how far does grading alone (say a character, hear +1 or -1, never the answer) take a Cadence brain on real text? Cadence's own MANIFESTO makes language a dedicated goal and says "the world supplies problems, never answers".
- Setup: Alice chapter 1 (10,891 characters, a-z, space, period) lived through 3 times, then chapter 2 (10,468) held out with learning on (prequential: every character said before it is graded). Cadence arms, modules (32, 16), arousal on: w1 (last character in, one-step episodes), w3 (last 3 characters in), seq (last character in, the life runs on through the text, so the brain's own working trace may carry context). Baselines on the same text: majority character; a tabular epsilon-greedy bandit on the same grades (w1, w3); online n-gram counts that are TOLD the right character (k = 1-4; the LLM training signal, an upper reference). 3 seeds. Also greedy held-out accuracy from a saved copy, and a 160-character sample after "alice was ".
- Prediction (written before the full run; a 600-character smoke run of the code was seen first, too short to read): (P1) Cadence w1 beats the majority baseline on the held-out chapter by >= .02. (P2) No grading learner, Cadence or bandit, reaches the supervised bigram's held-out accuracy: being told only "wrong" is far less information than being told the answer. (P3) w3 does not beat w1 by more than 2 SEM (three-character contexts are too many to explore by grading in one chapter). (P4) seq does not beat w1 by more than 2 SEM (no evidence yet that the working trace carries character context). (P5) Cadence w1 does no better than the tabular bandit on the same grades. (P6) Samples are not English: short loops of frequent characters, at best common pairs.
- Result: PENDING (full run started 2026-10-10 ~17:20).
- Verdict: PENDING.

## Reflection
- PENDING.
