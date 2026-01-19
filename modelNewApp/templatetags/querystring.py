from django import template

register = template.Library()

@register.simple_tag
def querystring(get_params, key, value):
    params = get_params.copy()
    params[key] = value
    return params.urlencode()
