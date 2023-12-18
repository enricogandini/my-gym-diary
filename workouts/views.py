import datetime
from collections import Counter

from django.shortcuts import render

from .models import Exercise, SetOfExercise, Workout, get_start_end_dates_from_period


def index(request):
    # TODO: create a form to choose the period
    # use DateRangeField
    # By default the form should be initialized with the current month
    start_date, end_date = get_start_end_dates_from_period(
        datetime.date.today(), "month"
    )
    context = {
        "exercises": Exercise.objects.compute_report(start_date, end_date),
        "interval_statistics": Workout.objects.compute_report(
            start_date, end_date, interval_total=True
        ),
        "start_date": start_date,
        "end_date": end_date,
    }
    return render(request, "workouts/index.html", context)


def dashboard(request):
    stats = SetOfExercise.objects.order_by("workout__date")

    data = Counter()
    for row in stats:
        yymm = row.workout.date.strftime("%Y-%m")
        data[yymm] += 1

    # unpack dict keys / values into two lists
    labels, values = zip(*data.items())

    context = {
        "labels": labels,
        "values": values,
    }
    return render(request, "workouts/dashboard.html", context)
