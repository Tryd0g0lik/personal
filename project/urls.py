"""
project/urls.py
"""

from django.contrib import admin
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from django.conf.urls.static import static
from django.views.generic import TemplateView
from project import settings
from project.urls_api import urlpatterns as api_person
from person.urls import urlpatterns as urls_person


schema_view = get_schema_view(
    openapi.Info(
        title="API for WINK",
        url="http://127.0.0.1:8000/api/v1",
        description="""none""",
        default_version="v1",
        service_identity=False,
        contact=openapi.Contact(email="work80@mail.ru"),
    ),
    public=True,
    permission_classes=[AllowAny],
    patterns=[
        path("api/v1/", include((api_person, "api_v1"), namespace="api_v1")),
    ],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include((urls_person, "persons"), namespace="persons")),
    path("api/v1/", include((api_person, "api_v1"), namespace="api_v1")),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger"),
    path(
        "swagger<format>/",
        schema_view.without_ui(cache_timeout=0),
        name="swagger-format",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="redoc"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("pages/", include(wagtail_urls)),
    re_path(
        r"^(?!static/|media/|api/|admin/|redoc/|swagger/).*",
        TemplateView.as_view(template_name="index.html"),
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
