from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from apps.expenses.models import Expense
from apps.trips.models import Trip, TripParticipant


@login_required
def add_expense(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)

    # Check if this is the user's trip
    if trip.user != request.user:
        messages.error(
            request, _("You don't have permission to add expenses to this trip.")
        )
        return redirect("dashboard")

    # For solo trips, we need to get or create a TripParticipant for the owner
    if not trip.is_group_trip:
        trip_participant, created = TripParticipant.objects.get_or_create(
            trip=trip, user=request.user, defaults={"shares": 1}
        )
    else:
        trip_participant = TripParticipant.objects.get(trip=trip, user=request.user)

    if request.method == "POST":
        category = request.POST["category"]
        amount = request.POST["amount"]
        description = request.POST.get("description", "")
        date = request.POST["date"]

        # Create expense with the TripParticipant instance
        Expense.objects.create(
            trip=trip,
            paid_by=trip_participant,  # Use trip_participant instead of request.user
            category=category,
            amount=amount,
            description=description,
            date=date,
            is_shared=False,  # Solo expenses are not shared
        )

        messages.success(request, _("Expense added successfully!"))
        return redirect("view_trip", trip_id=trip.id)

    return render(request, "add_expense.html", {"trip": trip})
