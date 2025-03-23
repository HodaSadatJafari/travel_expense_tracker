from django import forms

from apps.expenses.models import Contribution, Expense
from apps.trips.models import TripParticipant


class GroupExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["paid_by", "category", "amount", "description", "date", "is_shared"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        trip = kwargs.pop("trip", None)
        super().__init__(*args, **kwargs)
        if trip:
            self.fields["paid_by"].queryset = TripParticipant.objects.filter(trip=trip)


class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ["participant", "amount", "date", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        trip = kwargs.pop("trip", None)
        super().__init__(*args, **kwargs)
        if trip:
            self.fields["participant"].queryset = TripParticipant.objects.filter(
                trip=trip
            )
