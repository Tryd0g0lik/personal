"""
person/models_person/model_black.py
"""

from django.core.validators import (
    MinLengthValidator,
    MaxLengthValidator,
    RegexValidator,
    EmailValidator,
)
from django.db import models
from django.utils.translation import gettext_lazy as _
from person.models_person.model_basic import BaseModel


class BlackListModel(BaseModel):
    """
    Black list model - email пользователя попадает в данный список на этапе (первичного) удаления.
    """

    email = models.EmailField(
        unique=True,
        blank=False,
        validators=[
            EmailValidator(),
            RegexValidator(
                regex=r"(^[A-Za-z][A-Za-z_0-9-]{0,20}@[A-Za-z]{1,10}\.[A-Za-z]{2,3})"
            ),
        ],
    )

    class Meta:
        db_table = "person_blacklist"
        verbose_name_plural = "Black List"
        ordering = ["email"]

    def __str__(self):
        return self.email
