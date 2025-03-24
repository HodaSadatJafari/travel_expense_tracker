from django.urls import path

from apps.expenses.views.group import add_contribution

urlpatterns = [
    path(
        "group/<int:trip_id>/contribution/add/",
        add_contribution,
        name="add_contribution",
    ),
]
