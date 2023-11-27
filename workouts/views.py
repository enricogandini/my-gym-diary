import datetime

from django.shortcuts import render

from .models import Exercise, get_start_end_dates_from_period


def index(request):
    start_date, end_date = get_start_end_dates_from_period(
        datetime.date.today(), "month"
    )
    context = Exercise.objects.compute_report(start_date, end_date)
    context = {"exercises": list(context)}
    return render(request, "workouts/index.html", context)
