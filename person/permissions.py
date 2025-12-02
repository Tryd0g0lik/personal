"""
person/permissions.py
"""

from typing import Optional

from django.db.models import Model
from rest_framework.permissions import BasePermission
from rest_framework.request import Request


class IsActive(BasePermission):
    """allows access only activated"""

    def has_permission(self, request: Request, view=None) -> bool:
        return (
            request.user and not request.user.is_anonymous and request.user.is_active
        ) and request.user.is_authenticated


is_active = IsActive().has_permission


class IsAll(BasePermission):
    """Allows the all access for the user of superuser only"""

    def has_permission(self, request: Request, view=None) -> bool:
        return is_active(request) and request.user.is_superuser


is_all = IsAll().has_permission

type ModelObjects = Optional[Model.objects]


class IsOwner(BasePermission):
    """ "Allows access only for the pruck-drivers"""

    def has_permission(self, request: Request, View: ModelObjects = None) -> bool:
        """
        Line of the single view from db. This is where is get the index from 'View.id'
        If the db's line was created by the user - it means return the True or not.
        """
        if not is_active(request) or not View:
            return False
        return is_all(request) or request.user.is_admin or request.user.id == View.id


is_owner = IsOwner().has_permission


class IsManagerOrAdmin(BasePermission):
    """Allows access for the managers and admin"""

    def has_permission(self, request, view=None):
        return (
            not request.user.groups.filter(
                name__in=[
                    "User_group",
                    "Visitor_group",
                ]
            ).exists()
            and is_active(request)
            and (is_all(request) or (request.user.is_admin or request.user.is_staff))
        )


is_managerOrAdmin = IsManagerOrAdmin().has_permission


class IsReader(BasePermission):
    """allows access only for read"""

    def has_permission(self, request: Request, view=None) -> bool:
        return is_active(request)


is_reader = IsReader().has_permission


class IsCreate(BasePermission):
    """allows access only for admin"""

    def has_permission(self, request: Request, view=None) -> bool:
        return (
            is_managerOrAdmin(request)
            or request.user.groups.filter(
                name__in=[
                    "User_group",
                ]
            ).exists()
        )


is_create = IsCreate().has_permission


class IsRemove(BasePermission):
    """allows access only for admin"""

    def has_permission(self, request: Request, view=None) -> bool:
        return is_all(request) or (request.user.is_admin)


is_remove = IsRemove().has_permission


class IsUpdate(BasePermission):
    """allows access only for admin"""

    def has_permission(self, request: Request, View: ModelObjects = None) -> bool:
        return is_all(request) or (request.user.is_admin or is_owner(request, View))


is_update = IsUpdate().has_permission
