from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from .forms import CustomUserCreationForm


def landing(request):
    return render(request, "index.html")


def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = CustomUserCreationForm()
    return render(request, "signup.html", {"form": form})
