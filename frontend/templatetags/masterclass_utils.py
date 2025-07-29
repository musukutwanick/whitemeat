"""
Custom template filters for masterclass schedule.
"""

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, [])


@register.simple_tag
def masterclass_dummy_tag():
    return "dummy"
