from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("add/", views.add_trip, name="add_trip"),
    path("<int:trip_id>/", views.view_trip, name="view_trip"),
]
