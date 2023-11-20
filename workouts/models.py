from decimal import Decimal

from django.db import models
from django.core.validators import RegexValidator

validator_only_letters = RegexValidator(
    r"^[a-zA-Z]*$", message="Only letters are allowed."
)
validator_only_letters_and_spaces = RegexValidator(
    r"^[a-zA-Z ]*$", message="Only letters and spaces are allowed."
)


class Exercise(models.Model):
    code = models.CharField(
        max_length=5, unique=True, validators=[validator_only_letters]
    )
    name = models.CharField(
        max_length=25, unique=True, validators=[validator_only_letters_and_spaces]
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

    # TODO: add custom Manager, with methods to compute:
    # total volume, total repetitions, total sets in a given period of time: week, month, year.
    def compute_exercise_report(self, period: str) -> dict[str, float]:
        # TODO: check if this works, and add this to a custom objects manager
        sets_exercises = self.setofexercise_set.all()
        n_sets_of_exercises = sets_exercises.count()
        total_volume = sum(set_exercise.volume for set_exercise in sets_exercises)
        total_repetitions = sets_exercises.aggregate(models.Sum("n_repetitions"))[
            "n_repetitions__sum"
        ]
        return {
            "n_sets_of_exercises": n_sets_of_exercises,
            "total_volume": total_volume,
            "total_repetitions": total_repetitions,
        }


class Workout(models.Model):
    date = models.DateField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=["date"], name="unique_date")]

    def __str__(self) -> str:
        return f"{self.date}"

    @property
    def n_different_exercises(self) -> int:
        return self.setofexercise_set.values("exercise").distinct().count()

    def compute_exercise_report(self) -> dict[str, float]:
        sets_exercises = self.setofexercise_set.all()
        n_sets_of_exercises = sets_exercises.count()
        unique_exercises = sets_exercises.values("exercise").distinct()
        n_unique_exercises = unique_exercises.count()
        total_volume = sum(set_exercise.volume for set_exercise in sets_exercises)
        total_repetitions = sets_exercises.aggregate(models.Sum("n_repetitions"))[
            "n_repetitions__sum"
        ]
        return {
            "n_sets_of_exercises": n_sets_of_exercises,
            "n_unique_exercises": n_unique_exercises,
            "total_volume": total_volume,
            "total_repetitions": total_repetitions,
        }


class SetOfExercise(models.Model):
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

    @property
    def volume(self) -> Decimal:
        return self.n_repetitions * self.weight
