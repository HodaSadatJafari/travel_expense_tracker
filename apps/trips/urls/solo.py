from django.urls import path

from apps.trips.views.solo import add_trip, view_trip

urlpatterns = [
    # solo trips
    path(
        "add/",
        add_trip,
        name="add_trip",
    ),
    path(
        "<int:trip_id>/",
        view_trip,
        name="view_trip",
    ),
]
