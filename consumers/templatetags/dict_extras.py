# consumers/templatetags/dict_extras.py

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Usage in template: {{ my_dict|get_item:key }}
    """
    return dictionary.get(key)