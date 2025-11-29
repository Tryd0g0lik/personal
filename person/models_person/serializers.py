"""
person/models_person/serializers.py
"""

import asyncio
from typing import Optional, List

from adrf.serializers import ModelSerializer

from rest_framework import serializers


from person.models import User
from person.models_person.model_business import BusinessElementModel
from person.models_person.model_role import RoleModel


class UserSerializer(ModelSerializer):
    """
    User serializer
    """

    role = serializers.CharField(write_only=True)
    password = serializers.CharField(min_length=6, max_length=255)
    password_confirm = serializers.CharField(
        write_only=True, min_length=6, max_length=255
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "role",
            "is_staff",
            "first_name",
            "is_superuser",
            "is_active",
            "is_sent",
            "is_verified",
            "status",
            "last_name",
            "created_at",
            "updated_at",
            "username",
            "password_confirm",
            "password",
        ]
        read_only_fields = (
            "username",
            "password_hash",
            "refer",
            "is_sent",
            "is_verified",
            "verification_code",
            "status",
        )

        # read_only_fields = ("created_at",)

    def validate(self, attrs) -> dict:
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Passwords don't match")
        role_name = attrs.get("role")
        if not role_name:
            raise serializers.ValidationError({"role": "Role is required"})
        return attrs

    async def acreate(self, validated_data) -> Optional[User]:
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

        email = validated_data.get("email")
        validated_data["username"] = email.split("@")[0]

        role_name = validated_data.pop("role")
        validated_data.pop("groups", None)
        validated_data.pop("user_permissions", None)

        user_role, created = await RoleModel.objects.aget_or_create(name=role_name)
        user = await User.objects.acreate(role=user_role, **validated_data)

        user.set_password(password)
        await user.asave()
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
