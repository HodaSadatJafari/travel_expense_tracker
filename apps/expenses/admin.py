from django.contrib import admin

from apps.expenses.models import Expense, ExpenseShare


class ExpenseShareAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "expense",
        "participant",
        "amount",
    ]


admin.site.register(ExpenseShare, ExpenseShareAdmin)
admin.site.register(Expense)
