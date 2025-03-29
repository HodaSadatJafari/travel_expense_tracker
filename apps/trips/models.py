from apps.core.models.users import CustomUser
from django.db import models

from apps.core.models.base import BaseModel


class Trip(BaseModel):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        help_text="Trip creator/owner",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    is_group_trip = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"


class TripParticipant(BaseModel):
    trip = models.ForeignKey(
        Trip, related_name="participants", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        CustomUser, related_name="participated_trips", on_delete=models.CASCADE
    )
    shares = models.PositiveIntegerField(
        default=1,
        help_text="Number of people this participant represents (e.g. family)",
    )

    class Meta:
        unique_together = ("trip", "user")

    def __str__(self):
        display_name = self.user.get_full_name() or self.user.username
        if self.shares > 1:
            display_name += f" ({self.shares} shares)"
        return f"{display_name} in {self.trip.name}"
