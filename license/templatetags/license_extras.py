from django import template

register = template.Library()

@register.filter
def divisor(value, arg):
    """Calculate percentage"""
    try:
        if arg == 0:
            return 0
        return (value / arg) * 100
    except (ValueError, ZeroDivisionError):
        return 0