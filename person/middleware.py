"""
person/middleware.py
"""

from rest_framework import status
from person.jwt.person_jwt_manager import TokenManager


class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        try:
            access_token = request.COOKIES.get("access_token")
            refresh_token = request.COOKIES.get("refresh_token")
            token_user = (
                "access_token"
                if access_token
                else ("refresh_token" if refresh_token else False)
            )

            if token_user and token_user == "access_token":
                # ==== ACCESS TOKEN
                from person.models import User
                from rest_framework.response import Response

                token_manager = TokenManager(request.user)
                t = token_manager.verify_access_token(access_token)
                u_list = User.objects.filter(pk=t["id"], email=t["email"]) if t else []
                if request.user.is_anonymous and u_list.exists():
                    request.user = u_list.first()
            if token_user and token_user == "refresh_token":
                # ==== REFRESH TOKEN
                pass
            request.__setattr__("status_code", status.HTTP_200_OK)
            return self.get_response(request)
        except Exception as error:
            request.__setattr__("status_code", status.HTTP_500_INTERNAL_SERVER_ERROR)
            request.__setattr__("error", f"ERROR => {error.args[0]}")
            return self.get_response(request)
