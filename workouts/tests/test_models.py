import datetime
from pathlib import Path

import pandas as pd
import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from workouts.models import Exercise, SetOfExercise, Workout

DIR_TEST_DATA = Path(__file__).parent.resolve() / "data"
DIR_EXCEL = DIR_TEST_DATA / "excel"


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
    "a_",
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
    "a_",
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
    new_name = exercise.name + " new"
    exercise_duplicate = Exercise(code=exercise.code, name=new_name)
    with pytest.raises(ValidationError):
        exercise_duplicate.full_clean()
    with pytest.raises(IntegrityError):
        exercise_duplicate.save()


def test_duplicate_exercise_name_invalid(db, exercise):
    new_code = exercise.code + "new"
    exercise_duplicate = Exercise(code=new_code, name=exercise.name)
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


def test_duplicate_workout_date_invalid(db, workout_empty):
    workout_duplicate = Workout(date=workout_empty.date)
    with pytest.raises(ValidationError):
        workout_duplicate.full_clean()
    with pytest.raises(IntegrityError):
        workout_duplicate.save()


_CORRECT_EXCEL_FILES = [
    DIR_EXCEL / file_name
    for file_name in [
        "correct_with_notes.xlsx",
        "correct_no_notes.xlsx",
        "correct_1workout_2exercises.xlsx",
    ]
]


@pytest.mark.parametrize("file", _CORRECT_EXCEL_FILES)
def test_load_correct_excel(db, file):
    df = pd.read_excel(file)
    n_sets_before = SetOfExercise.objects.count()
    created_objects = SetOfExercise.objects.create_from_excel(file)
    n_sets_after = SetOfExercise.objects.count()
    retrieved_sets = []
    for row in df.itertuples():
        workout = Workout.objects.get(date=row.Date)
        exercise = Exercise.objects.get(code=row.Exercise)
        try:
            notes = row.Notes
        except AttributeError:
            notes = None
        retrieved_set = SetOfExercise.objects.get(
            workout=workout,
            exercise=exercise,
            n_repetitions=row.Reps,
            weight=row.Weight,
            notes=notes,
        )
        retrieved_sets.append(retrieved_set)
    n_retrieved_sets = len(retrieved_sets)
    assert n_retrieved_sets == n_sets_after - n_sets_before
    ids_retrieved_sets = {set_.id for set_ in retrieved_sets}
    assert len(ids_retrieved_sets) == n_retrieved_sets
    assert ids_retrieved_sets == set(created_objects["set_of_exercise"])
    assert len(created_objects["workout"]) == df["Date"].nunique()
    assert len(created_objects["exercise"]) == df["Exercise"].nunique()


@pytest.mark.parametrize("file", _CORRECT_EXCEL_FILES)
def test_compute_report_total_per_exercise(db, file):
    df = (
        pd.read_excel(file)
        .assign(volume=lambda df_: df_["Reps"] * df_["Weight"])
        .rename(columns={"Exercise": "code"})
    )
    start_date = df["Date"].min().date()
    end_date = df["Date"].max().date()
    SetOfExercise.objects.create_from_excel(file)
    report = SetOfExercise.objects.compute_report(
        start_date=start_date, end_date=end_date, periodicity="total", per_exercise=True
    )
    report = (
        pd.DataFrame.from_records(report, coerce_float=True)
        .drop(columns="name")
        .sort_values("code")
        .set_index("code")
    )
    assert report.shape[0] == df["code"].nunique()
    expected_report = df.groupby("code").agg(
        max_volume=pd.NamedAgg(column="volume", aggfunc="max"),
        min_volume=pd.NamedAgg(column="volume", aggfunc="min"),
        avg_volume=pd.NamedAgg(column="volume", aggfunc="mean"),
        total_volume=pd.NamedAgg(column="volume", aggfunc="sum"),
        max_weight=pd.NamedAgg(column="Weight", aggfunc="max"),
        min_weight=pd.NamedAgg(column="Weight", aggfunc="min"),
        avg_weight=pd.NamedAgg(column="Weight", aggfunc="mean"),
        total_weight=pd.NamedAgg(column="Weight", aggfunc="sum"),
        max_repetitions=pd.NamedAgg(column="Reps", aggfunc="max"),
        min_repetitions=pd.NamedAgg(column="Reps", aggfunc="min"),
        avg_repetitions=pd.NamedAgg(column="Reps", aggfunc="mean"),
        total_repetitions=pd.NamedAgg(column="Reps", aggfunc="sum"),
        n_workouts=pd.NamedAgg(column="Date", aggfunc="nunique"),
        n_sets=pd.NamedAgg(column="Date", aggfunc="count"),
    )
    # TODO: make this work!
    pd.testing.assert_frame_equal(report, expected_report)
    assert report["n_workouts"] == df["Date"].nunique()
