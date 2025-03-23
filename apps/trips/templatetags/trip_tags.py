from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def sum_expenses(expenses):
    """Sum the amount of all expenses"""
    if not expenses:
        return 0
    return sum(expense.amount for expense in expenses)


@register.simple_tag
def get_today():
    """Return today's date"""
    from django.utils import timezone

    return timezone.now().date()
