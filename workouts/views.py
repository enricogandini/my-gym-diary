import datetime
from collections import Counter

from django.http import JsonResponse
from django.shortcuts import render

from .forms import DateRangeForm
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


def activity_chart(request):
    if request.method == "POST":
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]

            # Get all sets of exercises for the given period, counting the amount of sets per day
            workouts = Workout.objects.compute_report(start_date, end_date)

            # Prepare data for the chart
            chart_data = {
                "labels": [w.date.isoformat() for w in workouts],
                "values": [w.n_sets_of_exercises for w in workouts],
            }

            return JsonResponse(chart_data)
    else:
        form = DateRangeForm()

    return render(request, "workouts/activity_chart.html", {"form": form})
