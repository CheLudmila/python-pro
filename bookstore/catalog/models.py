from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField("Назва", max_length=150)
    slug = models.SlugField("Slug", max_length=150, unique=True)

    class Meta:
        ordering = ["name", "pk"]
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField("Назва", max_length=255)
    author = models.CharField("Автор", max_length=255)
    price = models.DecimalField(
        "Ціна, грн", max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    description = models.TextField("Опис", blank=True)
    stock = models.PositiveIntegerField("Залишок", default=0)
    category = models.ForeignKey(
        Category, verbose_name="Категорія", on_delete=models.PROTECT,
        related_name="books",
    )

    class Meta:
        ordering = ["title", "pk"]
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        constraints = [
            models.CheckConstraint(condition=models.Q(price__gte=0), name="book_price_nonnegative"),
            models.CheckConstraint(condition=models.Q(stock__gte=0), name="book_stock_nonnegative"),
        ]

    def __str__(self):
        return f"{self.title} — {self.author}"
