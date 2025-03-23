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


@login_required
def add_group_expense(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    participants = TripParticipant.objects.filter(trip=trip)

    if request.method == "POST":
        form = GroupExpenseForm(request.POST, trip=trip)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.trip = trip
            expense.save()

            # Process expense shares based on selection
            if expense.is_shared:
                # Get selected participants or all if none specified
                selected_participant_ids = request.POST.getlist("shared_with", [])
                share_with_participants = participants

                if selected_participant_ids:
                    # Filter to only selected participants
                    share_with_participants = participants.filter(
                        id__in=selected_participant_ids
                    )

                # Calculate total shares among selected participants
                total_shares = sum(p.shares for p in share_with_participants)

                if total_shares > 0:
                    # Calculate share per unit
                    share_per_unit = expense.amount / total_shares

                    # Create expense shares
                    for participant in share_with_participants:
                        ExpenseShare.objects.create(
                            expense=expense,
                            participant=participant,
                            amount=share_per_unit * participant.shares,
                        )

            return redirect("view_group_trip", trip_id=trip.id)
    else:
        form = GroupExpenseForm(trip=trip)

    return render(
        request,
        "add_group_expense.html",
        {"form": form, "trip": trip, "participants": participants},
    )
