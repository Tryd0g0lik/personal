import uuid
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from typing import Optional
from person.jwt.person_jwt_access_token import CustomAccessToken


class TokenManager:
    def __init__(self, user):
        self.user = user
        self.access_token: Optional[CustomAccessToken] = None
        self.refresh_token: Optional[RefreshToken] = None

    def create_token(
        self, access_lifetime: int | None = 86400, refresh_lifetime: int = None
    ):
        """

        :param int access_lifetime: seconds - the time of the token's live
        :param refresh_lifetime: seconds - the time of the token's refresh
        :return:
        """
        self.refresh_token = RefreshToken.for_user(self.user)
        self.access_token = CustomAccessToken.for_user(
            self.user, lifetime=access_lifetime
        )

        self.refresh_token["token_type"]: str = "refresh"
        self.refresh_token["access_token"] = self.access_token
        self.refresh_token["jti"] = str(uuid.uuid4())
        self.refresh_token["lifetime"] = timedelta(seconds=access_lifetime) + timedelta(
            seconds=refresh_lifetime
        )

        return {
            "access": str(self.access_token),
            "refresh": str(self.refresh_token),
            "access_expires": self.access_token["exp"],
            "refresh_expires": self.refresh_token["exp"],
        }

    def refresh_access_token(self, refresh_token_str: str) -> dict:
        """
        Updating the access token wrought  refresh token
        """
        try:
            refresh = RefreshToken()

            if str(refresh["user_id"]) != str(self.user.id):
                raise ValueError("Token does not belong to this user")

            new_access = CustomAccessToken.for_user(self.user)

            refresh["access_token"] = new_access

            return {
                "access": str(new_access),
                "refresh": str(refresh),
                "access_expires": new_access["exp"],
            }
        except Exception as e:
            raise ValueError(f"Token refresh failed: {str(e)}")

    def verify_access_token(self, token_str: str) -> bool:
        """
        Verification of access token
        """
        try:
            token = CustomAccessToken(token_str, verify=True)

            # additionally checks
            if str(token["user_id"]) != str(self.user.id):
                return False

            if not self.user.is_active:
                return False

            return True

        except Exception:
            return False
