from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from apps.expenses.models import Expense
from apps.trips.models import Trip


@login_required
def add_solo_expense(request, trip_id):
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
        return redirect("view_solo_trip", trip_id=trip.id)
    return render(request, "add_solo_expense.html", {"trip": trip})
