from django.contrib import admin
from apps.expenses.models import ExpenseShare, Expense


class ExpenseShareAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "expense",
        "participant",
        "amount",
    ]


admin.site.register(ExpenseShare, ExpenseShareAdmin)
admin.site.register(Expense)
