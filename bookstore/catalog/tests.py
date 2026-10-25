from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.urls import reverse

from .models import Book, Category
from .queries import available_books, category_statistics, search_books


class CatalogTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Programming", slug="programming")
        cls.empty = Category.objects.create(name="Fiction", slug="fiction")
        cls.python = Book.objects.create(
            title="Python", author="Alice", price="100.50", stock=3, category=cls.category,
        )
        cls.django = Book.objects.create(
            title="Django", author="Bob", price="200.00", stock=0, category=cls.category,
        )

    def test_available_books_respects_price_and_stock(self):
        self.assertQuerySetEqual(available_books(max_price=Decimal("100.50")), [self.python])
        self.assertFalse(available_books(max_price=Decimal("100.49")).exists())

    def test_search_matches_title_or_author(self):
        self.assertQuerySetEqual(search_books("PYTHON"), [self.python])
        self.assertQuerySetEqual(search_books("bob"), [self.django])
        self.assertFalse(search_books("missing").exists())

    def test_statistics_include_empty_categories(self):
        stats = category_statistics().get(pk=self.category.pk)
        self.assertEqual(stats.book_count, 2)
        self.assertEqual(stats.available_count, 1)
        self.assertEqual(stats.average_price, Decimal("150.25"))
        self.assertEqual(stats.total_stock, 3)
        empty = category_statistics().get(pk=self.empty.pk)
        self.assertEqual(empty.book_count, 0)
        self.assertEqual(empty.total_stock, 0)
        self.assertIsNone(empty.average_price)

    def test_negative_price_and_stock_are_rejected(self):
        for field in ("price", "stock"):
            with self.subTest(field=field):
                book = Book(title="Invalid", author="Author", price="1.00",
                            stock=1, category=self.category)
                setattr(book, field, -1)
                with self.assertRaises(ValidationError):
                    book.full_clean()
                with self.assertRaises(IntegrityError), transaction.atomic():
                    book.save()

    def test_category_with_books_is_protected(self):
        with self.assertRaises(ProtectedError):
            self.category.delete()

    def test_slug_is_unique(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Category.objects.create(name="Duplicate", slug="programming")

    def login_admin(self):
        user = get_user_model().objects.create_superuser(
            username="admin", password="test-only-password"
        )
        self.client.force_login(user)

    def test_admin_search_and_filter(self):
        self.login_admin()
        url = reverse("admin:catalog_book_changelist")
        response = self.client.get(url, {"q": "Alice"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["cl"].queryset), [self.python])
        response = self.client.get(url, {"category__id__exact": self.empty.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["cl"].result_count, 0)

    def test_category_admin_has_books_inline(self):
        self.login_admin()
        response = self.client.get(reverse("admin:catalog_category_change", args=[self.category.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="books-TOTAL_FORMS"')
        self.assertContains(response, 'value="Python"')
