from django import template

register = template.Library()

@register.filter
def dict_content(dict, key):
    return dict[key]
