"""
project/person_jwt_access_token.py
"""
import uuid
from typing import Optional

from rest_framework_simplejwt.tokens import (AccessToken, T)
from rest_framework_simplejwt.tokens import Token
from datetime import datetime, timedelta, date
from django.apps import apps
from rest_framework_simplejwt.utils import aware_utcnow

User = apps.get_model("person", "User")

class CustomAccessToken(AccessToken):
    def __init__(self, user: Optional[User] | None, token: Token | None = None, verify: bool = True,):
        if token is not None:
            super().__init__(token, verify)

        else:
            super().__init__()

        if user is not None:
            self.user = user
            self._init_user_claims()


    def _init_user_claims(self) -> None:
        """
        Access token from user properties
        :param int exp: hours - the time of the token's live
        """
        if not self.user: return
        self["first_name"] = self.user.first_name
        self['email'] = self.user.email


        self["token_type"] = "access"
        self["iat"] = datetime.now()
        self['jti'] = str(uuid.uuid4())

    @classmethod
    def for_user(cls: type[T], user: User, lifetime: int | None = 86400) -> AccessToken:
        """

        :param user:
        :param lifetime: seconds - the time of the token's live
        :return:
        """
        token = cls(user=user)
        if lifetime:
            token.set_exp(lifetime=timedelta(seconds=lifetime), from_time=aware_utcnow())

        return token
