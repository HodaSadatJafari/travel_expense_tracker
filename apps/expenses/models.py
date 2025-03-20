from django.db import models
from apps.trips.models import Trip
from apps.core.models.base import BaseModel
from django.utils.translation import gettext_lazy as _

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
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField()

    def __str__(self):
        return f"{self.category}: ${self.amount} on {self.date}"
