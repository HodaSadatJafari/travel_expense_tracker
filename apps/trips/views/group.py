from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

from apps.core.utils import get_or_create_user
from apps.expenses.models import Contribution, Expense, ExpenseShare
from apps.trips.forms.group import GroupTripForm, ParticipantForm
from apps.trips.models import Trip, TripParticipant


@login_required
def add_group_trip(request):
    if request.method == "POST":
        form = GroupTripForm(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.user = request.user
            trip.is_group_trip = True
            trip.save()

            # Add creator as participant
            participant = TripParticipant.objects.create(
                trip=trip, user=request.user, shares=1
            )

            # Add initial contribution if specified
            initial_contribution = form.cleaned_data.get("initial_contribution")
            if initial_contribution and initial_contribution > 0:
                Contribution.objects.create(
                    participant=participant,
                    amount=initial_contribution,
                    notes="Initial contribution",
                )

            return redirect("manage_participants", trip_id=trip.id)
    else:
        form = GroupTripForm()

    return render(request, "add_group_trip.html", {"form": form})


@login_required
def manage_participants(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)

    if request.method == "POST":
        form = ParticipantForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            email = form.cleaned_data.get("email")
            shares = form.cleaned_data.get("shares")

            # Get or create the user
            user, created = get_or_create_user(
                first_name=first_name, last_name=last_name, email=email
            )

            # Create participant
            participant, p_created = TripParticipant.objects.get_or_create(
                trip=trip, user=user, defaults={"shares": shares}
            )

            # If participant already existed, update shares
            if not p_created:
                participant.shares = shares
                participant.save()

            # Add initial contribution if specified
            initial_contribution = form.cleaned_data.get("initial_contribution")
            if initial_contribution and initial_contribution > 0:
                Contribution.objects.create(
                    participant=participant,
                    amount=initial_contribution,
                    notes="Initial contribution",
                )

            return redirect("manage_participants", trip_id=trip.id)
    else:
        form = ParticipantForm()

    participants = TripParticipant.objects.filter(trip=trip)

    return render(
        request,
        "manage_participants.html",
        {"trip": trip, "participants": participants, "form": form},
    )


@login_required
def view_group_trip(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    # Ensure user is owner or participant
    user_is_participant = TripParticipant.objects.filter(
        trip=trip, user=request.user
    ).exists()
    if trip.user != request.user and not user_is_participant:
        return HttpResponseForbidden()

    participants = TripParticipant.objects.filter(trip=trip)
    expenses = Expense.objects.filter(trip=trip).order_by("-date")

    # Calculate contributions
    contributions_by_participant = {}
    total_contributions = 0

    for participant in participants:
        contributions = Contribution.objects.filter(participant=participant)
        participant_total = sum(c.amount for c in contributions)
        contributions_by_participant[participant.id] = {
            "participant": participant,
            "contributions": contributions,
            "total": participant_total,
        }
        total_contributions += participant_total

    # Calculate expenses
    total_expenses = sum(expense.amount for expense in expenses)
    remaining_fund = total_contributions - total_expenses

    # Calculate balances
    balances = {}
    for participant in participants:
        # Sum of all contributions
        contributions = Contribution.objects.filter(participant=participant)
        contributed_total = sum(c.amount for c in contributions)

        # Expenses they paid
        paid_expenses = Expense.objects.filter(trip=trip, paid_by=participant)
        paid_total = sum(expense.amount for expense in paid_expenses)

        # Their share of expenses
        shares = ExpenseShare.objects.filter(participant=participant)
        share_total = sum(share.amount for share in shares)

        # Calculate balance: contributions - shares + paid - share_total
        # Positive means they should receive money, negative means they owe
        balance = contributed_total + paid_total - share_total

        balances[participant.id] = {
            "participant": participant,
            "contributed": contributed_total,
            "paid": paid_total,
            "shares": share_total,
            "balance": balance,
        }

    return render(
        request,
        "view_group_trip.html",
        {
            "trip": trip,
            "expenses": expenses,
            "participants": participants,
            "contributions_by_participant": contributions_by_participant,
            "balances": balances,
            "total_contributions": total_contributions,
            "total_expenses": total_expenses,
            "remaining_fund": remaining_fund,
        },
    )


@login_required
def remove_participant(request, trip_id, participant_id):
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    participant = get_object_or_404(TripParticipant, id=participant_id, trip=trip)

    # Don't allow removing the trip owner
    if participant.user != request.user:
        if request.method == "POST":
            # Remove their contributions
            Contribution.objects.filter(participant=participant).delete()

            # Remove their expense shares
            ExpenseShare.objects.filter(participant=participant).delete()

            # Reassign their expenses to the trip owner if needed
            owner_participant = TripParticipant.objects.get(
                trip=trip, user=request.user
            )
            Expense.objects.filter(paid_by=participant).update(
                paid_by=owner_participant
            )

            # Finally remove the participant
            participant.delete()

            messages.success(request, _("Participant has been removed from the trip."))

    return redirect("manage_participants", trip_id=trip.id)


@login_required
def edit_participant(request, trip_id, participant_id):
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    participant = get_object_or_404(TripParticipant, id=participant_id, trip=trip)

    # Don't allow editing self (trip owner)
    if participant.user == request.user:
        messages.error(request, _("You cannot edit your own participant data."))
        return redirect("manage_participants", trip_id=trip.id)

    if request.method == "POST":
        # Update user data
        user = participant.user
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)

        email = request.POST.get("email")
        if email and email != user.email:
            # Check if email is already used by another user
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(
                    request, _("This email is already in use by another user.")
                )
                return redirect("manage_participants", trip_id=trip.id)
            user.email = email

        user.save()

        # Update participant data
        shares = request.POST.get("shares")
        if shares and shares.isdigit() and int(shares) > 0:
            participant.shares = int(shares)
            participant.save()

            # Recalculate expense shares if shares change
            expenses = Expense.objects.filter(trip=trip, is_shared=True)
            for expense in expenses:
                # Get all participants sharing this expense
                expense_shares = ExpenseShare.objects.filter(expense=expense)
                participants_sharing = [share.participant for share in expense_shares]

                if participant in participants_sharing:
                    # Recalculate total shares
                    total_shares = sum(p.shares for p in participants_sharing)

                    # Calculate share per unit
                    share_per_unit = expense.amount / total_shares

                    # Update all shares for this expense
                    for p in participants_sharing:
                        share = ExpenseShare.objects.get(expense=expense, participant=p)
                        share.amount = share_per_unit * p.shares
                        share.save()

        messages.success(request, _("Participant information updated successfully."))

    return redirect("manage_participants", trip_id=trip.id)
