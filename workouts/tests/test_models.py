import datetime
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import pytest
from django.core.exceptions import ValidationError
from django.db import models
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


@dataclass(frozen=True)
class ExcelData:
    file: Path
    df: pd.DataFrame
    start_date: datetime.date
    end_date: datetime.date


@pytest.fixture(params=_CORRECT_EXCEL_FILES)
def excel_data(request):
    file = request.param
    df = (
        pd.read_excel(file)
        .assign(volume=lambda df_: df_["Reps"] * df_["Weight"])
        .rename(columns={"Exercise": "code"})
    )
    start_date = df["Date"].min().date()
    end_date = df["Date"].max().date()
    return ExcelData(file=file, df=df, start_date=start_date, end_date=end_date)


def test_load_correct_excel(db, excel_data: ExcelData):
    n_sets_before = SetOfExercise.objects.count()
    created_objects = SetOfExercise.objects.create_from_excel(excel_data.file)
    n_sets_after = SetOfExercise.objects.count()
    retrieved_sets = []
    for row in excel_data.df.itertuples():
        workout = Workout.objects.get(date=row.Date)
        exercise = Exercise.objects.get(code=row.code)
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
    assert len(created_objects["workout"]) == excel_data.df["Date"].nunique()
    assert len(created_objects["exercise"]) == excel_data.df["code"].nunique()


def compute_expected_report(
    df: pd.DataFrame, periodicity: str, per_exercise: bool
) -> pd.DataFrame:
    aggregations = {
        "max_volume": pd.NamedAgg(column="volume", aggfunc="max"),
        "min_volume": pd.NamedAgg(column="volume", aggfunc="min"),
        "avg_volume": pd.NamedAgg(column="volume", aggfunc="mean"),
        "total_volume": pd.NamedAgg(column="volume", aggfunc="sum"),
        "max_weight": pd.NamedAgg(column="Weight", aggfunc="max"),
        "min_weight": pd.NamedAgg(column="Weight", aggfunc="min"),
        "avg_weight": pd.NamedAgg(column="Weight", aggfunc="mean"),
        "total_weight": pd.NamedAgg(column="Weight", aggfunc="sum"),
        "max_repetitions": pd.NamedAgg(column="Reps", aggfunc="max"),
        "min_repetitions": pd.NamedAgg(column="Reps", aggfunc="min"),
        "avg_repetitions": pd.NamedAgg(column="Reps", aggfunc="mean"),
        "total_repetitions": pd.NamedAgg(column="Reps", aggfunc="sum"),
        "n_workouts": pd.NamedAgg(column="Date", aggfunc="nunique"),
        "n_sets": pd.NamedAgg(column="Date", aggfunc="count"),
    }
    grouping = []
    map_rename_index = {}
    match periodicity:
        case "yearly":
            grouping.append(df["Date"].dt.year)
            map_rename_index["Date"] = "year"
        case "monthly":
            grouping.append(df["Date"].dt.month)
            map_rename_index["Date"] = "month"
        case "weekly":
            grouping.append(df["Date"].dt.week)
            map_rename_index["Date"] = "week"
        case "daily":
            grouping.append(df["Date"])
        case "total":
            pass
        case _:
            raise ValueError(f"Invalid periodicity {periodicity}.")
    if per_exercise:
        grouping.insert(0, "code")
    else:
        aggregations["n_unique_exercises"] = pd.NamedAgg(
            column="code", aggfunc="nunique"
        )
    if grouping:
        report = (
            df.groupby(grouping).agg(**aggregations).rename_axis(index=map_rename_index)
        )
    else:
        report = {
            aggregation_name: df[aggregation.column].apply(aggregation.aggfunc)
            for aggregation_name, aggregation in aggregations.items()
        }
        report = pd.DataFrame.from_records([report])
    return report


def test_compute_report_total_per_exercise(db, excel_data: ExcelData):
    SetOfExercise.objects.create_from_excel(excel_data.file)
    report = SetOfExercise.objects.compute_report(
        start_date=excel_data.start_date,
        end_date=excel_data.end_date,
        periodicity="total",
        per_exercise=True,
    )
    assert isinstance(report, models.QuerySet)
    report = (
        pd.DataFrame.from_records(report, coerce_float=True)
        .drop(columns="name")
        .set_index("code")
    )
    assert report.shape[0] == excel_data.df["code"].nunique()
    expected_report = compute_expected_report(
        excel_data.df, periodicity="total", per_exercise=True
    )
    pd.testing.assert_frame_equal(
        left=report,
        right=expected_report,
        check_dtype="equiv",
        check_like=True,
        check_exact=False,
    )


def test_compute_report_total_across_exercises(db, excel_data: ExcelData):
    SetOfExercise.objects.create_from_excel(excel_data.file)
    report = SetOfExercise.objects.compute_report(
        start_date=excel_data.start_date,
        end_date=excel_data.end_date,
        periodicity="total",
        per_exercise=False,
    )
    assert isinstance(report, dict), "Report is not a final aggregation!"
    report = pd.DataFrame.from_records([report], coerce_float=True)
    expected_report = compute_expected_report(
        excel_data.df, periodicity="total", per_exercise=False
    )
    pd.testing.assert_frame_equal(
        left=report,
        right=expected_report,
        check_dtype="equiv",
        check_like=True,
        check_exact=False,
    )


def test_compute_report_yearly_per_exercise(db, excel_data: ExcelData):
    df = (
        pd.read_excel(excel_data.file)
        .assign(volume=lambda df_: df_["Reps"] * df_["Weight"])
        .rename(columns={"Exercise": "code"})
    )
    start_date = df["Date"].min().date()
    end_date = df["Date"].max().date()
    SetOfExercise.objects.create_from_excel(excel_data.file)
    report = SetOfExercise.objects.compute_report(
        start_date=start_date,
        end_date=end_date,
        periodicity="yearly",
        per_exercise=True,
    )
    assert isinstance(report, models.QuerySet)
    report = (
        pd.DataFrame.from_records(report, coerce_float=True)
        .drop(columns="name")
        .set_index(["code", "year"])
    )
    assert report.shape[0] == df["code"].nunique()
    expected_report = compute_expected_report(
        df, periodicity="yearly", per_exercise=True
    )
    pd.testing.assert_frame_equal(
        left=report,
        right=expected_report,
        check_dtype="equiv",
        check_index_type=False,
        check_like=True,
        check_exact=False,
    )


def test_compute_report_yearly_across_exercises(db, excel_data: ExcelData):
    SetOfExercise.objects.create_from_excel(excel_data.file)
    report = SetOfExercise.objects.compute_report(
        start_date=excel_data.start_date,
        end_date=excel_data.end_date,
        periodicity="yearly",
        per_exercise=False,
    )
    assert isinstance(report, models.QuerySet)
    report = pd.DataFrame.from_records(report, coerce_float=True).set_index("year")
    expected_report = compute_expected_report(
        excel_data.df, periodicity="yearly", per_exercise=False
    )
    pd.testing.assert_frame_equal(
        left=report,
        right=expected_report,
        check_dtype="equiv",
        check_index_type=False,
        check_like=True,
        check_exact=False,
    )
