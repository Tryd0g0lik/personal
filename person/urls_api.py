from django.urls import path, include
from rest_framework.routers import DefaultRouter

from person.views_api.views_person_api import UserViews, ProfileViewSet

router = DefaultRouter()
router.register(r"users", UserViews, basename="persons")
urlpatterns = [
    path("", include(router.urls), name="persons_api"),
    path(
        "0/active/",
        ProfileViewSet.as_view({"patch": "active"}),
        name="person_active",
    ),
]
