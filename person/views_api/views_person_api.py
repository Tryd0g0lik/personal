import asyncio
import logging

from adrf import viewsets
from celery import group
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_yasg.utils import swagger_auto_schema

from logs import configure_logging
from person.models import User
from django.contrib.auth.models import AnonymousUser
from person.views_api.serializers import UserSerializer, ProfileSerializer
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status, authentication

from project.settings import IS_SUPERUSER, IS_ADMIN

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


class UserViews(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [authentication.SessionAuthentication]

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
        If the field of role does not has the name - "user" or "visitor", it means a user has permission from the staff
        In moment of registration:
         - we fill the username's field - the text from the email address;
         - user is adding to the group. Group name is formed as a "< Rolename >_group";
         - the 'superuser' could be only one/single useer.
         The 'superuser' has a quantity only 1 - by the default value.
         The 'admin' has a quantity before 4 - by default value.
         We can change this quantity in the '.env' file. It's variable 'IS_ADMIN' & 'IS_SUPERUSER'.



        :param request:
        :return:
        """
        text_log = "[%s.%s]:" % (self.__class__.__name__, self.create.__name__)
        user = request.user if request.user else AnonymousUser()
        data = request.data
        role = data.get("role")
        response = Response()
        if user.is_anonymous:
            try:
                text_log += " User created failed."
                log.info(text_log)
                response.data = {"data": "User creates failed."}
                response.status_code = status.HTTP_401_UNAUTHORIZED
                # CHECK - VALID DATA
                # is staff
                serializer = self.serializer_class(data=data)
                is_valid = await asyncio.to_thread(serializer.is_valid)
                if is_valid:
                    # User is creating
                    await serializer.asave()
                    u = await asyncio.to_thread(
                        lambda: User.objects.get(email=data["email"])
                    )
                    # THis is , where is the user added in a group
                    u.groups.add(f"{role}_group".capitalize())
                    # This is, where user get the permission as a staff
                    is_staff = role not in ["user", "visitor"]
                    u.is_staff = is_staff

                    if role == "superuser":
                        superuser_list = await asyncio.to_thread(
                            lambda: User.objects.filter(is_superuser=True)
                        )
                        # The 'superuser' could be only one/single useer.
                        if len(superuser_list) == int(IS_SUPERUSER):
                            return response
                    elif role == "admin":
                        admin_list = await asyncio.to_thread(
                            lambda: User.objects.filter(is_admin=True)
                        )
                        # The 'superuser' could be only one/single useer.
                        if len(admin_list) == int(IS_ADMIN):
                            return response

                    await u.asave()
                    response.data = {"data": "User created successfully"}
                    response.status_code = status.HTTP_200_OK
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


class ProfileViewSet(viewsets.ViewSet):
    @method_decorator(ensure_csrf_cookie)
    async def active(self, request: Request, *args, **kwargs) -> Response:
        text_log = "[%s.%s]:" % (self.__class__.__name__, self.active.__name__)
        user = request.user if request.user else AnonymousUser()
        data = request.data

        response = Response()

        if user.is_anonymous:
            try:
                # serializer = self.serializer_class(data=data)
                serializer = ProfileSerializer(data=data)
                is_valid = await asyncio.to_thread(serializer.is_valid)
                if is_valid:
                    # u = User.objects.get(email=data.get("email"))
                    # u.is_active = True
                    #
                    # добавить пользователя в группу (group_имя_роли) при регистрации
                    # тобавить токены
                    # из header Authorization: Bearer {user_token},
                    # не работает CSRFToken
                    # kwargs = {"is_active": True}
                    # В request сразу присваивать request.user перед обработкой запроса в кастомном Middleware в Django
                    await serializer.update(**kwargs)
                    # c = Cookies(session_key_user="token_jwt", response=response)
                    # tokens_str = json.dumps(tokens_dict)
                    # c.session_user(value=tokens_str
                else:
                    text_log += " Data is invalid."
                    log.info(text_log)
                    response.data = {"data": text_log}
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
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return response
