from django.shortcuts import render, redirect
from apps.trips.models import Trip
from apps.expenses.models import Expense
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _


@login_required
def add_expense(request, trip_id):
    trip = Trip.objects.get(id=trip_id)
    if request.method == "POST":
        category = request.POST["category"]
        amount = request.POST["amount"]
        description = request.POST.get("description", "")
        date = request.POST["date"]
        Expense.objects.create(
            trip=trip,
            category=category,
            amount=amount,
            description=description,
            date=date,
        )
        return redirect("view_trip", trip_id=trip.id)
    return render(request, "add_expense.html", {"trip": trip})
