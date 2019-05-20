import math

from django import template
from django.utils.http import urlencode
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def get_item(d, k):
    return d.get(k)

@register.filter(name='floor')
def floor(num):
    try:
        outcome = math.floor(num)
    except TypeError:
        return '0'

    return outcome

@register.filter(name='roundTo10')
def roundTo10(num):
    try:
        outcome = round(num / 10) * 10
    except TypeError:
        return num

    return outcome

@register.filter(name='rename_none')
def rename_none(d):
    if d is None:
        return '-'
    return d
