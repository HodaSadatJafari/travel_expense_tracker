from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.core.models.users import CustomUser
from django.db.models import F, Q, Sum
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _

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
            if CustomUser.objects.filter(email=email).exclude(id=user.id).exists():
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


@login_required
def view_group_trip(request, trip_id):
    """
    View function for displaying a group trip with expense calculations,
    participant balances, and settlement instructions.
    """
    trip = get_object_or_404(Trip, id=trip_id)

    # Check if user is a participant in this trip
    try:
        user_participant = trip.participants.get(user=request.user)
    except TripParticipant.DoesNotExist:
        messages.error(request, _("You are not a participant in this trip."))
        return redirect("dashboard")  # Or wherever you want to redirect

    # Get all participants
    participants = trip.participants.all()

    # Get all expenses for this trip
    expenses = Expense.objects.filter(trip=trip).order_by("-date")
    group_expenses = expenses.filter(paid_from_group_fund=True)
    individual_expenses = expenses.filter(paid_from_group_fund=False)

    # Get contributions to the group fund
    contributions = Contribution.objects.filter(participant__trip=trip)
    total_contributions = contributions.aggregate(Sum("amount"))[
        "amount__sum"
    ] or Decimal("0.00")

    # Calculate group expenses total
    group_expenses_total = group_expenses.aggregate(Sum("amount"))[
        "amount__sum"
    ] or Decimal("0.00")

    # Calculate remaining fund
    remaining_fund = total_contributions - group_expenses_total

    # Calculate data for each participant
    participant_data = {}

    for participant in participants:
        # Participant's contributions to the group fund
        participant_contributions = contributions.filter(participant=participant)
        contributed = participant_contributions.aggregate(Sum("amount"))[
            "amount__sum"
        ] or Decimal("0.00")

        # Calculate participant's share of group expenses based on actual expense shares
        group_expenses_share = Decimal("0.00")

        for expense in group_expenses:
            if expense.is_shared:
                # Get all shares for this particular expense
                expense_shares = ExpenseShare.objects.filter(expense=expense)

                if expense_shares.exists():
                    # If specific shares exist, use the participant's actual share
                    try:
                        # Use the participant's direct share amount if it exists
                        participant_share = expense_shares.get(
                            participant=participant
                        ).amount
                        group_expenses_share += participant_share
                    except ExpenseShare.DoesNotExist:
                        # This participant isn't sharing this expense
                        participant_share = Decimal("0.00")
                else:
                    # If no specific shares exist but expense is marked as shared,
                    # divide among all participants based on shares ratio
                    total_shares = sum(p.shares for p in participants)
                    participant_share_ratio = Decimal(participant.shares) / Decimal(
                        total_shares
                    )
                    participant_share = participant_share_ratio * expense.amount
                    group_expenses_share += participant_share
            else:
                # If expense is not shared, no one bears the cost
                # This case shouldn't typically happen for group expenses
                participant_share = Decimal("0.00")

        # Calculate fund balance (contributions minus share of group expenses)
        fund_balance = contributed - group_expenses_share
        # Individual expenses paid by this participant
        paid_expenses = individual_expenses.filter(paid_by=participant)

        # Calculate details for expenses paid by this participant
        expenses_paid_for_others = []
        paid_personally_total = Decimal("0.00")  # Total amount paid
        others_owe_total = Decimal("0.00")  # Amount others owe to this participant

        for expense in paid_expenses:
            if expense.is_shared:
                # Get all shares for this expense
                expense_shares = ExpenseShare.objects.filter(expense=expense)
                total_expense_shares = sum(
                    share.participant.shares for share in expense_shares
                )

                # Calculate participant's own share
                participant_expense_share = expense.amount * (
                    Decimal(participant.shares) / Decimal(total_expense_shares)
                )
                others_owe = expense.amount - participant_expense_share

                expenses_paid_for_others.append(
                    {
                        "date": expense.date,
                        "category": expense.category,
                        "get_category_display": expense.get_category_display(),
                        "description": expense.description,
                        "amount": expense.amount,
                        "your_share": participant_expense_share,
                        "for_others": others_owe,
                    }
                )

                paid_personally_total += expense.amount
                others_owe_total += others_owe
            else:
                # Personal expense (not shared)
                paid_personally_total += expense.amount

        # Get expenses this participant is sharing in (but didn't pay for)
        shared_expenses = (
            ExpenseShare.objects.filter(
                participant=participant,
            )
            .exclude(expense__paid_by=participant)
            .exclude(expense__paid_from_group_fund=True)
        )

        # Filter out group fund expenses for the "Owes to Others" tab
        individual_shared_expenses = []
        for share in shared_expenses:
            if (
                not share.expense.paid_from_group_fund
                and share.expense.paid_by is not None
            ):
                individual_shared_expenses.append(share)

        # Calculate how much this participant owes to others (only for individual expenses)
        owes_others_total = sum(share.amount for share in individual_shared_expenses)

        # Calculate personal balance (others owe minus owes others)
        personal_balance = others_owe_total - owes_others_total

        # Calculate net balance (fund balance + personal balance)
        balance = fund_balance + personal_balance

        # Store all the data for this participant
        participant_data[participant.id] = {
            "participant": participant,
            "contributed": contributed,
            "group_expenses_share": group_expenses_share,
            "fund_balance": fund_balance,
            "paid_personally": paid_personally_total,
            "personal_share": paid_personally_total
            - others_owe_total,  # What they actually consumed
            "personal_balance": personal_balance,
            "balance": balance,  # Net balance (fund + personal)
            "contributions": participant_contributions,
            "expenses_paid": paid_expenses,
            "expenses_paid_for_others": expenses_paid_for_others,
            "expenses_shared": shared_expenses,
            "individual_expenses_shared": individual_shared_expenses,  # Filtered for individual expenses only
            "others_owe": others_owe_total,
            "owes_others": owes_others_total,
            "group_expenses_shared": ExpenseShare.objects.filter(
                participant=participant, expense__paid_from_group_fund=True
            ),
        }

    # Calculate settlements
    settlements, detailed_settlements = calculate_settlements(participant_data)

    # Add detailed settlements to each participant's data
    for participant_id, person_settlements in detailed_settlements.items():
        if participant_id in participant_data:
            participant_data[participant_id][
                "detailed_settlements"
            ] = person_settlements

    context = {
        "trip": trip,
        "participants": participants,
        "expenses": expenses,
        "group_expenses": group_expenses,
        "individual_expenses": individual_expenses,
        "total_contributions": total_contributions,
        "group_expenses_total": group_expenses_total,
        "remaining_fund": remaining_fund,
        "participant_data": participant_data,
        "settlements": settlements,
    }

    return render(request, "view_group_trip.html", context)


