
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from business.views_business import BusinessElementModel
from person.models import User
from person.models_person.model_black import BlackListModel
from person.models_person.model_role import RoleModel, AccessRolesModel


class UserAdmin(SnippetViewSet):
    model = User
    list_display = (
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
        "is_staff",
        "is_active",
        "is_superuser",
        "is_admin",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_admin",
        "is_active",
        "created_at",
        "updated_at",
    )
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("email", "username", "first_name", "last_name")
    readonly_fields = (
        "created_at",
        "id",
    )


register_snippet(UserAdmin)


class RoleAdmin(SnippetViewSet):
    model = RoleModel
    list_display = ("id", "name", "updated_at")
    search_fields = ("name",)
    ordering = ("updated_at",)
    list_filter = ("updated_at",)
    readonly_fields = ("created_at", "id")


register_snippet(RoleAdmin)


class BusinessElementAdmin(SnippetViewSet):
    model = BusinessElementModel
    list_display = ("id", "name", "code", "updated_at")
    search_fields = ("name",)
    ordering = ("updated_at",)
    list_filter = ("updated_at",)
    readonly_fields = ("created_at", "id")


register_snippet(BusinessElementAdmin)


class BlackListAdmin(SnippetViewSet):
    model = BlackListModel
    list_display = (
        "id",
        "email",
        "updated_at",
    )
    list_filter = (
        "email",
        "updated_at",
    )
    search_fields = ("email",)
    ordering = ("updated_at",)
    readonly_fields = ("created_at", "id")


register_snippet(BlackListAdmin)
