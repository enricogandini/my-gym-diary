import calendar
import datetime

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


class ExerciseManager(models.Manager):
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
            "total_volume": models.Sum(
                models.F("setofexercise__n_repetitions")
                * models.F("setofexercise__weight")
            ),
        }
        result = self.filter(**filter_dict).annotate(**annotate_dict)
        return result


class Exercise(models.Model):
    objects = ExerciseManager()
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


class WorkoutManager(models.Manager):
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
            "total_volume": models.Sum(
                models.F("setofexercise__n_repetitions")
                * models.F("setofexercise__weight")
            ),
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
    objects = WorkoutManager()
    date = models.DateField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=["date"], name="unique_date")]

    def __str__(self) -> str:
        return f"{self.date}"

    @property
    def n_different_exercises(self) -> int:
        return self.setofexercise_set.values("exercise").distinct().count()


def _get_current_period_id(period: str) -> int:
    today = datetime.date.today()
    calendar = today.isocalendar()
    match period:
        case "week":
            return calendar.week
        case "month":
            return today.month
        case "year":
            return calendar.year
        case _:
            raise ValueError("Invalid period")


class SetOfExerciseManager(models.Manager):
    # TODO: add a constructor method that takes an excel file and creates the objects
    # It should create the exercises if they don't exist.
    # It should create the workouts if they don't exist.
    def compute_report(self, period: str) -> models.QuerySet:
        id_period = _get_current_period_id(period)
        filter_dict = {
            f"workout__date__{period}": id_period,
        }
        annotate_dict = {
            "n_workouts": models.Count("workout", distinct=True),
            "n_unique_exercises": models.Count("exercise", distinct=True),
            "volume": models.F("n_repetitions") * models.F("weight"),
        }
        result = self.filter(**filter_dict).annotate(**annotate_dict)
        return result


class SetOfExercise(models.Model):
    objects = SetOfExerciseManager()
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    workout = models.ForeignKey(
        Workout, on_delete=models.CASCADE, help_text="When was this set performed?"
    )
    n_repetitions = models.PositiveSmallIntegerField(
        verbose_name="Number of repetitions"
    )
    weight = models.DecimalField(
        max_digits=5, decimal_places=1, help_text="Weight in kilograms"
    )
    notes = models.TextField(max_length=1000, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.exercise.code}: {self.n_repetitions} reps at {self.weight} kg"
