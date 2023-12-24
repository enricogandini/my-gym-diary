import calendar
import datetime
import re
from collections import defaultdict
from enum import StrEnum
from pathlib import Path

import pandas as pd
from django.core.validators import RegexValidator
from django.db import models

validator_only_latin_letters = RegexValidator(
    r"^[a-zA-Z]*$", message="Only latin letters are allowed."
)
validator_latin_words_single_spaces = RegexValidator(
    r"^[a-zA-Z]+(?: [a-zA-Z]+)*$",
    message="Only latin letters and single spaces are allowed, no trailing spaces.",
)


def get_start_end_dates_from_period(
    center: datetime.date, period: str
) -> tuple[datetime.date, datetime.date]:
    """Returns start and end dates of a period of time, given a center date."""
    match period:
        case "week":
            start_date = center - datetime.timedelta(days=center.weekday())
            end_date = start_date + datetime.timedelta(days=6)
        case "month":
            start_date = center.replace(day=1)
            last_month_day = calendar.monthrange(center.year, center.month)[1]
            end_date = start_date.replace(day=last_month_day)
        case "year":
            start_date = center.replace(month=1, day=1)
            end_date = start_date.replace(month=12, day=31)
        case _:
            raise ValueError("Invalid period")
    return (start_date, end_date)


class ExerciseQuerySet(models.QuerySet):
    def compute_report(
        self, start_date: datetime.date, end_date: datetime.date
    ) -> models.QuerySet:
        if start_date > end_date:
            raise ValueError("Start date must be before end date.")
        filter_dict = {
            "setofexercise__workout__date__range": (start_date, end_date),
        }
        annotate_dict = {
            "n_workouts": models.Count("setofexercise__workout", distinct=True),
            "n_sets": models.Count("setofexercise", distinct=True),
            "n_repetitions": models.Sum("setofexercise__n_repetitions"),
            "total_weight": models.Sum("setofexercise__weight"),
            "total_volume": models.Sum("setofexercise__volume"),
        }
        result = self.filter(**filter_dict).annotate(**annotate_dict)
        return result


class Exercise(models.Model):
    objects = ExerciseQuerySet.as_manager()
    code = models.CharField(
        max_length=5, unique=True, validators=[validator_only_latin_letters]
    )
    name = models.CharField(
        max_length=25, unique=True, validators=[validator_latin_words_single_spaces]
    )
    description = models.TextField(max_length=1000, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(models.functions.Lower("code"), name="unique_code"),
            models.UniqueConstraint(models.functions.Lower("name"), name="unique_name"),
            models.UniqueConstraint(fields=["code", "name"], name="unique_exercise"),
        ]

    def __str__(self) -> str:
        return f"{self.code}: {self.name}"


class WorkoutQuerySet(models.QuerySet):
    def compute_report(
        self,
        start_date: datetime.date,
        end_date: datetime.date,
        interval_total: bool = False,
    ) -> models.QuerySet:
        filter_dict = {
            "date__range": (start_date, end_date),
        }
        stats_dict = {
            "n_sets_of_exercises": models.Count("setofexercise", distinct=True),
            "n_unique_exercises": models.Count(
                "setofexercise__exercise", distinct=True
            ),
            "n_repetitions": models.Sum("setofexercise__n_repetitions"),
            "total_weight": models.Sum("setofexercise__weight"),
            "total_volume": models.Sum("setofexercise__volume"),
        }
        if interval_total:
            stats_dict["n_workouts"] = models.Count("id", distinct=True)
            operation = "aggregate"
        else:
            operation = "annotate"
        result = self.filter(**filter_dict)
        result = getattr(result, operation)(**stats_dict)
        return result


class Workout(models.Model):
    objects = WorkoutQuerySet.as_manager()
    date = models.DateField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=["date"], name="unique_date")]

    def __str__(self) -> str:
        return f"{self.date}"

    @property
    def n_different_exercises(self) -> int:
        return self.setofexercise_set.values("exercise").distinct().count()


class SetOfExerciseManager(models.Manager):
    def create_from_excel(self, path: Path) -> dict[str, list[int]]:
        """Create a set of exercises from an Excel file."""
        df = pd.read_excel(path)
        created_objects = defaultdict(list)
        for id_row, row in df.iterrows():
            try:
                try:
                    exercise = Exercise.objects.get(code__iexact=row["Exercise"])
                except Exercise.DoesNotExist:
                    exercise = Exercise.objects.create(
                        code=row["Exercise"], name=row["Exercise"]
                    )
                    created_objects["exercise"].append(exercise.pk)
                workout, workout_created = Workout.objects.get_or_create(
                    date=row["Date"]
                )
                if workout_created:
                    created_objects["workout"].append(workout.pk)
                set_exercise = self.create(
                    exercise=exercise,
                    workout=workout,
                    n_repetitions=row["Reps"],
                    weight=row["Weight"],
                    notes=row.get("Notes", None),
                )
                created_objects["set_of_exercise"].append(set_exercise.pk)
            except Exception as exc:
                print(f"Skipping row {id_row} because of: {exc}")
        return created_objects


