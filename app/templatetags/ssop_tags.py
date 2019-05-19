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
    if num is None:
        return '0'

    return math.floor(num)
