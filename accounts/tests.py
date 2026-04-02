from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

User = get_user_model()

NO_THROTTLE = {
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": {},
}


@override_settings(
    REST_FRAMEWORK={
        **{
            "DEFAULT_AUTHENTICATION_CLASSES": (
                "accounts.tokenauth.TokenAuthentication",
            )
        },
        **NO_THROTTLE,
    }
)
class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = "/api/auth/register/"
        self.login_url = "/api/auth/login/"
        self.refresh_url = "/api/auth/refresh/"

    def test_register_success(self):
        res = self.client.post(
            self.register_url,
            {
                "email": "admin@test.com",
                "username": "adminuser",
                "password": "Admin@123",
                "role": "ADMIN",
            },
        )
        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.data["success"])

    def test_register_duplicate_email(self):
        User.objects.create_user(
            email="dup@test.com", username="dup", password="Pass@1"
        )
        res = self.client.post(
            self.register_url,
            {
                "email": "dup@test.com",
                "username": "dup2",
                "password": "Pass@1",
            },
        )
        self.assertEqual(res.status_code, 400)

    def test_register_weak_password(self):
        res = self.client.post(
            self.register_url,
            {
                "email": "weak@test.com",
                "username": "weakuser",
                "password": "password",
            },
        )
        self.assertEqual(res.status_code, 400)

    def test_login_success(self):
        User.objects.create_user(
            email="login@test.com", username="loginuser", password="Login@123"
        )
        res = self.client.post(
            self.login_url,
            {
                "email": "login@test.com",
                "password": "Login@123",
            },
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("token", res.data)
        self.assertIn("access_token", res.data)
        self.assertIn("refresh_token", res.data)

    def test_login_wrong_password(self):
        User.objects.create_user(
            email="user@test.com", username="someuser", password="Right@123"
        )
        res = self.client.post(
            self.login_url,
            {
                "email": "user@test.com",
                "password": "Wrong@123",
            },
        )
        self.assertEqual(res.status_code, 400)

    def test_login_returns_role(self):
        User.objects.create_user(
            email="analyst@test.com",
            username="analystuser",
            password="Pass@123",
            role="ANALYST",
        )
        res = self.client.post(
            self.login_url,
            {
                "email": "analyst@test.com",
                "password": "Pass@123",
            },
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["user"]["role"], "ANALYST")

    def test_refresh_success(self):
        User.objects.create_user(
            email="refresh@test.com",
            username="refreshuser",
            password="Refresh@123",
        )
        login_res = self.client.post(
            self.login_url,
            {
                "email": "refresh@test.com",
                "password": "Refresh@123",
            },
        )

        refresh_res = self.client.post(
            self.refresh_url,
            {"refresh_token": login_res.data["refresh_token"]},
        )

        self.assertEqual(refresh_res.status_code, 200)
        self.assertIn("access_token", refresh_res.data)

    def test_refresh_rejects_invalid_token(self):
        res = self.client.post(
            self.refresh_url,
            {"refresh_token": "invalid-token"},
        )
        self.assertEqual(res.status_code, 401)
