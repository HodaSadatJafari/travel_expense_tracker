from django.urls import path

from apps.trips.views.solo import add_solo_trip, view_solo_trip

urlpatterns = [
    # solo trips
    path(
        "solo/add/",
        add_solo_trip,
        name="add_solo_trip",
    ),
    path(
        "solo/<int:trip_id>/",
        view_solo_trip,
        name="view_solo_trip",
    ),
]
