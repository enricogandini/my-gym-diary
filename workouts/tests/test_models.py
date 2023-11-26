import datetime

import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from workouts.models import Exercise, Workout


@pytest.fixture
def workout_empty(transactional_db):
    workout = Workout(date=datetime.date(2000, 1, 1))
    workout.save()
    yield workout
    workout.delete()


@pytest.fixture
def exercise(transactional_db):
    exercise = Exercise(code="hello", name="Hello Gym")
    exercise.save()
    yield exercise
    exercise.delete()


max_length_code = Exercise._meta.get_field("code").max_length
invalid_exercise_codes = [
    "",
    " ",
    " a",
    "a ",
    "a a",
    "a1",
    "1a",
    "a" * (max_length_code + 1),
]


@pytest.mark.parametrize("code", invalid_exercise_codes)
def test_exercise_invalid_code(code):
    exercise = Exercise(code=code, name="hello")
    with pytest.raises(ValidationError):
        exercise.clean_fields()


max_length_name = Exercise._meta.get_field("name").max_length
invalid_exercise_names = [
    "",
    " ",
    " a",
    "a ",
    "a  a",
    "a1",
    "1a",
    "a" * (max_length_name + 1),
]


@pytest.mark.parametrize("name", invalid_exercise_names)
def test_exercise_invalid_name(name):
    exercise = Exercise(code="hello", name=name)
    with pytest.raises(ValidationError):
        exercise.clean_fields()


valid_exercise_codes = [
    "a",
    "a" * max_length_code,
    "Z",
    "Z" * max_length_code,
    "aZ",
    "Za",
]


@pytest.mark.parametrize("code", valid_exercise_codes)
def test_exercise_valid_code(db, code):
    exercise = Exercise(code=code, name="hello")
    exercise.full_clean()
    assert exercise.code == code


valid_exercise_names = [
    "a",
    "a" * max_length_name,
    "Z",
    "Z" * max_length_name,
    "aZ",
    "Za",
    "a a",
    "a a a",
    "a a a",
    "Z Z",
    "Z Z Z",
    "aZ Z",
    "Za Z",
    "a Z",
    "Z a",
]


@pytest.mark.parametrize("name", valid_exercise_names)
def test_exercise_valid_name(db, name):
    exercise = Exercise(code="hello", name=name)
    exercise.full_clean()
    assert exercise.name == name


def test_duplicate_exercise_code_invalid(db, exercise):
    exercise_duplicate = Exercise(code=exercise.code, name=exercise.name)
    with pytest.raises(ValidationError):
        exercise_duplicate.full_clean()
    with pytest.raises(IntegrityError):
        exercise_duplicate.save()


def test_ok_exercise_same_code_and_name(db):
    name = "hello"
    exercise = Exercise(code=name, name=name)
    exercise.full_clean()
    exercise.save()
    assert exercise.code == name
    assert exercise.name == name
    exercise.delete()
