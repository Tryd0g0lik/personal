"""
project/urls_api.py
"""

from django.urls import path, include
from person.urls_api import urlpatterns as person_api

urlpatterns = [
    path("person/", include(person_api)),
]
