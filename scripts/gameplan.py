#!/usr/bin/env python3
import sys
import os
import re
import time
import string
import urllib
from skillbott.orm.models import Topic


sys.path.insert(0, os.getcwd().replace('/scripts', ''))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

tagged_topics = [
    1, 2, 3, 11, 12, 13, 23, 24, 25, 30, 31, 32, 39,
    40, 41, 57, 59, 61, 64, 65, 66, 71, 72, 73, 87, 88, 89, 109,
    110, 111, 113, 114, 117, 134, 135, 141, 147, 149, 152, 164,
    166, 172, 177, 179, 180, 185, 187, 188, 214, 216, 218, 224,
    225, 229, 234, 238, 240, 254, 255, 261, 284, 285, 287, 294,
    296, 300, 326, 327, 328, 329, 331, 333, 334, 335, 337,338,
    341, 343, 354, 355, 358, 360, 361, 363, 365, 366, 367, 370,
    371, 372, 374, 375, 376, 380, 381, 383, 404, 407, 408, 409,
    412, 413, 414, 415, 416, 417, 418, 419, 424, 425, 426, 427,
    430, 433, 444, 445, 446, 449, 450, 453, 474, 476, 477, 478,
    479, 481, 484, 486, 487, 488, 491, 493]

topics = Topic.objects.filter(pk__in=tagged_topics)
for topic in topics:
    topic.tags.add("gameplan")
    print(topic.name)
    topic.save()
print
print('Tagged topics: %d' % len(topics))
sys.exit(0)
