from django import template

register = template.Library()

@register.filter(name='pluck')
def pluck(queryset, attr):
    return [getattr(obj, attr, None) for obj in queryset]
