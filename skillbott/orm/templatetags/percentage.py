from django import template

register = template.Library()


@register.filter
def percentage(decimal):

    return "%s%%" % int(decimal*100)
