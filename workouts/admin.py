from typing import Any

from django.contrib import admin
from django.db.models.query import QuerySet

from .models import Exercise, RepetitionsRanges, SetOfExercise, Workout


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "description")
    search_fields = ("code", "name", "description")
    ordering = ("code",)


class RepetitionsRangesFilter(admin.SimpleListFilter):
    title = "repetitions range"
    parameter_name = "n_repetitions"

    def lookups(self, request, model_admin):
        return [(range.value, range.display_name()) for range in RepetitionsRanges]

    def queryset(self, request: Any, queryset: QuerySet) -> QuerySet | None:
        range = self.value()
        if range is None:
            return queryset
        return queryset.repetitions_range(range)


@admin.register(SetOfExercise)
class SetOfExerciseAdmin(admin.ModelAdmin):
    list_display = ("workout", "exercise", "n_repetitions", "weight", "notes")
    search_fields = ("notes", "exercise__code", "exercise__name", "workout__date")
    list_filter = ("exercise", "workout__date", RepetitionsRangesFilter)
    ordering = ("-workout__date", "exercise__code", "-weight")


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    ordering = ("-date",)
