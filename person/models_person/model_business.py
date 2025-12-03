"""
person/models_person/model_business.py
"""

import uuid

from django.core.validators import (
    RegexValidator,
    MaxLengthValidator,
    MinLengthValidator,
)
from django.db import models


from person.models_person.model_basic import BaseModel


class BusinessElementModel(BaseModel):
    name = models.CharField(
        max_length=120,
        unique=True,
        validators=[
            MaxLengthValidator(120),
            MinLengthValidator(1),
            RegexValidator(
                regex=r"^([A-Za-z0-9\"'%)(}{_ ]{1,120})$",
            ),
        ],
        help_text="The business element name",
        verbose_name="business element name",
    )
    descriptions = models.TextField(
        blank=True, null=True, help_text="The business element descriptions"
    )
    code = models.TextField(
        max_length=50,
        default=str(uuid.uuid4()),
        unique=True,
        help_text="The business element code",
    )

    class Meta:
        db_table = "business_element"
        verbose_name = "business element"
        verbose_name_plural = "business elements"
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name