def calculate_settlements(participant_data):
    """
    Calculate the optimal settlement plan to minimize the number of transactions.

    Args:
        participant_data: Dictionary with participant balances and details

    Returns:
        tuple: (settlements, detailed_settlements)
            - settlements: List of settlement instructions
            - detailed_settlements: Dict mapping participant IDs to their settlement details
    """
    # Extract net balances for each participant
    balances = {p_id: data["balance"] for p_id, data in participant_data.items()}

    # Create lists of debtors and creditors
    debtors = [(p_id, -balance) for p_id, balance in balances.items() if balance < 0]
    creditors = [(p_id, balance) for p_id, balance in balances.items() if balance > 0]

    # Sort by amount (descending)
    debtors.sort(key=lambda x: x[1], reverse=True)
    creditors.sort(key=lambda x: x[1], reverse=True)

    # Settlements to return
    settlements = []

    # Detailed settlements for each participant
    detailed_settlements = {p_id: [] for p_id in participant_data.keys()}

    # Match debtors with creditors to minimize transactions
    i, j = 0, 0
    while i < len(debtors) and j < len(creditors):
        debtor_id, debt = debtors[i]
        creditor_id, credit = creditors[j]

        # Skip if the amounts are essentially zero (floating point issues)
        if debt < Decimal("0.01") or credit < Decimal("0.01"):
            if debt < Decimal("0.01"):
                i += 1
            if credit < Decimal("0.01"):
                j += 1
            continue

        # Calculate the settlement amount
        amount = min(debt, credit)

        # Create the settlement record
        settlements.append(
            {
                "from_user": participant_data[debtor_id][
                    "participant"
                ].user.get_full_name()
                or participant_data[debtor_id]["participant"].user.username,
                "to_user": participant_data[creditor_id][
                    "participant"
                ].user.get_full_name()
                or participant_data[creditor_id]["participant"].user.username,
                "amount": amount,
            }
        )

        # Add to detailed settlements for each participant
        detailed_settlements[debtor_id].append(
            {
                "you_pay": True,
                "other_person": participant_data[creditor_id][
                    "participant"
                ].user.get_full_name()
                or participant_data[creditor_id]["participant"].user.username,
                "amount": amount,
            }
        )

        detailed_settlements[creditor_id].append(
            {
                "you_pay": False,
                "other_person": participant_data[debtor_id][
                    "participant"
                ].user.get_full_name()
                or participant_data[debtor_id]["participant"].user.username,
                "amount": amount,
            }
        )

        # Update the remaining balances
        debtors[i] = (debtor_id, debt - amount)
        creditors[j] = (creditor_id, credit - amount)

        # Move to next person if their balance is cleared
        if debt - amount < Decimal("0.01"):
            i += 1
        if credit - amount < Decimal("0.01"):
            j += 1

    return settlements, detailed_settlements
