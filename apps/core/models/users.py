from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models.base import BaseModel

class CustomUser(BaseModel, AbstractUser):
    phone_number = models.CharField(
        _("Phone Number"),
        max_length=15,
        blank=True,
        null=True,
        help_text=_("Enter your phone number (optional)"),
    )
    email = models.EmailField(
        _("Email Address"),
        unique=True,
        help_text=_("Enter your email address"),
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) 