from typing import Any

from django.contrib import admin
from django.db.models.query import QuerySet

from .models import Exercise, SetOfExercise, Workout


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "description")
    search_fields = ("code", "name", "description")


class RepetitionsRangesFilter(admin.SimpleListFilter):
    title = "repetitions range"
    parameter_name = "n_repetitions"

    def lookups(self, request, model_admin):
        return (
            ("1-5", "Low"),
            ("6-10", "Medium"),
            ("11-15", "High"),
            (">15", "Very high"),
        )

    def queryset(self, request: Any, queryset: QuerySet) -> QuerySet | None:
        return queryset.repetitions_range(self.value())


@admin.register(SetOfExercise)
class SetOfExerciseAdmin(admin.ModelAdmin):
    list_display = ("workout", "exercise", "n_repetitions", "weight", "notes")
    search_fields = ("notes", "exercise__code", "exercise__name", "workout__date")
    list_filter = ("exercise", "workout__date", RepetitionsRangesFilter)


admin.site.register(Workout)
