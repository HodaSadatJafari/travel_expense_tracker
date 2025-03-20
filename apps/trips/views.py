from django.shortcuts import render
from apps.trips.models import Trip
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _


from django.shortcuts import render, redirect
from .forms import TripForm
from django.contrib.auth.decorators import login_required


@login_required
def my_trips(request):
    # Filter trips by the currently logged-in user
    user_trips = Trip.objects.filter(user=request.user).order_by("-start_date")
    return render(request, "my_trips.html", {"trips": user_trips})


# @login_required
def add_trip(request):
    if request.method == "POST":
        form = TripForm(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.user = request.user  # Assign the trip to the logged-in user
            trip.save()
            return redirect(
                "view_trip", trip_id=trip.id
            )  # Redirect to the trip detail page
    else:
        form = TripForm()

    return render(request, "add_trip.html", {"form": form})


# @login_required
def view_trip(request, trip_id):
    trip = Trip.objects.get(id=trip_id, user=request.user)
    expenses = trip.expenses.all().order_by("-date")  # Retrieve expenses for this trip

    # Calculate total expenses by category (optional)
    expense_summary = {}
    for expense in expenses:
        expense_summary[expense.category] = (
            expense_summary.get(expense.category, 0) + expense.amount
        )

    context = {
        "trip": trip,
        "expenses": expenses,
        "expense_summary": expense_summary,
    }
    return render(request, "view_trip.html", context)
