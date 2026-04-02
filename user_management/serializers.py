import re
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

MANAGEABLE_ROLES = (User.Role.VIEWER, User.Role.ANALYST)


class UserManagementSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["id", "email", "username", "role", "is_active", "password"]
        read_only_fields = ["id"]

    def validate_role(self, value):
        if value not in MANAGEABLE_ROLES:
            raise serializers.ValidationError(
                "Only VIEWER and ANALYST roles can be assigned."
            )
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

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
