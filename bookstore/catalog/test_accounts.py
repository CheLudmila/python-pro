from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import Client, TestCase
from django.urls import reverse


class AccountsTests(TestCase):
    def test_registration_is_unprivileged(self):
        self.assertEqual(get_user_model()._meta.label, "accounts.User")
        password = "registration-test!72"
        response = self.client.post("/accounts/register/", {
            "username": "reader", "email": "reader@example.com",
            "password1": password, "password2": password, "is_staff": "on",
        })
        self.assertRedirects(response, "/accounts/login/")
        user = get_user_model().objects.get(username="reader")
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.groups.exists())
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_group_member_can_access_book_creation_after_login(self):
        user = get_user_model().objects.create_user("editor", password="editor-test!72")
        user.groups.add(Group.objects.get(name="Catalog editors"))
        create_url = reverse("catalog:book_create")
        login_url = "/accounts/login/"
        self.assertRedirects(self.client.get(create_url), f"{login_url}?next={create_url}")
        response = self.client.post(login_url, {
            "username": "editor", "password": "editor-test!72", "next": create_url,
        })
        self.assertRedirects(response, create_url)
        self.assertTrue(user.has_perm("catalog.change_book"))
        self.assertTrue(user.has_perm("catalog.delete_book"))
        self.assertFalse(user.is_staff)

    def test_logout_requires_post_and_csrf(self):
        client = Client(enforce_csrf_checks=True)
        user = get_user_model().objects.create_user("reader")
        client.force_login(user)
        url = "/accounts/logout/"
        self.assertEqual(client.get(url).status_code, 405)
        self.assertEqual(client.post(url).status_code, 403)
        client.get("/")
        token = client.cookies["csrftoken"].value
        self.assertRedirects(client.post(url, {"csrfmiddlewaretoken": token}), "/")
        self.assertNotIn("_auth_user_id", client.session)

    def test_request_log_omits_query_string(self):
        with self.assertLogs("bookstore.requests", level="INFO") as logs:
            self.client.get("/?q=private-query")
        self.assertIn("GET catalog:book_list status=200 duration_ms=", logs.output[0])
        self.assertNotIn("private-query", logs.output[0])
