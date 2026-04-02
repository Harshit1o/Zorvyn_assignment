from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from accounts.tokenauth import TokenAuthentication
from django.test import TestCase, override_settings
from financial_records.models import FinancialRecord

User = get_user_model()

NO_THROTTLE = {
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": {},
}

RECORD_PAYLOAD = {
    "amount": "1500.00",
    "type": "INCOME",
    "category": "SALARY",
    "date": "2026-04-01",
    "notes": "April salary",
}


def make_token(user):
    payload = {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "role": user.role,
    }
    return TokenAuthentication.generate_token(payload)


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
class FinancialRecordPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.list_url = "/api/finance/records/"
        self.admin = User.objects.create_user(
            email="admin@t.com", username="admin", password="A@1", role="ADMIN"
        )
        self.analyst = User.objects.create_user(
            email="analyst@t.com", username="analyst", password="A@1", role="ANALYST"
        )
        self.viewer = User.objects.create_user(
            email="viewer@t.com", username="viewer", password="A@1", role="VIEWER"
        )

    def auth(self, user):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {make_token(user)}")

    def test_admin_can_create_record(self):
        self.auth(self.admin)
        res = self.client.post(self.list_url, RECORD_PAYLOAD)
        self.assertEqual(res.status_code, 201)

    def test_analyst_cannot_create_record(self):
        self.auth(self.analyst)
        res = self.client.post(self.list_url, RECORD_PAYLOAD)
        self.assertEqual(res.status_code, 403)

    def test_viewer_cannot_create_record(self):
        self.auth(self.viewer)
        res = self.client.post(self.list_url, RECORD_PAYLOAD)
        self.assertEqual(res.status_code, 403)

    def test_all_roles_can_list_records(self):
        for user in [self.admin, self.analyst, self.viewer]:
            self.auth(user)
            res = self.client.get(self.list_url)
            self.assertEqual(res.status_code, 200)

    def test_unauthenticated_cannot_list(self):
        self.client.credentials()
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, 403)


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
class FinancialRecordCRUDTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.list_url = "/api/finance/records/"
        self.admin = User.objects.create_user(
            email="admin@t.com", username="admin", password="A@1", role="ADMIN"
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {make_token(self.admin)}")
        res = self.client.post(self.list_url, RECORD_PAYLOAD)
        self.record_id = res.data["record"]["id"]
        self.detail_url = f"/api/finance/records/{self.record_id}/"

    def test_get_single_record(self):
        res = self.client.get(self.detail_url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["record"]["category"], "SALARY")

    def test_update_record(self):
        res = self.client.patch(self.detail_url, {"amount": "2000.00"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["record"]["amount"], "2000.00")

    def test_delete_record_is_soft(self):
        res = self.client.delete(self.detail_url)
        self.assertEqual(res.status_code, 200)
        # Record should no longer appear in list
        list_res = self.client.get(self.list_url)
        ids = [r["id"] for r in list_res.data["results"]]
        self.assertNotIn(self.record_id, ids)
        # But it still exists in DB with is_deleted=True
        record = FinancialRecord.all_objects.get(id=self.record_id)
        self.assertTrue(record.is_deleted)
        self.assertIsNotNone(record.deleted_at)

    def test_deleted_record_returns_404(self):
        self.client.delete(self.detail_url)
        res = self.client.get(self.detail_url)
        self.assertEqual(res.status_code, 404)


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
class FinancialRecordFilterSearchTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.list_url = "/api/finance/records/"
        self.admin = User.objects.create_user(
            email="admin@t.com", username="admin", password="A@1", role="ADMIN"
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {make_token(self.admin)}")
        self.client.post(
            self.list_url,
            {
                "amount": "1000",
                "type": "INCOME",
                "category": "SALARY",
                "date": "2026-03-01",
                "notes": "march salary",
            },
        )
        self.client.post(
            self.list_url,
            {
                "amount": "200",
                "type": "EXPENSE",
                "category": "FOOD",
                "date": "2026-03-15",
                "notes": "grocery run",
            },
        )
        self.client.post(
            self.list_url,
            {
                "amount": "500",
                "type": "INCOME",
                "category": "FREELANCE",
                "date": "2026-04-01",
                "notes": "freelance project",
            },
        )

    def test_filter_by_type(self):
        res = self.client.get(self.list_url, {"type": "INCOME"})
        self.assertEqual(res.status_code, 200)
        for r in res.data["results"]:
            self.assertEqual(r["type"], "INCOME")

    def test_filter_by_category(self):
        res = self.client.get(self.list_url, {"category": "FOOD"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["results"]), 1)

    def test_filter_by_date_range(self):
        res = self.client.get(
            self.list_url, {"date_from": "2026-04-01", "date_to": "2026-04-30"}
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["results"]), 1)

    def test_search_by_notes(self):
        res = self.client.get(self.list_url, {"search": "grocery"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["notes"], "grocery run")

    def test_viewer_filters_ignored(self):
        viewer = User.objects.create_user(
            email="viewer@t.com", username="viewer", password="A@1", role="VIEWER"
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {make_token(viewer)}")
        res = self.client.get(self.list_url, {"type": "INCOME"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["count"], 3)


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
class PaginationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.list_url = "/api/finance/records/"
        self.admin = User.objects.create_user(
            email="admin@t.com", username="admin", password="A@1", role="ADMIN"
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {make_token(self.admin)}")
        for i in range(15):
            self.client.post(
                self.list_url,
                {
                    "amount": "100",
                    "type": "INCOME",
                    "category": "SALARY",
                    "date": f"2026-01-{i + 1:02d}",
                    "notes": f"record {i}",
                },
            )

    def test_default_page_size_is_10(self):
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["results"]), 10)
        self.assertIn("next", res.data)
        self.assertEqual(res.data["count"], 15)

    def test_custom_page_size(self):
        res = self.client.get(self.list_url, {"page_size": 5})
        self.assertEqual(len(res.data["results"]), 5)

    def test_second_page(self):
        res = self.client.get(self.list_url, {"page": 2})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["results"]), 5)
