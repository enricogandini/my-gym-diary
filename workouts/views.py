import datetime

from django.shortcuts import render

from .charts import Colors, line_chart
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


def dashboard(request):
    total_page_views = {
        "x": ["mon", "tue", "wed", "thur", "fri", "sat", "sun"],
        "y": [8, 20, 15, 20, 50, 30, 35],
        "chart_title": "Total Page Views",
    }

    unique_visitors = {
        "x": ["mon", "tue", "wed", "thur", "fri", "sat", "sun"],
        "y": [3, 4, 10, 12, 30, 20, 33],
        "chart_title": "Unique Visitors",
    }
    signups = {
        "x": ["mon", "tue", "wed", "thur", "fri", "sat", "sun"],
        "y": [3, 4, 10, 12, 30, 20, 33],
        "chart_title": "Signups",
    }
    charts = [
        line_chart(total_page_views),
        line_chart(unique_visitors, Colors.yellow),
        line_chart(signups, Colors.green),
    ]

    context = {"charts": charts}

    return render(request, "workouts/dashboard.html", context)
