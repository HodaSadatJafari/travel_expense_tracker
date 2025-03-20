from django.urls import path
from . import views

urlpatterns = [
    path("", views.my_trips, name="my_trips"),
    path("add/", views.add_trip, name="add_trip"),
    path("<int:trip_id>/", views.view_trip, name="view_trip"),
]
