""""
person/models_person/model_session.py
"""

from person.models import models, User
from person.models import BaseModel
from django.utils import timezone


# class UserSessionModel(BaseModel):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
#     token = models.TextField()
#     expires_at = models.DateTimeField()
#     is_active = models.BooleanField(default=True)
#
#     class Meta:
#         db_table = "user_sessions"
#
#     def is_expired(self):
#         return timezone.now() > self.expires_at
