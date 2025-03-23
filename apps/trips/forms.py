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


class GroupTripForm(forms.ModelForm):
    initial_contribution = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text=_("Optional: Your initial contribution to the trip fund"),
    )

    class Meta:
        model = Trip
        fields = ["name", "start_date", "end_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class ParticipantForm(forms.Form):
    first_name = forms.CharField(
        max_length=30, required=False, help_text=_("First name of the participant")
    )
    last_name = forms.CharField(
        max_length=30, required=False, help_text=_("Last name of the participant")
    )
    email = forms.EmailField(
        required=False, help_text=_("Optional: Email address for the participant")
    )
    shares = forms.IntegerField(
        min_value=1,
        initial=1,
        help_text=_("Number of shares (e.g., 2 for a couple, 3 for a family of three)"),
    )
    initial_contribution = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text=_("Optional: Initial contribution to the trip fund"),
    )

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")
        email = cleaned_data.get("email")

        # Ensure at least one identifier is provided
        if not first_name and not last_name and not email:
            raise forms.ValidationError(
                _("At least one of first name, last name, or email must be provided.")
            )

        return cleaned_data
