from django.db import models
from django.core.validators import RegexValidator

validator_only_letters = RegexValidator(r"^[a-zA-Z]*$", "Only letters are allowed.")
validator_only_letters_and_spaces = RegexValidator(
    r"^[a-zA-Z ]*$", "Only letters and spaces are allowed."
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
