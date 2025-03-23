from django.urls import path

from apps.expenses.views.general import delete_expense, edit_expense
from apps.expenses.views.solo import add_solo_expense

urlpatterns = [
    path(
        "solo/<int:trip_id>/expense/add/",
        add_solo_expense,
        name="add_solo_expense",
    ),
]