class SetOfExerciseQuerySet(models.QuerySet):
    _pattern_repetitions_range_between = re.compile(r"^(?P<low>\d+)-(?P<high>\d+)$")
    _pattern_repetitions_range_greater = re.compile(r"^>(?P<low>\d+)$")

    def named_repetitions_range(self, range: str) -> models.QuerySet:
        """Filter by named repetitions range."""
        try:
            range = range.replace(" ", "_").upper()
            range = SetOfExercise.REPETITIONS_RANGES[range]
        except KeyError as exc:
            raise ValueError(
                "Invalid repetitions range name. Valid names are: "
                f"{", ".join(
                    [r.display_name() for r in SetOfExercise.REPETITIONS_RANGES]
                )}"
            ) from exc
        else:
            return self.repetitions_range(range.value)

    def repetitions_range(self, range: str) -> models.QuerySet:
        """Filter by repetitions range."""
        if matched := self._pattern_repetitions_range_between.match(range):
            low = int(matched["low"])
            high = int(matched["high"])
            if low > high:
                raise ValueError(
                    "Low repetitions must be lowepyr than high repetitions."
                )
            return self.filter(n_repetitions__range=(low, high))
        elif matched := self._pattern_repetitions_range_greater.match(range):
            low = int(matched["low"])
            return self.filter(n_repetitions__gt=low)
        else:
            print("No filter applied")
            return self

    def compute_report(
        self,
        start_date: datetime.date,
        end_date: datetime.date,
        periodicity: str,
        per_exercise: bool = True,
    ) -> models.QuerySet:
        timerange_periods = ["yearly", "monthly", "weekly"]
        total_period = "total"
        acceptable_period_groupings = timerange_periods + [total_period]
        grouping = []
        sorting = []
        if periodicity not in acceptable_period_groupings:
            raise ValueError(
                f"Invalid periodicity {periodicity}. "
                f"Acceptable values are: {acceptable_period_groupings}"
            )
        if periodicity in timerange_periods:
            periodicity = periodicity.removesuffix("ly")
            periodicity_groupings = {
                "workout__date__year",
                f"workout__date__{periodicity}",
            }
            grouping.extend(periodicity_groupings)
            sorting.extend([f"-{g}" for g in periodicity_groupings])
        if per_exercise:
            grouping.extend(["exercise__code", "exercise__name"])
        filter_dict = {
            "workout__date__range": (start_date, end_date),
        }
        stats_dict = {
            "n_workouts": models.Count("workout", distinct=True),
            "n_sets": models.Count("id"),
            "total_repetitions": models.Sum("n_repetitions"),
            "total_weight": models.Sum("weight"),
            "total_volume": models.Sum("volume"),
        }
        sorting.append("-total_volume")
        result = self.filter(**filter_dict).values(*grouping)
        if periodicity == total_period and not per_exercise:
            action = "aggregate"
        else:
            action = "annotate"
        result = getattr(result, action)(**stats_dict)
        try:
            result = result.order_by(*[f"-{g}" for g in grouping])
        except AttributeError:
            pass
        return result


class SetOfExercise(models.Model):
    objects = SetOfExerciseManager.from_queryset(SetOfExerciseQuerySet)()
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    workout = models.ForeignKey(
        Workout, on_delete=models.CASCADE, help_text="When was this set performed?"
    )
    n_repetitions = models.PositiveSmallIntegerField(
        verbose_name="Number of repetitions"
    )
    weight = models.DecimalField(
        max_digits=6, decimal_places=1, help_text="Weight in kilograms"
    )
    volume = models.GeneratedField(
        expression=models.F("n_repetitions") * models.F("weight"),
        output_field=models.DecimalField(max_digits=10, decimal_places=1),
        db_persist=True,
    )
    notes = models.TextField(max_length=1000, null=True, blank=True)

    class REPETITIONS_RANGES(StrEnum):
        LOW = "1-5"
        MEDIUM = "6-10"
        HIGH = "11-15"
        VERY_HIGH = ">15"

        def display_name(self) -> str:
            return self.name.replace("_", " ").title()

    def __str__(self) -> str:
        return f"{self.exercise.code}: {self.n_repetitions} reps at {self.weight} kg"
