import datetime

import pytest
from django.core.exceptions import ValidationError

from workouts.models import Exercise, Workout


@pytest.fixture
def workout_empty(db):
    workout = Workout(date=datetime.date(2000, 1, 1))
    workout.save()
    yield workout
    workout.delete()


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
def test_exercise_invalid_code(db, code):
    exercise = Exercise(code=code, name="ciao")
    with pytest.raises(ValidationError):
        exercise.clean_fields()


max_length_name = Exercise._meta.get_field("name").max_length
invalid_exercise_names = [
    "",
    " ",
    " a",
    "a ",
    "a" * (max_length_name + 1),
]


@pytest.mark.parametrize("name", invalid_exercise_names)
def test_exercise_invalid_name(db, name):
    exercise = Exercise(code="ciao", name=name)
    with pytest.raises(ValidationError):
        exercise.clean_fields()
