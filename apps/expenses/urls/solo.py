from django.urls import path

from apps.expenses.views.general import delete_expense, edit_expense
from apps.expenses.views.solo import add_expense

urlpatterns = [
    path(
        "<int:trip_id>/add_expense/",
        add_expense,
        name="add_expense",
    ),
    path(
        "trip/<int:trip_id>/expense/<int:expense_id>/edit/",
        edit_expense,
        name="edit_expense",
    ),
    path(
        "trip/<int:trip_id>/expense/<int:expense_id>/delete/",
        delete_expense,
        name="delete_expense",
    ),
]
