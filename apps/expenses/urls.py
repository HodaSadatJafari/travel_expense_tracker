from django.urls import path
from . import views

urlpatterns = [
    path("trip/<int:trip_id>/add_expense/", views.add_expense, name="add_expense"),
]
