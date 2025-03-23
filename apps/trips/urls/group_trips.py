from django.urls import path

from apps.trips.views.group_trips import (
    add_contribution,
    add_group_expense,
    create_group_trip,
    manage_participants,
    view_group_trip,
)

urlpatterns = [
    path(
        "group-trip/add/",
        create_group_trip,
        name="create_group_trip",
    ),
    path(
        "group-trip/<int:trip_id>/participants/",
        manage_participants,
        name="manage_participants",
    ),
    path(
        "group-trip/<int:trip_id>/contribution/add/",
        add_contribution,
        name="add_contribution",
    ),
    path(
        "group-trip/<int:trip_id>/expense/add/",
        add_group_expense,
        name="add_group_expense",
    ),
    path(
        "group-trip/<int:trip_id>/",
        view_group_trip,
        name="view_group_trip",
    ),
]
