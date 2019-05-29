import os
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.db import connection
from .models import Page


def view_page(request, title):

    cms_page = get_object_or_404(Page, title=title)
    context = {'page': cms_page}
    return render(request, 'cms_page.html', context=context)