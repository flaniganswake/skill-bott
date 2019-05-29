from django.template.defaultfilters import register


@register.filter(name='lookup')
def lookup(dict, index):

    # make sure index is string
    index = str(index)
    if index in dict:
        return dict[index]

    return -1
