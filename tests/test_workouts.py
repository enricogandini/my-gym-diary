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


invalid_exercise_codes = [
    "",
    " ",
    " a",
    "a ",
    "a a",
    "a1",
    "1a",
]


@pytest.mark.parametrize("code", invalid_exercise_codes)
def test_exercise_invalid_code(db, code):
    exercise = Exercise(code=code, name="ciao")
    with pytest.raises(ValidationError):
        exercise.full_clean()
