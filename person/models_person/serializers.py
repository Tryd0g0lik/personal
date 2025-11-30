"""
person/models_person/serializers.py
"""

import logging
import asyncio
import re
from typing import Optional, List

from adrf.serializers import ModelSerializer
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.core.validators import validate_email
from person.models import User
from person.models_person.model_business import BusinessElementModel
from person.models_person.model_role import RoleModel
from logs import configure_logging

configure_logging(logging.INFO)
log = logging.getLogger(__name__)


class UserSerializer(ModelSerializer):
    """
    User serializer
    """

    role = serializers.CharField(write_only=True)
    password = serializers.CharField(min_length=6, max_length=255)
    password_confirm = serializers.CharField(
        write_only=True, min_length=6, max_length=255
    )
    email = serializers.EmailField()

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
        regex = r"[A-Za-z0-9-_%)(]{6,255}$"
        if attrs["password"] != attrs["password_confirm"] or not re.search(
            regex, attrs["password"]
        ):
            raise serializers.ValidationError("Passwords don't match")
        role_name = attrs.get("role")
        if not role_name:
            raise serializers.ValidationError({"role": "Role is required"})

        email = attrs.get("email")
        print("EMAIL 1")
        rege = r"(^[A-Za-z][A-Za-z_0-9-]{0,20}@[A-Za-z]{1,10}\.[A-Za-z]{2,3})"
        if (
            not email
            or "@" not in email
            or "." not in email.split("@")[-1]
            or not re.search(rege, email)
        ):
            print("EMAIL 2")
            raise serializers.ValidationError(
                {"email": "Enter a invalid email address"}
            )
        try:
            validate_email(email)
        except ValidationError as e:
            raise serializers.ValidationError(
                {"email": "Enter a invalid email address => %s " % e.args[0]}
            )
        return attrs

    async def acreate(self, validated_data) -> Optional[User]:
        validated_data.pop("password_confirm").strip()
        password = validated_data.pop("password").strip()

        email = validated_data.get("email").strip()
        validated_data["username"] = email.split("@")[0].capitalize()
        role_name = validated_data.pop("role").strip()
        validated_data.pop("groups", None)
        validated_data.pop("user_permissions", None)
        try:
            user_role, created = await RoleModel.objects.aget_or_create(name=role_name)
            user = await User.objects.acreate(role=user_role, **validated_data)
            user.status = "PROCESS"
            user.set_password(password)
            await user.asave()
            return user
        except Exception as e:
            text_e = "[%s.%s]: %s" % (
                self.__class__.__name__,
                self.acreate.__name__,
                e.args[0],
            )
            log.error(text_e)
            raise text_e


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
