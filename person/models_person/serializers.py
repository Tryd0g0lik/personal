"""
person/models_person/serializers.py
"""

import asyncio
from typing import Optional

from adrf.serializers import ModelSerializer
from rest_framework import serializers

from person.models import User, Role


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
        )

    def validate(self, attrs) -> dict:
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_date) -> Optional[User]:
        validated_date.pop("password_confirm")
        password = validated_date.pop("password")

        user_role = Role.objects.get_or_create(name=validated_date["role"])
        user = User.objects.create(rolle=user_role, **validated_date)
        user.set_password(password)
        user.save()
        return user


class RoleSerializer(ModelSerializer):
    class Meta:
        model = Role
        fields = ()
