"""teachers.lessons: the policy contract the Arena relies on. Fast, no Cadence (students are stubs)."""
import numpy as np
import pytest

from teachers.lessons import LessonView, MissingFirstTeacher, RandomTeacher, check_lesson, grade, rehearse


class _Student:
    """Stub with the slice of Learner that grade/rehearse touch: live(c, judge), known, notes."""

    def __init__(self, known=(), notes=None, move=0):
        self.known, self.notes, self.move, self.steps = set(known), dict(notes or {}), move, []

    def live(self, c, judge):
        self.steps.append((c, judge(self.move)))
        return self.move


VIEW = LessonView(pool=(2, 5, 9, 11), student_wrong=frozenset({11, 5}), budget=7)


def test_random_teacher_is_one_choice_per_step():
    got = RandomTeacher().lesson(VIEW, np.random.default_rng(3))
    ref = np.random.default_rng(3)
    assert got == [int(ref.choice([2, 5, 9, 11])) for _ in range(7)]


def test_missing_first_cycles_wrong_items_without_drawing():
    rng = np.random.default_rng(3)
    state = rng.bit_generator.state
    assert MissingFirstTeacher().lesson(VIEW, rng) == [5, 11, 5, 11, 5, 11, 5]
    assert rng.bit_generator.state == state


def test_missing_first_falls_back_to_random_when_nothing_is_wrong():
    view = LessonView(pool=VIEW.pool, student_wrong=frozenset(), budget=7)
    a, b = np.random.default_rng(8), np.random.default_rng(8)
    assert MissingFirstTeacher().lesson(view, a) == RandomTeacher().lesson(view, b)
    assert a.bit_generator.state == b.bit_generator.state


def test_check_lesson_enforces_budget_and_pool():
    assert check_lesson(VIEW, np.array([2, 2, 5, 9, 11, 11, 2])) == [2, 2, 5, 9, 11, 11, 2]
    with pytest.raises(ValueError, match="budget"):
        check_lesson(VIEW, [2] * 8)
    with pytest.raises(ValueError, match="outside"):
        check_lesson(VIEW, [2, 2, 5, 9, 11, 11, 3])


def test_grade_rewards_matching_the_teacher_not_the_truth():
    teacher_answers = np.array([0, 1, 0, 1])
    s = _Student(move=1)
    assert grade(s, teacher_answers, [1, 0, 3]) == [1, 1, 1]
    assert s.steps == [(1, 1.0), (0, -1.0), (3, 1.0)]


def test_rehearse_grades_against_own_notes():
    s = _Student(known={4, 7}, notes={4: 1, 7: 0}, move=1)
    rng, ref = np.random.default_rng(5), np.random.default_rng(5)
    rehearse(s, 6, rng)
    drawn = [int(ref.choice([4, 7])) for _ in range(6)]
    assert s.steps == [(c, 1.0 if c == 4 else -1.0) for c in drawn]
    empty = _Student()
    state = rng.bit_generator.state
    assert rehearse(empty, 6, rng) == [] and empty.steps == [] and rng.bit_generator.state == state
