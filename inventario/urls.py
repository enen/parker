# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from . import views as v

urlpatterns = patterns(
    '',
    url(r'^tarifas$', v.Tarifas.as_view(), name="tarifas"),
    url(r'^barrera/(?P<slug>\w+)/(?P<comando>\w+)$', v.BarreraComando.as_view(), name="barrera_comando"),
)
