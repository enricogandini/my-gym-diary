import datetime

from django.shortcuts import render

from .models import Exercise, Workout, get_start_end_dates_from_period


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
