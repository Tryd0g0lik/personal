import uuid
from django.db import models

from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(_("created_at"), default=timezone.now)
    updated_at = models.DateTimeField(_("updated_at"), auto_now=True)

    class Meta:
        abstract = True
