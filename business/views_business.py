"""
business/views_business.py
"""

import logging

from django.apps import apps
from adrf import viewsets
from drf_yasg import openapi
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.request import Request

from logs import configure_logging
from person.permissions import is_active, is_managerOrAdmin, is_create
from person.views_api.serializers import BusinessSerializer

log = logging.getLogger(__name__)
configure_logging(logging.INFO)

BusinessElementModel = apps.get_model("person", "BusinessElementModel")


class BusinessViewSet(viewsets.ModelViewSet):
    queryset = BusinessElementModel.objects.all()
    serializer_class = BusinessSerializer
    MAX_LINE = 50

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
            if is_managerOrAdmin(request) or is_create(request):
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

    from drf_yasg import openapi
    from drf_yasg.utils import swagger_auto_schema

    # views.py
    class DashboardViewSet(viewsets.ModelViewSet):
        queryset = BusinessElementModel.objects.all()
        serializer_class = BusinessSerializer

    @swagger_auto_schema(
        operation_description="""
        Получение списка бизнес-элементов с пагинацией.

        **Требования к доступу:**
        - Только пользователи с ролью Manager или Admin
        - Активный аккаунт

        **Параметры пагинации:**
        - `page`: Номер страницы (начиная с 1)
        - `page_size`: Количество элементов на странице (по умолчанию определяется в настройках DRF, обычно 10)

        **Структура ответа:**
        - `data`: Массив бизнес-элементов текущей страницы
        - `pagination`: Метаданные пагинации с информацией о текущей странице, общем количестве страниц и элементов

        **Пример запроса:**
        ```
        GET /api/dashboard/?page=1&page_size=50
        ```
        """,
        manual_parameters=[
            openapi.Parameter(
                name="page",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="Номер запрашиваемой страницы (начиная с 1). Если не указан, возвращается первая страница.",
                required=False,
                default=1,
                example=1,
            ),
            openapi.Parameter(
                name="page_size",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="Количество элементов на странице. Если не указан, используется значение по умолчанию из настроек DRF. Для получения 50 записей как указано в требованиях, установите значение 50.",
                required=False,
                example=50,
            ),
            openapi.Parameter(
                name="ordering",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Поле для сортировки результатов. Для сортировки по убыванию добавьте '-' перед названием поля. Примеры: 'created_at', '-name'",
                required=False,
                example="created_at",
            ),
            openapi.Parameter(
                name="search",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Поиск по всем текстовым полям модели",
                required=False,
                example="название элемента",
            ),
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description="Токен аутентификации в формате 'Bearer <token>'. Требуется для всех запросов.",
                required=True,
                example="Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            ),
        ],
        responses={
            200: openapi.Response(
                description="Успешный ответ со списком элементов и метаданными пагинации",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "count": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Общее количество элементов",
                            example=487,
                        ),
                        "next": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="URL следующей страницы (если есть)",
                            example="http://api.example.com/dashboard/?page=2",
                            nullable=True,
                        ),
                        "previous": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="URL предыдущей страницы (если есть)",
                            example=None,
                            nullable=True,
                        ),
                        "results": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            description="Массив бизнес-элементов текущей страницы",
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description="UUID элемента",
                                        example="c4ebb722-930d-4ad9-ad1e-237eb4b41c70",
                                    ),
                                    "name": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description="Название бизнес-элемента",
                                        example="Название бизнес-элемента",
                                    ),
                                    "description": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description="Описание элемента",
                                        example="Подробное описание бизнес-элемента",
                                        nullable=True,
                                    ),
                                    "created_at": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        format="date-time",
                                        description="Дата и время создания",
                                        example="2024-01-15T10:30:00Z",
                                    ),
                                    "updated_at": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        format="date-time",
                                        description="Дата и время последнего обновления",
                                        example="2024-01-15T10:30:00Z",
                                    ),
                                    "is_active": openapi.Schema(
                                        type=openapi.TYPE_BOOLEAN,
                                        description="Статус активности элемента",
                                        example=True,
                                    ),
                                },
                            ),
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                description="Некорректные параметры запроса",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "data": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Сообщение об ошибке",
                            example="Invalid page number. Page number must be an integer.",
                        ),
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Детали ошибки",
                            example="Page number must be an integer",
                            nullable=True,
                        ),
                    },
                ),
            ),
            401: openapi.Response(
                description="Неавторизованный доступ - недостаточно прав",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "data": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Сообщение об ошибке",
                            example="Not OK - you do not have sufficient rights",
                        )
                    },
                ),
            ),
            403: openapi.Response(
                description="Доступ запрещен - аккаунт не активирован",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "data": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Сообщение об ошибке",
                            example="Your account needs to be activated",
                        )
                    },
                ),
            ),
            404: openapi.Response(
                description="Страница не найдена",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "data": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Сообщение об ошибке",
                            example="Page not found",
                        ),
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Детали ошибки",
                            example="Requested page does not exist",
                            nullable=True,
                        ),
                    },
                ),
            ),
            500: openapi.Response(
                description="Внутренняя ошибка сервера",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "data": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Сообщение об ошибке",
                            example="Internal server error",
                        ),
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Детали ошибки",
                            example="Database connection failed",
                            nullable=True,
                        ),
                    },
                ),
            ),
        },
        tags=["business"],
    )
    async def list(self, request: Request, *args, **kwargs) -> Response:
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
                queryset = self.filter_queryset(self.get_queryset())

                paginator = self.pagination_class()
                page = paginator.paginate_queryset(queryset, request)

                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    response = paginator.get_paginated_response(serializer.data)
                    log.info(f"{text_log} Successfully retrieved page")
                    return response

                # Если пагинация не используется
                serializer = self.get_serializer(queryset, many=True)
                log.info(f"{text_log} Successfully retrieved all data")
                return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            text_log += f" ERROR => %s" % e.args[0]
            log.error(text_log)
            return Response(
                {"data": "Internal server error", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
