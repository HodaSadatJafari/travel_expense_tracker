from django.urls import path

from apps.trips.views.group import (add_group_trip, edit_participant,
                                    manage_participants, remove_participant,
                                    view_group_trip)

urlpatterns = [
    path(
        "group/add/",
        add_group_trip,
        name="add_group_trip",
    ),
    path(
        "group/<int:trip_id>/participants/",
        manage_participants,
        name="manage_participants",
    ),
    path(
        "group/<int:trip_id>/",
        view_group_trip,
        name="view_group_trip",
    ),
    # Participant management
    path(
        "group/<int:trip_id>/participants/remove/<int:participant_id>/",
        remove_participant,
        name="remove_participant",
    ),
    path(
        "group/<int:trip_id>/participants/edit/<int:participant_id>/",
        edit_participant,
        name="edit_participant",
    ),
]
