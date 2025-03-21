from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect


def landing(request):
    return render(request, "landing_page.html")


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "signup.html", {"form": form})
