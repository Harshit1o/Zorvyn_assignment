from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from accounts.tokenauth import TokenAuthentication
from rest_framework.throttling import ScopedRateThrottle
from accounts.serializers import UserSerializer, LoginSerializer, RefreshTokenSerializer


class UserRegistration(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "register"

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "user registered successfully", "success": True},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            token_pair = TokenAuthentication.generate_token_pair(
                payload=serializer.validated_data
            )
            return Response(
                {
                    "token": token_pair["access_token"],
                    "access_token": token_pair["access_token"],
                    "refresh_token": token_pair["refresh_token"],
                    "message": "login success",
                    "user": serializer.validated_data,
                    "success": True,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshView(APIView):
    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            access_token = TokenAuthentication.refresh_access_token(
                serializer.validated_data["refresh_token"]
            )
        except AuthenticationFailed as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(
            {
                "access_token": access_token,
                "token": access_token,
                "success": True,
            },
            status=status.HTTP_200_OK,
        )
