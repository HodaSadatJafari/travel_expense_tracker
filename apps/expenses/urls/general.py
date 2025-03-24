from django.urls import path

from apps.expenses.views.general import delete_expense, edit_expense, add_expense

urlpatterns = [
    path(
        "<int:trip_id>/expense/<int:expense_id>/edit/",
        edit_expense,
        name="edit_expense",
    ),
    path(
        "<int:trip_id>/expense/<int:expense_id>/delete/",
        delete_expense,
        name="delete_expense",
    ),
    path(
        "<int:trip_id>/expense/add/",
        add_expense,
        name="add_expense",
    ),
]
