from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from apps.expenses.forms.group import ContributionForm, GroupExpenseForm
from apps.expenses.models import Contribution, Expense, ExpenseShare
from apps.trips.models import Trip, TripParticipant


@login_required
def edit_expense(request, trip_id, expense_id):
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    expense = get_object_or_404(Expense, id=expense_id, trip=trip)

    if request.method == "POST":
        # Get form data
        category = request.POST.get("category")
        amount = request.POST.get("amount")
        description = request.POST.get("description", "")
        date = request.POST.get("date")

        # Update expense
        expense.category = category
        expense.amount = amount
        expense.description = description
        expense.date = date

        # Handle shared expenses for group trips
        if trip.is_group_trip:
            is_shared = request.POST.get("is_shared") == "on"
            expense.is_shared = is_shared

            # Delete old shares
            if is_shared:
                ExpenseShare.objects.filter(expense=expense).delete()

                # Get participants who share this expense
                participants = TripParticipant.objects.filter(trip=trip)
                selected_participant_ids = request.POST.getlist("shared_with", [])

                if selected_participant_ids:
                    # Filter to only selected participants
                    participants = participants.filter(id__in=selected_participant_ids)

                # Calculate shares
                total_shares = sum(p.shares for p in participants)
                if total_shares > 0:
                    share_per_unit = float(expense.amount) / total_shares

                    # Create expense shares
                    for participant in participants:
                        ExpenseShare.objects.create(
                            expense=expense,
                            participant=participant,
                            amount=share_per_unit * participant.shares,
                        )

        expense.save()
        messages.success(request, _("Expense updated successfully."))

        # Redirect based on trip type
        if trip.is_group_trip:
            return redirect("view_group_trip", trip_id=trip.id)
        else:
            return redirect("view_trip", trip_id=trip.id)

    # Prepare context for rendering the form
    context = {
        "trip": trip,
        "expense": expense,
    }

    # Add group trip specific context
    if trip.is_group_trip:
        participants = TripParticipant.objects.filter(trip=trip)
        current_shares = ExpenseShare.objects.filter(expense=expense).values_list(
            "participant_id", flat=True
        )

        context.update(
            {"participants": participants, "current_shares": list(current_shares)}
        )

    # Render appropriate template based on trip type
    if trip.is_group_trip:
        return render(request, "edit_expense_group.html", context)
    else:
        return render(request, "edit_expense.html", context)


@login_required
def delete_expense(request, trip_id, expense_id):
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    expense = get_object_or_404(Expense, id=expense_id, trip=trip)

    if request.method == "POST":
        expense.delete()
        messages.success(request, _("Expense has been deleted."))

        # Redirect based on trip type
        if trip.is_group_trip:
            return redirect("view_group_trip", trip_id=trip.id)
        else:
            return redirect("view_trip", trip_id=trip.id)

    return render(request, "delete_expense.html", {"trip": trip, "expense": expense})
