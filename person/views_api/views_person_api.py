import asyncio
import logging
import re
from http.client import responses

from adrf import viewsets
from django.http import HttpRequest, HttpResponse
from drf_yasg.utils import swagger_auto_schema

from logs import configure_logging
from person.models import User
from django.contrib.auth.models import AnonymousUser
from person.models_person.serializers import UserSerializer
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import serializers, status

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


class UserViews(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_description="""
                    Четыре обязательных поля. Пароли сверяются на стороне сервера. Если пользователь заполняет\
                    форму эдентичными паролями, значит пароль шифруется и сохраняется. Иначе возвращяем 404 статус код.
                    Method: POST and the fixed pathname of '/api/auth/person/'\
                    Example PATHNAME: "{{url_base}}/api/auth/person/"\
                    @param: str email - обязательное значение.\
                    @param: str password_confirm - обязательное значение.\
                    @param: str password - обязательное значение.\
                    @param: str role - обязательное значение.  От роли зависят ограничения профиля.\

                    """,
        manual_parameters=[
            openapi.Parameter(
                name="X-CSRFToken",
                title="X-CSRFToken",
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                example="nH2qGiehvEXjNiYqp3bOVtAYv....",
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            title="BodyData",
            in_=openapi.IN_FORM,
            required=["email", "password", "password_confirm", "role"],
            properties={
                "email": openapi.Schema(
                    example="<user_email>", type=openapi.TYPE_STRING
                ),
                "password_confirm": openapi.Schema(
                    example="nH2qGiehvEXjNiYqp3bOVtAYv....", type=openapi.TYPE_STRING
                ),
                "password": openapi.Schema(
                    example="nH2qGiehvEXjNiYqp3bOVtAYv....", type=openapi.TYPE_STRING
                ),
                "role": openapi.Schema(example="staff", type=openapi.TYPE_STRING),
                "username": openapi.Schema(example="Serge", type=openapi.TYPE_STRING),
                "first_name": openapi.Schema(example="null", type=openapi.TYPE_STRING),
                "last_login": openapi.Schema(example="null", type=openapi.TYPE_STRING),
            },
        ),
        responses={
            201: openapi.Response(
                description="Данные на выходе",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(
                            example="da7611fc-87f4-42aa-9019-956a8824f1cb",
                            type=openapi.TYPE_STRING,
                        ),
                        "email": openapi.Schema(
                            example="email@my.ry",
                            type=openapi.TYPE_STRING,
                        ),
                        "username": openapi.Schema(
                            example="nH2qGiehvEXjNiYqp3bOVtAYv....",
                            type=openapi.TYPE_STRING,
                        ),
                        "first_name": openapi.Schema(
                            type=openapi.TYPE_STRING, example=""
                        ),
                        "last_name": openapi.Schema(
                            type=openapi.TYPE_STRING, example="null"
                        ),
                        "last_login": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="2025-07-20 00:39:14.739 +0700",
                        ),
                        "is_superuser": openapi.Schema(
                            type=openapi.TYPE_BOOLEAN,
                            example=False,
                        ),
                        "is_staff": openapi.Schema(
                            type=openapi.TYPE_BOOLEAN,
                            example=False,
                            description="user got permissions how superuser or not.",
                        ),
                        "is_active": openapi.Schema(
                            type=openapi.TYPE_BOOLEAN,
                            example=False,
                        ),
                        "updated_at": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="2025-07-20 00:39:14.739 +0700",
                        ),
                        "created_at": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="2025-07-20 00:39:14.739 +0700",
                        ),
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="-------",
                        ),
                    },
                ),
            ),
            401: "Not Ok",
            500: "Something what wrong. Read the response variable 'data'",
        },
        tags=["person"],
    )
    async def create(self, request: Request, *args, **kwargs) -> Response:
        """
        This method has 4 required of variables. It's : "mail', 'password', 'password_confirm', "role".
        THe 'role' has a following values: "staff", "admin", "user", "visitor", "superuser".
        In moment of registration, we fill the username's field by the text from the email address.
        TODO: добоавить токен
        :param request:
        :return:
        """
        text_log = "[%s.%s]:" % (self.__class__.__name__, self.create.__name__)
        user = request.user if request.user else AnonymousUser()
        data = request.data
        response = Response()
        if user.is_anonymous:
            try:
                # CHECK - VALID DATA
                serializer = self.serializer_class(data=data)
                is_valid = await asyncio.to_thread(serializer.is_valid)
                if is_valid:
                    await serializer.asave()
                    text_log += " User created successful."
                    log.info(text_log)
                    response.status_code = status.HTTP_200_OK
                    response_data = await asyncio.to_thread(lambda: serializer.data)
                    response_data.pop("password")
                    response.data = {"data": response_data}
                    return response
                text_log += " User created failed."
                log.info(text_log)
                response.data = {"data": "User creates failed."}
                response.status_code = status.HTTP_401_UNAUTHORIZED
                return response
            except Exception as error:
                text_log += f"ERROR => {error.args[0]}"
                log.error(text_log)
                response.data = {"errors": text_log}
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return response
        text_log += " User was activated before this."
        log.info(text_log)
        response.data = {"data": text_log}
        return response

    async def list(self, request: Request, *args, **kwargs) -> Response:
        response = await super().alist(*args, **kwargs)
        if isinstance(response.data, list):
            response.data[0].pop("password")
        if isinstance(response.data, dict):
            response.data.pop("password")
        return response

    async def retrieve(self, request: Request, *args, **kwargs) -> Response:
        response = await super().aretrieve(request, *args, **kwargs)
        pass
        if isinstance(response.data, list):
            response.data[0].pop("password")
        if isinstance(response.data, dict):
            response.data.pop("password")
        return response
