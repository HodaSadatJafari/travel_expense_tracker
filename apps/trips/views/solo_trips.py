from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from apps.expenses.models import Contribution, Expense
from apps.trips.models import Trip, TripParticipant

from ..forms import TripForm


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
    return render(request, "view_trip.html", context)


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
            paid_by=request.user,
            category=category,
            amount=amount,
            description=description,
            date=date,
        )
        return redirect("view_trip", trip_id=trip.id)
    return render(request, "add_expense.html", {"trip": trip})
