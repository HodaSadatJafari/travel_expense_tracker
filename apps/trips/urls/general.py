from django.urls import path

from apps.trips.views.general import delete_trip, edit_trip

urlpatterns = [
    # Edit and delete trips
    path("<int:trip_id>/edit/", edit_trip, name="edit_trip"),
    path("<int:trip_id>/delete/", delete_trip, name="delete_trip"),
]
