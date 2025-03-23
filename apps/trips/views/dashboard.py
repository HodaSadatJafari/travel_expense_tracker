from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from apps.trips.models import Trip


@login_required
def dashboard(request):
    from django.utils import timezone

    # Get all individual trips
    individual_trips = Trip.objects.filter(user=request.user, is_group_trip=False)

    # Get all group trips where user is either owner or participant
    group_trips_owned = Trip.objects.filter(user=request.user, is_group_trip=True)
    group_trips_participating = Trip.objects.filter(
        participants__user=request.user, is_group_trip=True
    ).exclude(user=request.user)

    return render(
        request,
        "dashboard.html",
        {
            "individual_trips": individual_trips,
            "group_trips_owned": group_trips_owned,
            "group_trips_participating": group_trips_participating,
            "today": timezone.now().date(),
        },
    )
