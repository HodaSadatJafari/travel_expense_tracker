from django.urls import path

from apps.expenses.views.general import delete_expense, edit_expense
from apps.expenses.views.group import add_contribution, add_group_expense

urlpatterns = [
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
    # Expense management
    path(
        "group-trip/<int:trip_id>/expense/<int:expense_id>/edit/",
        edit_expense,
        name="edit_expense",
    ),
    path(
        "group-trip/<int:trip_id>/expense/<int:expense_id>/delete/",
        delete_expense,
        name="delete_expense",
    ),
]
