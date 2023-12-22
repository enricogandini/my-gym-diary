from django import forms
from django_flatpickr.schemas import FlatpickrOptions
from django_flatpickr.widgets import DatePickerInput


class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        label="Start Date",
        widget=DatePickerInput(options=FlatpickrOptions(altFormat="Y-m-d")),
    )
    end_date = forms.DateField(
        label="End Date",
        widget=DatePickerInput(
            range_from="start_date", options=FlatpickrOptions(altFormat="Y-m-d")
        ),
    )
