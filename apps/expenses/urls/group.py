from django.urls import path

from apps.expenses.views.general import delete_expense, edit_expense
from apps.expenses.views.group import add_contribution, add_group_expense

urlpatterns = [
    path(
        "group/<int:trip_id>/expense/add/",
        add_group_expense,
        name="add_group_expense",
    ),
    path(
        "group/<int:trip_id>/contribution/add/",
        add_contribution,
        name="add_contribution",
    ),
]
