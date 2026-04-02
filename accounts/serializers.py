import re
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = get_user_model().objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            role=validated_data.get("role", get_user_model().Role.VIEWER),
        )
        return user

    class Meta:
        model = get_user_model()
        fields = ["email", "username", "password", "role"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_email(self, value):
        if get_user_model().objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_password(self, value):
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )
        if not re.search(r"\d", value):
            raise serializers.ValidationError(
                "Password must contain at least one digit."
            )
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError(
                "Password must contain at least one special character."
            )
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise serializers.ValidationError(
                    "User not found with these credentials"
                )
            if not user.is_active:
                raise serializers.ValidationError("User is not active")
        else:
            raise serializers.ValidationError("Email and password are required.")
        return {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "role": user.role,
        }


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
