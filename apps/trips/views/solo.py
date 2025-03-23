from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from apps.trips.forms.solo import TripForm
from apps.trips.models import Trip, TripParticipant


@login_required
def add_solo_trip(request):
    if request.method == "POST":
        form = TripForm(request.POST)
        if form.is_valid():
            name = request.POST["name"]
            start_date = request.POST["start_date"]
            end_date = request.POST["end_date"]

            # Create trip
            trip = form.save(commit=False)
            trip.user = request.user  # Assign the trip to the logged-in user
            trip.save()

            # Create trip participant for the owner
            TripParticipant.objects.create(trip=trip, user=request.user, shares=1)

            messages.success(request, _("Trip created successfully!"))
            return redirect("dashboard")
    else:
        form = TripForm()

    return render(request, "add_solo_trip.html", {"form": form})


@login_required
def view_solo_trip(request, trip_id):
    trip = Trip.objects.get(id=trip_id, user=request.user)
    expenses = trip.expenses.all().order_by("-date")  # Retrieve expenses for this trip

    # Calculate total expenses by category (optional)
    total_expense = 0
    expense_summary = {}
    for expense in expenses:
        expense_summary[expense.category] = (
            expense_summary.get(expense.category, 0) + expense.amount
        )
        total_expense += expense.amount

    context = {
        "trip": trip,
        "total_expense": total_expense,
        "expenses": expenses,
        "expense_summary": expense_summary,
    }
    return render(request, "view_solo_trip.html", context)
