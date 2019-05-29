from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.urls import reverse
from django.template.defaultfilters import slugify
import urllib


class Page(models.Model):

    title = models.CharField(max_length=200)
    content = models.TextField()
    slug = models.SlugField()

    def __unicode__(self):
        return u'%s' % (self.title)