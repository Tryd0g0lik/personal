"""
person/views_api/views_person_api.py
"""

import asyncio
import logging

from adrf import viewsets

from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from logs import configure_logging
from person.models import User
from django.contrib.auth.models import AnonymousUser

from person.models_person.model_black import BlackListModel
from person.permissions import is_all, is_active, is_owner
from person.views_api.serializers import UserSerializer, ProfileSerializer
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status, authentication

from project.cookies import Cookies
from project.settings import IS_SUPERUSER, IS_ADMIN

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


class UserViews(viewsets.ModelViewSet):
    """
    TODO: Сделать обновление токена.
        Логика обновления JWT реализована в 'person/jwt'.
        Обновление JWT токена разместить в API.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    # authentication_classes = [authentication.SessionAuthentication]
    # permission_classes = [IsAuthenticated]

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
            201: "OK",
            401: "Not Ok",
            500: "Something what wrong. Read the response variable 'data'",
        },
        tags=["person"],
    )
    async def create(self, request: Request, *args, **kwargs) -> Response:
        """
        This method has 4 required of variables. It's : "mail', 'password', 'password_confirm', "role".
        THe 'role' has a following values: "staff", "admin", "user", "visitor", "superuser".

        If the field of role does not has the name - "user" or "visitor", it means a user has permission from the staff
        In moment of registration:
         - we fill the username's field - the text from the email address;
         - user is adding to the group. Group name is formed as a "< Rolename >_group";
         - the 'superuser' could be only one/single useer.
         The 'superuser' has a quantity only 1 - by the default value.
         The 'admin' has a quantity before 4 - by default value.
         We can change this quantity in the '.env' file. It's variable 'IS_ADMIN' & 'IS_SUPERUSER'.
        "visitor" - this is Anonymous. His does not has the access.
        "user" -  user allows access for - reade and create.


        :param request:
        :return:
        """
        from django.contrib.auth.models import Group
        from rest_framework import status

        text_log = "[%s.%s]:" % (self.__class__.__name__, self.create.__name__)
        user = request.user if request.user else AnonymousUser()
        data = request.data
        role = data.get("role")
        response = Response()
        response.status_code = status.HTTP_403_FORBIDDEN
        if user.is_anonymous or is_all(request) or user.is_admin:
            try:
                text_log += " User created failed."
                log.info(text_log)
                response.data = {"data": "User creates failed."}

                # CHECK - VALID DATA
                # is staff
                serializer = self.serializer_class(data=data)
                is_valid = await asyncio.to_thread(serializer.is_valid)
                if is_valid:
                    # ==== USER ====
                    # User is creating
                    await serializer.asave()
                    u = await asyncio.to_thread(
                        lambda: User.objects.get(email=data["email"])
                    )
                    # ==== GROUP & ROLE ====
                    # THis is , where is the user added in a group (and a group is creating or created)
                    rl = f"{role}_group".capitalize()
                    g, is_true = await Group.objects.aget_or_create(name=rl)
                    await u.groups.aadd(g)
                    # This is, where user get the permission as a staff
                    is_staff = role not in ["user", "visitor"]
                    u.is_staff = is_staff

                    if role == "superuser":
                        # Check - the superuser was created before or nor
                        superuser_list = await asyncio.to_thread(
                            lambda: User.objects.filter(is_superuser=True)
                        )
                        # The 'superuser' could be only one/single useer.
                        if len(superuser_list) == int(IS_SUPERUSER):
                            return response
                    elif role == "admin":
                        # Check the quantity of 'admin'
                        admin_list = await asyncio.to_thread(
                            lambda: User.objects.filter(is_admin=True)
                        )
                        # The 'superuser' could be only one/single useer.
                        if len(admin_list) == int(IS_ADMIN):
                            return response

                    await u.asave()

                    response.data = {"data": "User created successfully"}
                    response.status_code = status.HTTP_201_CREATED
                    return response
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
        text_log = "[%s.%s]:" % (self.__class__.__name__, self.list.__name__)
        if not is_active(request):
            response = Response()
            text_log += " Your accout needs to be activated"
            log.info(text_log)
            response.status_code = status.HTTP_401_UNAUTHORIZED
            response.data = {"data", text_log}
            return response
        if not is_all(request) or not request.user.is_admin:
            response = Response()
            text_log += "Not OK - you do not have sufficient rights"
            log.info(text_log)
            response.status_code = status.HTTP_401_UNAUTHORIZED
            response.data = {"data", text_log}
            return response
        response = await super().alist(*args, **kwargs)
        if isinstance(response.data, list):
            response.data[0].pop("password")
        if isinstance(response.data, dict):
            response.data.pop("password")
        return response

    async def update(self, request: Request, *args, **kwargs) -> Response:
        text_log = "[%s.%s]:" % (self.__class__.__name__, self.update.__name__)
        response = Response()
        if not is_active(request):
            text_log += " Your accout needs to be activated"
            log.info(text_log)
            response.status_code = status.HTTP_401_UNAUTHORIZED
            response.data = {"data", text_log}
            return response
        # FREEZING
        k = list(kwargs.keys())[0]
        v = list(kwargs.values())[0]
        u_list = User.objects.filter(k=v)
        if not await u_list.aexists():
            text_log += " Data was not found"
            log.info(text_log)
            response.status_code = status.HTTP_404_NOT_FOUND
            response.data = {"data", text_log}
            return response
        u = u_list.first()
        if is_owner(request, u) or request.user.is_admin or is_all(request):
            response = await super().aupdate(request, args, kwargs)

            return response
        text_log += " you do not have sufficient rights"
        log.info(text_log)
        response.status_code = status.HTTP_403_FORBIDDEN
        response.data = {"data", text_log}
        return response

    async def retrieve(self, request: Request, *args, **kwargs) -> Response:
        response = await super().aretrieve(request, *args, **kwargs)
        pass
        if isinstance(response.data, list):
            response.data[0].pop("password")
        if isinstance(response.data, dict):
            response.data.pop("password")
        return response

    @swagger_auto_schema(
        operation_description="""
        METHOD: DELETE.
        description: You wil can delete the user account only if is:
            - owner;
            - admin;
            - superuser;
        In the delete event, the user is added to the 'BlackListSerializer' db.
        Fully from the database - the user's account can only be deleted by a user with superuser or administrator rights.

        A window of time is likely needed to restore the account.

        Currently, the account is being returned to the user with the administrator's assistance.
        """,
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
        responses={
            200: "OK",
            401: "Not OK - you do not have sufficient rights",
            404: " User does not exist.",
            500: "IERROR => ...",
        },
        tags=["person"],
    )
    async def destroy(self, request: Request, *args, **kwargs) -> Response:
        """
        TODO: Прочитать 'TODO' из 'person.views_api.views_person_api.ProfileViewSet.active'
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        text_log = "[%s.%s]:" % (self.__class__.__name__, self.destroy.__name__)
        response = Response()
        if not is_active(request):
            text_log += " Your accout needs to be activated"
            log.info(text_log)
            response.status_code = status.HTTP_401_UNAUTHORIZED
            response.data = {"data", text_log}
            return response

        u_list = User.objects.filter(id=kwargs["pk"])
        u = await u_list.afirst()
        if not u:
            # Check a pk
            text_log += " User does not exist."
            log.info(text_log)
            response.status_code = status.HTTP_404_NOT_FOUND
            return response

        # FREEZING
        black_list = BlackListModel.objects.filter(email=u.email)
        if (
            not await black_list.aexists()
            and kwargs["pk"]
            and is_owner(request, u)
            or request.user.is_admin
        ):
            try:
                u = await User.objects.aget(id=kwargs["pk"])
                u.is_active = False
                b = BlackListModel(email=u.email)
                await u.asave(update_fields=["is_active"])
                await b.asave()
                response.data = {"data": "OK"}
                response.status_code = status.HTTP_200_OK
            except Exception as e:
                text_e = "%s ERROR => %s" % (text_log, e.args[0])
                log.error(text_e)
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                response.data = {"errors", text_e}
            return response
        elif await black_list.aexists() and (request.user.is_admin or is_all(request)):
            # DELETE
            try:
                await User.objects.filter(id=u.email).adelete()
                await BlackListModel.objects.get(email=u.email).adelete()
                response.data = {"data": "Removed successfully"}
                response.status_code = status.HTTP_200_OK
                return response
            except Exception as e:
                text_e = "%s ERROR => %s" % (text_log, e.args[0])
                log.error(text_e)
                response.data = {"errors", text_e}
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return response
        response.status_code = status.HTTP_403_FORBIDDEN
        response.data = {"data", "Not OK - you do not have sufficient rights"}
        return response


