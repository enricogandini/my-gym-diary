from django.db import models


class Exercise(models.Model):
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=25, unique=True)
    description = models.TextField(max_length=1000, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(models.functions.Lower("code"), name="unique_code"),
            models.UniqueConstraint(models.functions.Lower("name"), name="unique_name"),
            models.UniqueConstraint(fields=["code", "name"], name="unique_exercise"),
        ]

    def __str__(self) -> str:
        return f"{self.code}: {self.name}"
