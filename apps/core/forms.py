from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import uuid

from  apps.core.models.users import CustomUser  # Import directly from models.py


class CustomUserCreationForm(forms.ModelForm):
    email = forms.EmailField(
        label=_("Email Address"),
        required=True,
        help_text=_("Enter your email address"),
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput,
        required=True,
        help_text=_("Enter your password"),
    )

    class Meta:
        model = CustomUser
        fields = ("email", "password")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and CustomUser.objects.filter(email=email).exists():
            raise ValidationError(
                _("This email is already registered. Please log in or use a different email address.")
            )
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        # Generate username from email
        base_username = user.email.split('@')[0]
        username = base_username
        counter = 1
        while CustomUser.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
        user.username = username
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number and CustomUser.objects.filter(phone_number=phone_number).exists():
            raise ValidationError(_("A user with this phone number already exists."))
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        phone_number = cleaned_data.get("phone_number")

        if not email and not phone_number:
            raise ValidationError(_("Either email or phone number must be provided"))

        return cleaned_data 