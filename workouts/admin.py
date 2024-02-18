from typing import Any

from django.contrib import admin
from django.db.models.query import QuerySet

from .models import Exercise, MovementPattern, MuscleGroup, SetOfExercise, Workout


@admin.register(MuscleGroup)
class MuscleGroupAdmin(admin.ModelAdmin):
    ordering = ("name",)


@admin.register(MovementPattern)
class MovementPatternAdmin(admin.ModelAdmin):
    ordering = ("name",)


class MuscleGroupInline(admin.TabularInline):
    model = Exercise.muscle_groups.through
    extra = 1


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "description")
    search_fields = ("code", "name", "description")
    ordering = ("code",)
    inlines = (MuscleGroupInline,)

    def save_related(self, request, form, formsets, change):
        """
        Ensure that an exercise has at least one muscle group.
        If it has more than one, remove the default one.

        NOTE: the Admin interface must be used to create exercises!
        This logic would not be applied if the exercise is created via the Model API.
        See this issue for more details:
        https://forum.djangoproject.com/t/how-to-set-default-value-to-manytomanyfield/27971
        """
        super().save_related(request, form, formsets, change)
        default_muscle_group = MuscleGroup.get_default_instance()
        exercise = form.instance
        if exercise.muscle_groups.count() > 1:
            exercise.muscle_groups.remove(default_muscle_group)
        else:
            exercise.muscle_groups.add(default_muscle_group)


class RepetitionsRangesFilter(admin.SimpleListFilter):
    title = "repetitions range"
    parameter_name = "n_repetitions"

    def lookups(self, request, model_admin):
        return [
            (range.value, range.display_name())
            for range in SetOfExercise.REPETITIONS_RANGES
        ]

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
    show_facets = admin.ShowFacets.ALWAYS


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    ordering = ("-date",)
