from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models.base import BaseModel
from apps.trips.models import Trip, TripParticipant


class Contribution(BaseModel):
    """Track individual contributions to the trip fund"""

    participant = models.ForeignKey(
        TripParticipant, related_name="contributions", on_delete=models.CASCADE
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    notes = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.participant.user.username} contributed ${self.amount} on {self.date}"


CATEGORY_CHOICES = [
    ("FOOD", _("Food")),
    ("ACCOMMODATION", _("Accommodation")),
    ("TRANSPORT", _("Transport")),
    ("ACTIVITIES", _("Activities")),
    ("GAS", _("Gas")),
    ("CAR", _("Car")),
    ("MIC", _("Miscellaneous")),
]


class Expense(BaseModel):
    trip = models.ForeignKey(Trip, related_name="expenses", on_delete=models.CASCADE)
    paid_by = models.ForeignKey(
        TripParticipant, related_name="paid_expenses", on_delete=models.CASCADE
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField()
    is_shared = models.BooleanField(default=True)  # Whether this expense is shared

    def __str__(self):
        return f"{self.category}: ${self.amount} on {self.date} by {self.paid_by.user.username}"


class ExpenseShare(BaseModel):
    expense = models.ForeignKey(
        Expense, related_name="shares", on_delete=models.CASCADE
    )
    participant = models.ForeignKey(
        TripParticipant, related_name="expense_shares", on_delete=models.CASCADE
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ("expense", "participant")

    def __str__(self):
        return (
            f"{self.participant.user.username} owes ${self.amount} for {self.expense}"
        )
