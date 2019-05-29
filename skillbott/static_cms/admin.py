import sys
import os
from .models import Page
from django.contrib import admin


#sys.path.insert(0, os.getcwd().replace('/static_cms', ''))
#os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'content',)
    exclude = ('slug',)

admin.site.register(Page, PageAdmin)