"""Приклади ORM, які можна повторно використати у майбутніх views."""

from django.db.models import Avg, Count, Q, Sum

from .models import Book, Category


def available_books(max_price=None):
    """filter: книги в наявності з необов'язковою верхньою межею ціни."""
    books = Book.objects.select_related("category").filter(stock__gt=0)
    if max_price is not None:
        books = books.filter(price__lte=max_price)
    return books


def search_books(term):
    """Q: пошук за назвою АБО автором."""
    return Book.objects.select_related("category").filter(
        Q(title__icontains=term) | Q(author__icontains=term)
    )


def category_statistics():
    """annotate: кількість книг, середня ціна й залишок у кожній категорії."""
    return Category.objects.annotate(
        book_count=Count("books"),
        available_count=Count("books", filter=Q(books__stock__gt=0)),
        average_price=Avg("books__price"),
        total_stock=Sum("books__stock", default=0),
    )
