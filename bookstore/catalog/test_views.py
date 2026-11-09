from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Book, Category


class BookViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Programming", slug="programming")
        cls.other = Category.objects.create(name="Fiction", slug="fiction")
        for index in range(13):
            Book.objects.create(title=f"Python {index:02}", author="Author",
                                price="100.00", stock=2, category=cls.category)
        Book.objects.create(title="Python sold out", author="Author", price="90.00",
                            category=cls.category)
        Book.objects.create(title="Python fiction", author="Author", price="90.00",
                            stock=1, category=cls.other)
        Book.objects.create(title="Django", author="Other", price="80.00",
                            stock=1, category=cls.category)
        cls.book = Book.objects.get(title="Python 00")

    def test_filters_are_combined_and_kept_in_pagination(self):
        response = self.client.get(reverse("catalog:book_list"), {
            "q": "Python", "category": "programming", "in_stock": "1",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["paginator"].count, 13)
        self.assertContains(response, "category=programming&amp;in_stock=1")
        response = self.client.get(reverse("catalog:book_list"), {
            "q": "Python", "category": "programming", "in_stock": "1", "page": 2,
        })
        self.assertEqual([book.title for book in response.context["books"]], ["Python 12"])

    def test_book_detail_is_public(self):
        response = self.client.get(reverse("catalog:book_detail", args=[self.book.pk]))
        self.assertContains(response, "Python 00")

    def test_user_without_permission_cannot_write(self):
        create = reverse("catalog:book_create")
        self.assertEqual(self.client.get(create).status_code, 302)
        user = get_user_model().objects.create_user(username="reader")
        self.client.force_login(user)
        self.assertEqual(self.client.post(create).status_code, 403)
        self.assertEqual(self.client.post(
            reverse("catalog:book_update", args=[self.book.pk])
        ).status_code, 403)
        self.assertEqual(self.client.post(
            reverse("catalog:book_delete", args=[self.book.pk])
        ).status_code, 403)
        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())

    def test_admin_can_create_update_and_delete_book(self):
        admin = get_user_model().objects.create_superuser(username="admin")
        self.client.force_login(admin)
        data = {"title": "New book", "author": "Author", "price": "42.00",
                "stock": 3, "category": self.category.pk, "description": "Example"}
        response = self.client.post(reverse("catalog:book_create"), data)
        book = Book.objects.get(title="New book")
        detail = reverse("catalog:book_detail", args=[book.pk])
        self.assertRedirects(response, detail)
        data["title"] = "Updated book"
        response = self.client.post(reverse("catalog:book_update", args=[book.pk]), data)
        self.assertRedirects(response, detail)
        book.refresh_from_db()
        self.assertEqual(book.title, "Updated book")
        url = reverse("catalog:book_delete", args=[book.pk])
        self.assertContains(self.client.get(url), "Updated book")
        self.assertTrue(Book.objects.filter(pk=book.pk).exists())
        self.assertRedirects(self.client.post(url), reverse("catalog:book_list"))
        self.assertFalse(Book.objects.filter(pk=book.pk).exists())
