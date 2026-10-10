"""Lessons: how one Learner teaches another, and the teaching policies that decide what to drill.

A lesson is GRADING, not labels (EXP-22: skill passes down 5 generations by grading; label teaching fails 0/20).
The student acts on each drilled item and gets +1 when its move matches the teacher's answer, -1 otherwise. It never
sees the answer itself, only the grade.

A teaching policy decides WHAT to drill. It is any object with
  .name               a short label for tables and logs
  .lesson(view, rng)  -> list[int] of length view.budget: the items to drill, in order
where view is a LessonView (what the teacher sees when it plans the lesson) and rng is the network's numpy Generator.
Draw randomness only from that rng, so a run is reproducible from its seed. The network shares one rng between
pairing, lessons and rehearsal (the order EXP-33 used), so the number of draws a policy takes shifts the later draws:
compare policies over many seeds, not seed by seed.

RandomTeacher is the EXP-31/33 teacher (one rng.choice(pool) per step, the same draws in the same order), so the
network run with it reproduces EXP-33 exactly. MissingFirstTeacher is a second baseline that drills what the student
currently gets wrong.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .core import Learner


def _matches(answer):
    """Grade a move against one answer: +1 if the move equals it, -1 otherwise."""
    answer = int(answer)
    return lambda a: 1.0 if a == answer else -1.0


# ---------------- graded steps ----------------
def grade(student: Learner, teacher_answers: np.ndarray, items) -> list[int]:
    """One graded step per item, in order: +1 if the student's move matches teacher_answers[item], else -1.
    Returns the student's moves."""
    return [student.live(int(c), _matches(teacher_answers[int(c)])) for c in items]


def rehearse(student: Learner, steps: int, rng: np.random.Generator) -> list[int]:
    """EXP-33 rehearse: `steps` self-practice steps, each on an item drawn uniformly from the student's known set
    (one rng.choice per step) and graded against the student's own notes. Knows nothing: no steps, no draws.
    Returns the student's moves."""
    if not student.known:
        return []
    own = sorted(student.known)
    moves = []
    for _ in range(steps):
        c = int(rng.choice(own))
        moves.append(student.live(c, _matches(student.notes[c])))
    return moves


# ---------------- planning a lesson ----------------
@dataclass(frozen=True)
class LessonView:
    """What a teacher sees when it plans one lesson.

    pool          : the fresh items it may teach, sorted (its known items; with the drift check, only those whose
                    current answer still matches its notes)
    student_wrong : the items in pool where the student's current probe answer differs from the teacher's answer
    budget        : the number of graded steps in the lesson (EXP-33: M = 16)
    """
    pool: tuple[int, ...]
    student_wrong: frozenset[int]
    budget: int


def check_lesson(view: LessonView, items) -> list[int]:
    """Enforce the policy contract: exactly view.budget items, every one from the pool. Returns them as ints.
    A teacher cannot buy extra steps or teach outside what it knows (specialist rule, EXP-29)."""
    items = [int(c) for c in items]
    if len(items) != view.budget:
        raise ValueError(f"lesson has {len(items)} items, budget is {view.budget}")
    outside = sorted(set(items) - set(view.pool))
    if outside:
        raise ValueError(f"lesson drills items outside the teacher's pool: {outside}")
    return items


# ---------------- baseline policies ----------------
class RandomTeacher:
    """EXP-31/33 teacher: each step drills an item drawn uniformly from the pool (one rng.choice(pool) per step)."""
    name = "random"

    def lesson(self, view: LessonView, rng: np.random.Generator) -> list[int]:
        return [int(rng.choice(view.pool)) for _ in range(view.budget)]


class MissingFirstTeacher:
    """Drill what the student gets wrong: cycle through student_wrong (in sorted order) for the whole budget. If the
    student already answers every pool item like the teacher, fall back to RandomTeacher's draws over the pool.
    No draws are taken when there is something to fix."""
    name = "missing-first"

    def lesson(self, view: LessonView, rng: np.random.Generator) -> list[int]:
        wrong = sorted(view.student_wrong)
        if not wrong:
            return RandomTeacher().lesson(view, rng)
        return [wrong[i % len(wrong)] for i in range(view.budget)]
