from django.urls import path

from apps.expenses.views.general import edit_expense, delete_expense


urlpatterns = [
    path(
        "trip/<int:trip_id>/expense/<int:expense_id>/edit/",
        edit_expense,
        name="edit_solo_expense",
    ),
    path(
        "group/<int:trip_id>/expense/<int:expense_id>/delete/",
        delete_expense,
        name="delete_expense",
    ),
]
