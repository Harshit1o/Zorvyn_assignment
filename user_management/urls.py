from django.urls import path
from user_management.views import UserListCreateView, UserDetailView

urlpatterns = [
    path("users/", UserListCreateView.as_view(), name="user-list-create"),
    path("users/<uuid:pk>/", UserDetailView.as_view(), name="user-detail"),
]
