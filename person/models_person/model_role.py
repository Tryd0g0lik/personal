"""
person/models_person/model_role.py
"""

from django.core.validators import (
    MinLengthValidator,
    RegexValidator,
    MaxLengthValidator,
)
from django.utils.translation import gettext_lazy as _
from django.db import models

from person.models_person.model_basic import BaseModel
from person.models_person.model_business import BusinessElementModel


class RoleModel(BaseModel):
    """
    Запуская CMS автоматически создаётся список ролей (по умолчанию) =  "staff", "admin", "user", "visitor", "superuser".
    Note: Будьте осторожны. Список включает свободное расширение. При регистрации пользователя может зарегистрировать новый список если его нет в базе.
    Для регистрации пользлователя рекомендую сделать фиксированный список из наименований представленных выше (если не желаеете вносить новые данные).

    """

    name = models.CharField(
        max_length=50,
        unique=True,
        validators=[
            MinLengthValidator(3),
            MaxLengthValidator(50),
            RegexValidator(regex=r"(^[A-Z][A-Za-z0-9_-]+$)"),
        ],
        help_text=_("The role name. Min 3 & Max 50 characters long."),
    )
    description = models.TextField(
        blank=True,
        null=True,
        validators=[
            MaxLengthValidator(150),
            RegexValidator(regex=r"(^[A-Z][\w_ -]+$)"),
        ],
        help_text=_("The description of the role. Max 150 characters long."),
    )

    class Meta:
        db_table = "role"
        # unique_together = (("id", "name"), "description", ("created_at", "updated_at"))
        verbose_name = _("Role")
        ordering = ("name",)

    def __str__(self):
        return "Role: %s" % self.name


class AccessRolesModel(BaseModel):
    """
    This is table of roles and permissions
    """

    role = models.ForeignKey(
        "RoleModel",
        on_delete=models.CASCADE,
        related_name="access_rules",
        db_column="role_id",
    )
    element = models.ForeignKey(
        BusinessElementModel,
        on_delete=models.CASCADE,
        related_name="access_rules",
        db_column="element_id",
        null=True,
        blank=True,
    )

    read_permission = models.BooleanField(
        default=False, db_column="read_permission", help_text=_("Read only own element")
    )
    read_all_permission = models.BooleanField(
        default=False,
        db_column="read_all_permission",
        help_text=_("Read all user's elements"),
    )
    create_permission = models.BooleanField(
        default=False, db_column="create_permission", help_text=_("Create new element")
    )
    update_permission = models.BooleanField(
        default=False,
        db_column="update_permission",
        help_text=_("Update only own element"),
    )
    update_all_permission = models.BooleanField(
        default=False,
        db_column="update_all_permission",
        help_text=_("Update all user's elements"),
    )
    delete_permission = models.BooleanField(
        default=False,
        db_column="delete_permission",
        help_text=_("Delete only own element"),
    )
    delete_all_permission = models.BooleanField(
        default=False,
        db_column="delete_all_permission",
        help_text=_("Delete all user's elements"),
    )

    class Meta:
        db_table = "access_roles"

        verbose_name = _("Access roles")
        ordering = ("role", "element")

    def __str__(self):
        return "AccessRole: %s" % self.role
