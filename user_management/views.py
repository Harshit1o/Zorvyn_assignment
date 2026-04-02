from rest_framework import status
from rest_framework.views import APIView
from accounts.permissions import IsAdmin
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from accounts.tokenauth import TokenAuthentication
from user_management.serializers import UserManagementSerializer

User = get_user_model()
MANAGEABLE_ROLES = (User.Role.VIEWER, User.Role.ANALYST)


class UserListCreateView(APIView):
    permission_classes = [IsAdmin]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        role = request.query_params.get("role")
        users = User.objects.filter(role__in=MANAGEABLE_ROLES)
        if role and role in MANAGEABLE_ROLES:
            users = users.filter(role=role)
        serializer = UserManagementSerializer(users, many=True)
        return Response({"users": serializer.data, "success": True})

    def post(self, request):
        serializer = UserManagementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "user": serializer.data,
                    "message": "User created successfully.",
                    "success": True,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    permission_classes = [IsAdmin]
    authentication_classes = [TokenAuthentication]

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk, role__in=MANAGEABLE_ROLES)
        except User.DoesNotExist:
            return None

    def get(self, request, pk):
        user = self.get_object(pk)
        if user is None:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = UserManagementSerializer(user)
        return Response({"user": serializer.data, "success": True})

    def patch(self, request, pk):
        user = self.get_object(pk)
        if user is None:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = UserManagementSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "user": serializer.data,
                    "message": "User updated successfully.",
                    "success": True,
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = self.get_object(pk)
        if user is None:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )
        user.delete()
        return Response(
            {"message": "User deleted successfully.", "success": True},
            status=status.HTTP_200_OK,
        )
