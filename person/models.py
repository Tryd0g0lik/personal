import uuid
from typing import Optional

import bcrypt
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MinLengthValidator
from django.db import models

from person.jwt.person_jwt_manager import TokenManager
from project.bcoding import DcodeManager
# Create your models here.
import rest_framework_simplejwt
from datetime import date, timedelta
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from project.settings import AUTHENTIFICATION_STATUS


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(_("created_at"), default=timezone.now)
    updated_at = models.DateTimeField(_("updated_at"), auto_now=True)

    class Meta:
        abstract = True



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
    patronymic = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True)
    status = models.CharField(default=AUTHENTIFICATION_STATUS[0][0], choices=AUTHENTIFICATION_STATUS, max_length=50, )
    password = models.CharField(_("password"), max_length=255)
    role = models.ForeignKey('Role', on_delete=models.PROTECT, related_name='users')
    refer = models.UUIDField(default=uuid.uuid4, editable=False)
    is_sent = models.BooleanField(
        default=False,
        verbose_name="Message was sent",
        help_text=_(
            "Part is registration of new user.It is message sending \
to user's email. User indicates his email at the registrations moment."
        ),
    )
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(
        _("verification_code"),
        max_length=150,
        blank=True,
        null=True,
        validators=[MinLengthValidator(50)],
    )

    def __str__(self):
        return "User: %s Regisrated was: %s" % (self.username, self.created_at)

    class Meta:
        db_table = "user"
        verbose_name = _("User")
        ordering = [
            "-id",
        ]
        indexes = [models.Index(fields=["is_active"])]

    def set_password(self, password: str) -> None:
        """Hashing of password"""
        d = DcodeManager()
        salt = str(self.id).encode("utf-8")
        self.password = bcrypt.hashpw(d.str_to_bcode(password), salt).decode("utf-8")

    def check_password(self, password: str) -> bool:
        """Checking password"""
        d = DcodeManager()
        salt = str(self.id).encode("utf-8")
        return bcrypt.checkpw(bcrypt.hashpw(d.str_to_bcode(password), salt), self.password.encode("utf-8"))

    def get_token_manager(self) -> Optional[TokenManager]:
        """Gets the manage for token"""
        return TokenManager(self)

    def create_token(self, access_lifetime: int = 86400, refresh_lifetime: int = 864000):
        """
        :param int access_lifetime: seconds - the time of life. It by default value is 86400 seconds.
        :param refresh_lifetime: seconds - the time of the token's refresh. It by default value is 86400 seconds
        :return:
        """

        manager = self.get_token_manager()

        return  manager.create_token(access_lifetime=access_lifetime, refresh_lifetime=refresh_lifetime)

    def verify_token(self, token_str: str) -> bool:
        """Check the token"""
        manager = self.get_token_manager()
        return manager.verify_access_token(token_str)
