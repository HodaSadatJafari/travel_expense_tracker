from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from apps.expenses.forms.group import ContributionForm, GroupExpenseForm
from apps.expenses.models import Contribution, Expense, ExpenseShare
from apps.trips.models import Trip, TripParticipant


@login_required
def add_contribution(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)

    if request.method == "POST":
        form = ContributionForm(request.POST, trip=trip)
        if form.is_valid():
            contribution = form.save()
            return redirect("view_group_trip", trip_id=trip.id)
    else:
        form = ContributionForm(trip=trip)

    return render(request, "add_contribution.html", {"form": form, "trip": trip})
