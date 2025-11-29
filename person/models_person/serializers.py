"""
person/models_person/serializers.py
"""

import asyncio
from typing import Optional, List

from adrf.serializers import ModelSerializer

# from drf_yasg.inspectors import view
from rest_framework import serializers


from person.models import User
from person.models_person.model_business import BusinessElementModel
from person.models_person.model_role import RoleModel


class UserSerializer(ModelSerializer):
    """
    User serializer
    """

    password = serializers.CharField(write_only=True, min_length=8, max_length=255)
    password_confirm = serializers.CharField(
        write_only=True, min_length=6, max_length=255
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "status",
            "email",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
            "updated_at",
        )
        read_only_fields = ("created_at",)

    def validate(self, attrs) -> dict:
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_date) -> Optional[User]:
        validated_date.pop("password_confirm")
        password = validated_date.pop("password")

        user_role = RoleModel.objects.get_or_create(name=validated_date["role"])
        user = User.objects.create(rolle=user_role, **validated_date)
        user.set_password(password)
        user.save()
        return user


class BusinessSerializer(ModelSerializer):
    class Meta:
        model: BusinessElementModel
        fields = "__all__"
        read_only_fields = ("created_at", "code")


class RoleSerializer(ModelSerializer):
    class Meta:
        model = RoleModel
        fields = "__all__"
        read_only_fields = ("created_at",)


type PersonUserSerializer = Optional[UserSerializer]
type PersonBusinessSerializer = Optional[BusinessSerializer]
type PersonRoleSerializer = Optional[RoleSerializer]
type PersonSerializerList = Optional[
    PersonUserSerializer, PersonBusinessSerializer, PersonRoleSerializer
]

# class DynamicSerializer:
#     def __init__(self, ):
#
#         self.serializers = {}
#
#     def add_serializzer(self,
#                         serializers_list:PersonSerializerList) -> None:
#         # [UserSerializer, BusinessSerializer, RoleSerializer]
#         for view in serializers_list:
#             if view.Meta:
#                 self.serializers[view.Meta.model.__class__.__name__ ] = view
#         return None
#
#     def run_serializzer(self, model: Model)
#
#
