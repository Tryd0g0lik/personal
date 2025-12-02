"""
person/models.py
"""

import uuid
from typing import Optional

import bcrypt
from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MinLengthValidator,
    MaxLengthValidator,
    RegexValidator,
    EmailValidator,
)
from django.db import models


from person.jwt.person_jwt_manager import TokenManager
from person.models_person.model_basic import BaseModel
from person.models_person.model_role import RoleModel

from project.bcoding import DcodeManager

from django.utils.translation import gettext_lazy as _

from project.settings import AUTHENTIFICATION_STATUS


class User(BaseModel, AbstractUser):
    """
    :param id it is generate of uuid.uuid4.
    На этапе хеширования пароля, для атрибута 'salt' используется id-свойство (тип строка). Двлее
        пароль использует 'base64.b64encode(password.encode(utf-8))' добавлено с целью увеличения безопастности.
    :param str status. It have the three of level:  default ("-------" & "-------"), next ("PROCESS" &
     "Beginning of authentification"), else ("ERROR" & "Mistake to the authentification") and
     ("COMPLETED" & "Completed of authentification").
    :param refer this is the code/reference or token for authentification through email.
    :param is_verified is True if the user's email address is verified.
    :param verification_code is used to verify the user's email address.
    :param is_active is True if the user was in login.
    :param is_sent is True if the letter was sent to the user's email.


    """

    username = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        validators=[
            RegexValidator(regex="^(^$|[A-Za-z]+$)"),
            MaxLengthValidator(50),
        ],
    )
    first_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        validators=[
            RegexValidator(regex="(^$|[A-Za-z]+$)"),
            MaxLengthValidator(50),
        ],
    )
    last_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        validators=[
            RegexValidator(regex="(^$|[A-Za-z]+$)"),
            MaxLengthValidator(50),
        ],
    )
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
    status = models.CharField(
        default=AUTHENTIFICATION_STATUS[0][0],
        choices=AUTHENTIFICATION_STATUS,
        max_length=50,
    )
    password_hash = models.CharField(
        _("password"),
        max_length=255,
        blank=True,
        null=True,
        validators=[
            # MinLengthValidator(6),
            MaxLengthValidator(255),
            RegexValidator(regex="[A-Za-z0-9-_)(%]{6,255}$"),
        ],
    )
    role = models.ForeignKey(RoleModel, on_delete=models.PROTECT, related_name="users")
    refer = models.UUIDField(default=uuid.uuid4, editable=False)
    is_sent = models.BooleanField(
        default=False,
        verbose_name="Message was sent",
        help_text=_(
            "Part is registration of new user.It is message sending \
to user's email. User indicates his email at the registrations moment."
        ),
    )
    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    verification_code = models.CharField(
        _("verification_code"),
        max_length=150,
        blank=True,
        null=True,
        validators=[MinLengthValidator(50)],
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return "User: %s Regisrated was: %s" % (self.email, self.created_at)

    class Meta:
        db_table = "user"
        verbose_name = _("User")

        # indexes = [models.Index(fields=["is_active"])]

    def set_password(self, password: str) -> None:
        """Hashing of password"""
        d = DcodeManager()
        salt = bcrypt.gensalt()
        self.password = bcrypt.hashpw(d.str_to_bynary(password), salt).decode("utf-8")

    def check_password(self, password: str) -> bool:
        """Checking password"""
        d = DcodeManager()

        return bcrypt.checkpw(
            d.str_to_bynary(password),
            self.password.encode("utf-8"),
        )

    def _get_token_manager(self) -> Optional[TokenManager]:
        """Gets the manage for token"""
        return TokenManager(self)

    def create_token(
        self, access_lifetime: int = 86400, refresh_lifetime: int = 864000
    ):
        """
        :param int access_lifetime: seconds - the time of life. It by default value is 86400 seconds.
        :param refresh_lifetime: seconds - the time of the token's refresh. It by default value is 86400 seconds
        :return:
        """

        manager = self._get_token_manager()

        return manager.create_token(
            access_lifetime=access_lifetime, refresh_lifetime=refresh_lifetime
        )

    # def verify_token(self, token_str: str) -> bool:
    #     """Check the token"""
    #     manager = self._get_token_manager()
    #     return manager.verify_access_token(token_str)

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email.split("@")[0]

        super().save(*args, **kwargs)


type TypeUserModel = Optional[User.objects]
