from django import template

register = template.Library()

@register.filter
def mul10(value):
    return value * 10

@register.filter
def lstrip(value, chars):
    return value.lstrip(chars)

@register.filter
def strip(value):
    return value.strip()
