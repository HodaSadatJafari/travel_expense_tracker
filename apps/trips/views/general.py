from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from apps.trips.forms.group import EditTripForm
from apps.trips.models import Trip


@login_required
def delete_trip(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)

    if request.method == "POST":
        trip.delete()
        messages.success(request, _("Trip has been deleted successfully."))
        return redirect("dashboard")

    return render(request, "delete_trip.html", {"trip": trip})


@login_required
def edit_trip(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)

    if request.method == "POST":
        form = EditTripForm(request.POST, instance=trip)
        if form.is_valid():
            form.save()
            messages.success(request, _("Trip details have been updated."))
            if trip.is_group_trip:
                return redirect("view_group_trip", trip_id=trip.id)
            else:
                return redirect("view_trip", trip_id=trip.id)
    else:
        form = EditTripForm(instance=trip)

    return render(request, "edit_trip.html", {"form": form, "trip": trip})
