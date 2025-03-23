from django import forms
from django.utils.translation import gettext_lazy as _

from apps.trips.models import Trip, TripParticipant


class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ["name", "start_date", "end_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError(_("End date must be after start date."))

        return cleaned_data
