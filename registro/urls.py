#-*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from .views import *

from django.contrib.auth.decorators import login_required
perm = login_required

urlpatterns = patterns('',
    url(r'^(?P<year>\w+)/(?P<month>\w+)$', perm(VistaMes.as_view()), name='dia_ym'),
    url(r'^(?P<year>\w+)/(?P<month>\w+)/(?P<day>\w+)$', perm(VistaDia.as_view()), name='dia_ymd'),
    url(r'^$', perm(RedirectDia.as_view()), name='home'),
)
