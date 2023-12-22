import datetime

from django import forms
from django_flatpickr.schemas import FlatpickrOptions
from django_flatpickr.widgets import DatePickerInput

from .models import get_start_end_dates_from_period

_start_date, _end_date = get_start_end_dates_from_period(datetime.date.today(), "month")


class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        label="Start Date",
        initial=_start_date,
        widget=DatePickerInput(options=FlatpickrOptions(altFormat="Y-m-d")),
    )
    end_date = forms.DateField(
        label="End Date",
        initial=_end_date,
        widget=DatePickerInput(
            range_from="start_date", options=FlatpickrOptions(altFormat="Y-m-d")
        ),
    )
