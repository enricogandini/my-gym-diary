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


class Workout(models.Model):
    date = models.DateField()

    def __str__(self) -> str:
        return f"{self.date}"

    @property
    def n_different_exercises(self) -> int:
        return self.setofexercise_set.values("exercise").distinct().count()


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
