"""
person/urls.py
"""

from django.urls import path
from person.views import main

urlpatterns = [
    path("", main),
]
