from django.shortcuts import render

from .models import Workout


def index(request):
    last_workout = Workout.objects.last()
    context = last_workout.compute_exercise_report()
    context["sets_exercises"] = last_workout.setofexercise_set.all()
    return render(request, "workouts/workouts.html", context)
