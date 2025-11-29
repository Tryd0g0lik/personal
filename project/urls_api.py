"""
project/urls_api.py
"""

from django.urls import path, include
from person.urls_api import urlpatterns as person_api
from person.views import CSRFTokenView

urlpatterns = [
    path("person/", include(person_api)),
    path("auth/csrftoken/", CSRFTokenView.as_view(), name="token_obtain_pair"),
]
