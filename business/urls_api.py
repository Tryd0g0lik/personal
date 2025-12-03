from django.urls import path, include
from rest_framework.routers import DefaultRouter

from business.views_business import BusinessViewSet

router = DefaultRouter()
router.register(r"order", BusinessViewSet, basename="business")
urlpatterns = [
    path("", include(router.urls), name="business_api"),
]
