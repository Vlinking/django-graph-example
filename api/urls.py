# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views


urlpatterns = [
    # API
    url(r'^get_products_set/(?P<warehouse>\w+)/$',
        views.ProductsSetView.as_view()),
]



graph = {
    'A': {'E': 1, 'B': 3},
    'B': {'A': 3, 'C': 4, 'D': 2},
    'C': {'B': 4, 'D': 8, 'E': 2},
    'D': {'B': 2, 'C': 8},
}