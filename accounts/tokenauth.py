import jwt
from django.conf import settings
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import BaseAuthentication
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError


class TokenAuthentication(BaseAuthentication):
    ACCESS_TOKEN_LIFETIME_MINUTES = getattr(
        settings, "JWT_ACCESS_TOKEN_LIFETIME_MINUTES", 15
    )
    REFRESH_TOKEN_LIFETIME_DAYS = getattr(settings, "JWT_REFRESH_TOKEN_LIFETIME_DAYS", 7)

    def authenticate(self, request):
        token = self.extract_token(request)
        if token is None:
            return None

        try:
            payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=["HS256"])
            self.verify_token(payload)
            if payload.get("token_type") != "access":
                raise AuthenticationFailed("Invalid token type")
            user_id = payload.get("id")
            user = get_user_model().objects.get(id=user_id)
            return (user, token)
        except (
            InvalidTokenError,
            ExpiredSignatureError,
            get_user_model().DoesNotExist,
        ):
            raise AuthenticationFailed("Invalid or expired token")

    def verify_token(self, payload):
        if "exp" not in payload:
            raise AuthenticationFailed("Token is missing expiration time")

        expiration = payload["exp"]
        current_time = datetime.now().timestamp()
        if current_time > expiration:
            raise AuthenticationFailed("Token has expired")

    def extract_token(self, request):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            return None

        parts = auth_header.split(" ")
        if len(parts) != 2 or parts[0] != "Bearer":
            raise AuthenticationFailed("Invalid authentication header")

        token = parts[1]
        if not token:
            raise AuthenticationFailed("Token is missing")

        return token

    @staticmethod
    def _encode_token(payload, expires_at, token_type):
        token_payload = {**payload}
        token_payload["exp"] = int(expires_at.timestamp())
        token_payload["token_type"] = token_type
        return jwt.encode(
            payload=token_payload,
            key=settings.SECRET_KEY,
            algorithm="HS256",
        )

    @classmethod
    def generate_access_token(cls, payload):
        expiration = datetime.now() + timedelta(minutes=cls.ACCESS_TOKEN_LIFETIME_MINUTES)
        return cls._encode_token(payload, expiration, "access")

    @classmethod
    def generate_refresh_token(cls, payload):
        expiration = datetime.now() + timedelta(days=cls.REFRESH_TOKEN_LIFETIME_DAYS)
        return cls._encode_token(payload, expiration, "refresh")

    @classmethod
    def generate_token_pair(cls, payload):
        return {
            "access_token": cls.generate_access_token(payload),
            "refresh_token": cls.generate_refresh_token(payload),
        }

    @classmethod
    def generate_token(cls, payload):
        return cls.generate_access_token(payload)

    @classmethod
    def refresh_access_token(cls, refresh_token):
        try:
            payload = jwt.decode(refresh_token, key=settings.SECRET_KEY, algorithms=["HS256"])
            cls().verify_token(payload)
            if payload.get("token_type") != "refresh":
                raise AuthenticationFailed("Invalid token type")
            access_payload = {
                "id": payload.get("id"),
                "email": payload.get("email"),
                "username": payload.get("username"),
                "role": payload.get("role"),
            }
            return cls.generate_access_token(access_payload)
        except (InvalidTokenError, ExpiredSignatureError):
            raise AuthenticationFailed("Invalid or expired refresh token")