class ProfileViewSet(viewsets.ViewSet):

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            title="UserActivate",
            in_=openapi.IN_FORM,
            required=[
                "email",
                "password",
            ],
            properties={
                "email": openapi.Schema(
                    example="<user_email>", type=openapi.TYPE_STRING
                ),
                "password": openapi.Schema(
                    example="nH2qGiehvEXjNiYqp3bOVtAYv....", type=openapi.TYPE_STRING
                ),
            },
        ),
        manual_parameters=[],
        responses={
            201: openapi.Response(
                description="Данные на выходе",
                headers={
                    "Set-Cookie": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Access и refresh токены в cookies",
                        examples={
                            "access_token": {
                                "summary": "Access токен",
                                "value": "access=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...; Path=/; HttpOnly; Secure; SameSite=Lax",
                            },
                            "refresh_token": {
                                "summary": "Refresh токен",
                                "value": "refresh=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...; Path=/; HttpOnly; Secure; SameSite=Lax",
                            },
                        },
                    )
                },
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
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
                        "role": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="staff",
                        ),
                        "is_superuser": openapi.Schema(
                            type=openapi.TYPE_BOOLEAN,
                            example=False,
                        ),
                        "is_admin": openapi.Schema(
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
                        "is_sent": openapi.Schema(
                            type=openapi.TYPE_BOOLEAN,
                            example=False,
                        ),
                        "is_verified": openapi.Schema(
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
                        # "groups": [str],
                        # "user_permissions": [any]
                    },
                ),
            ),
            401: "Not Ok",
            500: "Something what wrong. Read the response variable 'data'",
        },
        tags=["person"],
    )
    async def active(self, request: Request, *args, **kwargs) -> Response:
        """ "
            TODO: Для 'BlackListModel' наладить CRUD для возвращения пользователю аккаунт.
                Запрос на удаление аккаунта, добавляет аккаунт в чёрный список - 'BlackListModel' db. После,
                 пользователь не может авторизоваться.
                Повторный запрос на удаление аккаунта (от пользователя с правами администратора и супервользователя)
                удаляет аккаунт из db.
            Если раннее проводилась попытка - удалить аккаунт, необходимы права \
             администратора - удалить (вручную) email из 'BlackListModel' db.
             После этого пользователь может активироваться.
            Cooockie содержит два токенаЖ
            - access;
            - refresh;
            :return ```text
             {
                "data": {
                    "id": "c4ebb722-930d-4ad9-ad1e-237eb4b41c70",
                    "email": "gKU@mail.ru",
                    "role": "Role: staff",
                    "last_login": null,
                    "is_superuser": false,
                    "is_staff": true,
                    "date_joined": "2025-12-01T15:57:02.286616+07:00",
                    "created_at": "2025-12-01T15:57:02.286726+07:00",
                    "updated_at": "2025-12-01T15:57:40.922670+07:00",
                    "username": "Gku",
                    "first_name": null,
                    "last_name": null,
                    "status": "PROCESS",
                    "refer": "c9b0fa36-210b-4095-8cb3-5b21bf04f953",
                    "is_sent": false,
                    "is_active": true,
                    "is_verified": false,
                    "is_admin": false,
                    "groups": [
                        3
                    ],
                    "user_permissions": []
                },
                "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY0NjY4MjgzLCJpYXQiOjE3NjQ1ODE4ODMsImp0aSI6IjFlOTJkYTg2OTg2YzQ3MjhhMjk0OTdjZDM4NDA1ZDA1IiwiZW1haWwiOiJnS1VAbWFpbC5ydSIsImlkIjoiYzRlYmI3MjItOTMwZC00YWQ5LWFkMWUtMjM3ZWI0YjQxYzcwIn0.u1JyXXHVFRvCnZIO95vRlLZ0-UbntTEFQUYQ5bOM2GM",
                "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2NDY2ODI4MCwiaWF0IjoxNzY0NTgxODgwLCJqdGkiOiI2Y2I0MmE4NS0zYWY0LTQ1YWUtYTc4MC00YzUyODVkYzcwYjMiLCJ1c2VyX2lkIjoiYzRlYmI3MjItOTMwZC00YWQ5LWFkMWUtMjM3ZWI0YjQxYzcwIiwiYWNjZXNzX3Rva2VuIjoiZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SjBiMnRsYmw5MGVYQmxJam9pWVdOalpYTnpJaXdpWlhod0lqb3hOelkwTmpZNE1qZ3pMQ0pwWVhRaU9qRTNOalExT0RFNE9ETXNJbXAwYVNJNklqRmxPVEprWVRnMk9UZzJZelEzTWpoaE1qazBPVGRqWkRNNE5EQTFaREExSWl3aVpXMWhhV3dpT2lKblMxVkFiV0ZwYkM1eWRTSXNJbWxrSWpvaVl6UmxZbUkzTWpJdE9UTXdaQzAwWVdRNUxXRmtNV1V0TWpNM1pXSTBZalF4WXpjd0luMC51MUp5WFhIVkZSdkNuWklPOTV2UmxMWjAtVWJudFRFRlFVWVE1Yk9NMkdNIiwibGlmZXRpbWUiOjg2NDMwMC4wfQ.NLOYV52mIgX-axeuMLbMsAdFOTYWy4ZVlviwWZxWaY4",
                "access_expires": 1764668283,
                "refresh_expires": 1764668280
            }
        ```
        """
        text_log = "[%s.%s]:" % (self.__class__.__name__, self.active.__name__)
        data = request.data
        email = data.get("email")
        black_list = BlackListModel.objects.filter(email=email)
        response = Response()
        if await black_list.aexists():
            text_log += " User was removed before this. Pleas, contact with admin."
            log.info(f"{text_log} Status code: {status.HTTP_403_FORBIDDEN}")
            response.data = {"data": text_log}
            response.status_code = status.HTTP_403_FORBIDDEN
            return response
        if not is_active(request):
            try:
                # ==== CHECK EMAIL & PASSWORD
                serializer = ProfileSerializer(data=data)
                is_valid = await asyncio.to_thread(serializer.is_valid)
                if is_valid:

                    u = await User.objects.aget(email=email)
                    u.is_active = True
                    await u.asave(
                        update_fields=[
                            "is_active",
                        ]
                    )
                    # Get data for sending
                    serializer = ProfileSerializer(u)
                    kwarg = await serializer.adata

                    kwarg.pop("password")
                    kwarg.pop("password_hash")
                    kwarg.pop("verification_code")
                    # Get tokens
                    tokens = u.create_token()
                    c = Cookies(response)
                    c.cookie_create(
                        cookie_key="access_token",
                        value=tokens.__getitem__("access"),
                        max_age_=tokens.__getitem__("access_expires"),
                    )
                    c.cookie_create(
                        cookie_key="refresh_token",
                        value=tokens.__getitem__("refresh"),
                        max_age_=tokens.__getitem__("refresh_expires"),
                    )

                    # не работает CSRFToken
                    response.status_code = status.HTTP_200_OK
                    response.data = {"data": kwarg, **tokens}

                    return response

                else:
                    text_log += " Data is invalid."
                    log.info(f"{text_log} Status code {status.HTTP_401_UNAUTHORIZED}")
                    response.data = {"data": text_log}
                    response.status_code = status.HTTP_401_UNAUTHORIZED
                    return response
            except Exception as error:
                text_log += f"ERROR => {error.args[0]}"
                log.info(
                    f"{text_log} Statuys code: {status.HTTP_500_INTERNAL_SERVER_ERROR}"
                )
                response.data = {"errors": text_log}
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return response
        text_log += " User was activated before this."
        log.info(f"{text_log} Status code: {status.HTTP_401_UNAUTHORIZED}")
        response.data = {"data": text_log}
        response.status_code = status.HTTP_403_FORBIDDEN
        return response

    @swagger_auto_schema(
        operation_description="""
            You wil can deactivate the user account only if you is:
            - owner;
            - admin;
            - superuser;
            Method: PATCH.
            Pathname: Change a user 'id' from pathname.


                        """,
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
        responses={
            200: "OK. User was inactive - successfully",
            401: "User was inactive before or something what wrong in the request",
            500: "IERROR => ...",
        },
        tags=["person"],
    )
    async def inactive(self, request: Request, pk: str, **kwargs) -> Response:
        text_log = "[%s.%s]" % (
            self.__class__.__name__,
            self.inactive.__name__,
        )
        response = Response()
        if not is_active(request):
            text_log += " Your accout needs to be activated"
            log.info(text_log)
            response.status_code = status.HTTP_401_UNAUTHORIZED
            response.data = {"data", text_log}
            return response
        u_list = User.objects.filter(id=pk)

        list_bool = await u_list.aexists()
        if not list_bool:
            response.data = {"data": "User not found"}
            response.status_code = status.HTTP_404_NOT_FOUND
            return response
        u = await u_list.afirst()
        if ((pk and is_owner(request, u)) or is_all(request)) or request.user.is_admin:
            try:
                # Change db
                u = await User.objects.aget(pk=pk)
                u.is_active = False
                await u.asave(
                    update_fields=[
                        "is_active",
                    ]
                )
                # The clear of cookie
                c = Cookies(response)
                c.cookie_create(
                    cookie_key="access_token",
                    value="",
                    max_age_=0,
                )
                c.cookie_create(
                    cookie_key="refresh_token",
                    value="",
                    max_age_=0,
                )
                # Create - a response
                response.__setattr__("data", "OK. User was inactive - successfully")
                response.__setattr__("status_code", status.HTTP_200_OK)
            except ValueError as e:
                # Error
                response.data = {"data": "ERROR => %s" % e.args[0]}
                response.status_code = status.HTTP_404_NOT_FOUND
                return response
            except Exception as error:
                # Error
                response.data = {"data": "ERROR => %s" % error.args[0]}
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return response
            # Then
            return response

        # We received a problem with user.
        response.data = {
            "data": "User was inactive before or something what wrong in the request"
        }
        response.__setattr__("status_code", status.HTTP_401_UNAUTHORIZED)
        return response
