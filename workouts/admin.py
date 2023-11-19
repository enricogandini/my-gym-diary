from django.contrib import admin

from .models import Exercise, SetOfExercise, Workout


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "description")
    search_fields = ("code", "name", "description")


@admin.register(SetOfExercise)
class SetOfExerciseAdmin(admin.ModelAdmin):
    list_display = ("exercise", "n_repetitions", "weight", "notes")
    search_fields = ("exercise", "n_repetitions", "weight", "notes")


admin.site.register(Workout)
