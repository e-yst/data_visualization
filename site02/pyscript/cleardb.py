#!/usr/bin/env python3.4

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'site02.settings'

import django
django.setup()

from main.models import Thread, Post

t_len = Thread.objects.all().count()
Thread.objects.all().delete()
print(t_len, 'Thread objects have been removed!')

p_len = Post.objects.all().count()
print(p_len)
Post.objects.all().delete()
print(p_len, 'Post objects have been removed!')
