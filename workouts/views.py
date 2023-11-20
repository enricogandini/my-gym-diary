from django.http import HttpResponse

from .models import Exercise


def index(request):
    message = "Hello, world. You're at the workouts index."
    exercises = Exercise.objects.all()
    message += f"<br>There are {exercises.count()} exercises."
    for exercise in exercises:
        message += f"<br>{exercise}"
    return HttpResponse(message)
