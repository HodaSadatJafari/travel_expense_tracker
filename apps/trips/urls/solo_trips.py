from django.urls import path

from apps.trips.views.solo_trips import add_trip, view_trip, add_expense

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
    path(
        "<int:trip_id>/add_expense/",
        add_expense,
        name="add_expense",
    ),
]
