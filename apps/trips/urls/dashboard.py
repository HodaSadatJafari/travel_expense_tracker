from django.urls import path

from apps.trips.views.dashboard import dashboard

urlpatterns = [
    path(
        "dashboard",
        dashboard,
        name="dashboard",
    ),
]
