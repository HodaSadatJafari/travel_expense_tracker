from django.db import models
from django.contrib.auth.models import User
from apps.core.models.base import BaseModel


class Trip(BaseModel):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"
