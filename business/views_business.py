"""
business/views_business.py
"""

import logging
import re
from typing import Optional

from django.apps import apps
from adrf import viewsets
from drf_yasg import openapi
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.request import Request

from logs import configure_logging
from person.permissions import is_active, is_all, is_managerOrAdmin
from person.views_api.serializers import BusinessSerializer

log = logging.getLogger(__name__)
configure_logging(logging.INFO)

BusinessElementModel = apps.get_model("person", "BusinessElementModel")


class DashboardViewSet(viewsets.ModelViewSet):
    queryset = BusinessElementModel.objects.all()
    serializer_class = BusinessSerializer

    @swagger_auto_schema(
        # operation_description="""
        #
        #                 """,
        manual_parameters=[
            openapi.Parameter(
                name="id",
                title="Pathname",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                example="c4ebb722-930d-4ad9-ad1e-237eb4b41c70",
            ),
            openapi.Parameter(
                name="X-CSRFToken",
                title="CSRF Token",
                required=["X-CSRFToken"],
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                example="nH2qGiehvEXjNiYqp3bOVtAYv....",
            ),
            openapi.Parameter(
                name="access_token",
                title="Access Token",
                type=openapi.TYPE_STRING,
                required=["access_token"],
                in_="cookie",
                description="JWT Access Token",
                example="nH2qGiehvEXjNiYqp3bOVtAYv....",
            ),
            openapi.Parameter(
                name="refresh_token",
                title="Refresh Token",
                type=openapi.TYPE_STRING,
                required=["refresh_token"],
                in_="cookie",
                description="JWT Refresh Token",
                example="nH2qGiehvEXjNiYqp3bOVtAYv....",
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            title="BodyData",
            in_=openapi.IN_FORM,
            required=[
                "name",
            ],
            properties={
                "name": openapi.Schema(
                    example="<user_email>", type=openapi.TYPE_STRING
                ),
                "descriptions": openapi.Schema(
                    example="Text about descriptions ....", type=openapi.TYPE_STRING
                ),
            },
        ),
        responses={
            201: "OK",
            401: "Not Ok",
            500: "Something what wrong. Read the response variable 'data'",
        },
        tags=["business"],
    )
    async def acreate(self, request: Request, *args, **kwargs) -> Response:
        text_log = "[%s.%s]:" % (self.__class__.__name__, self.acreate.__name__)
        response = Response()
        if not is_active(request):
            text_log += " Your accout needs to be activated"
            log.info(text_log)
            response.status_code = status.HTTP_401_UNAUTHORIZED
            response.data = {"data", text_log}
            return response
        try:
            if is_managerOrAdmin(request):
                response = await super().acreate(request, *args, **kwargs)
                response.status_code = status.HTTP_201_CREATED
                return response
            text_log += " Your accout needs to be activated"
            log.info(text_log)
            response.status_code = status.HTTP_401_UNAUTHORIZED
            response.data = {"data", "Not OK - you do not have sufficient rights"}
            return response
        except Exception as e:
            text_log += " ERROR => %s" % e.args[0]
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            response.data = {"data", text_log}
            return response

    async def alist(self, request: Request, *args, **kwargs) -> Response:
        """
        TODO: Можно реализовать выдачу списка для пагинации.
            В данный момент подаётся весь массив.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        text_log = "[%s.%s]:" % (self.__class__.__name__, self.alist.__name__)
        response = Response()
        if not is_active(request):
            text_log += " Your accout needs to be activated"
            log.info(text_log)
            response.status_code = status.HTTP_401_UNAUTHORIZED
            response.data = {"data", text_log}
            return response
        try:
            if is_managerOrAdmin(request):
                response = await super().alist(request, *args, **kwargs)
                response.status_code = status.HTTP_201_CREATED
                return response
            text_log += " Your accout needs to be activated"
            log.info(text_log)
            response.status_code = status.HTTP_401_UNAUTHORIZED
            response.data = {"data", "Not OK - you do not have sufficient rights"}
            return response
        except Exception as e:
            text_log += " ERROR => %s" % e.args[0]
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            response.data = {"data", text_log}
            return response
