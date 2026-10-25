# Книжковий інтернет-магазин — Django

Основа для наступних домашніх завдань: каталог книг, категорії, адмінка та
приклади ORM. Інтерфейс покупця, кошик і замовлення можна додавати наступними етапами.

## Запуск у PowerShell

Потрібен Python 3.12 або новіший. Перейдіть у теку `bookstore` та виконайте:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

Відкрийте http://127.0.0.1:8000/admin/ та увійдіть з обліковими даними,
які задали через `createsuperuser`. Спочатку додайте категорію, потім книги.
Адміністратора навмисно не створено з наперед визначеним паролем.

Налаштування розраховані на локальне навчання: SQLite, `DEBUG=True`,
локальний ключ Django. Перед публікацією потрібні окремі production-налаштування.

## Моделі

- `Category`: `name`, унікальний `slug` для URL.
- `Book`: `title`, `author`, `price`, необов'язковий `description`, `stock`, `category`.

Кожна книга належить одній категорії через `ForeignKey`. Зворотний зв'язок:
`category.books.all()`. Категорію з книгами видалити не можна (`PROTECT`).
Ціна зберігається як `DecimalField` з двома знаками після коми.
Нульові ціна та залишок дозволені, від'ємні значення заборонені валідацією
моделі та обмеженнями бази. Звичайний `save()` не викликає `full_clean()`;
для перевірки даних у власних скриптах викликайте його явно.

## Адмінка

- У категорії можна додавати й редагувати книги через `TabularInline`.
- Для категорій доступні пошук за назвою і slug, автоматичне заповнення slug
  та кількість книг, обчислена через `annotate`.
- Для книг доступні пошук за назвою, автором і описом, фільтри за категорією,
  автором та залишком, зміна ціни й залишку прямо у списку.
- Категорію книги можна обрати через автодоповнення.

## Django ORM

Запустіть shell:

```powershell
.\.venv\Scripts\python.exe manage.py shell
```

Створіть приклад даних (один раз):

```python
from decimal import Decimal
from catalog.models import Book, Category

category = Category.objects.create(name="Програмування", slug="programming")
book = Book.objects.create(
    title="Вивчаємо Python",
    author="Автор прикладу",
    price=Decimal("450.00"),
    description="Навчальна книга",
    stock=10,
    category=category,
)
```

`filter` — книги в наявності до 500 грн:

```python
books = Book.objects.filter(stock__gt=0, price__lte=Decimal("500.00"))
list(books)
```

`Q` — назва містить Python АБО автор містить «Автор», і книга є в наявності:

```python
from django.db.models import Q

books = Book.objects.filter(
    Q(title__icontains="Python") | Q(author__icontains="Автор"),
    stock__gt=0,
)
list(books)
```

`annotate` — кількість книг і середня ціна для кожної категорії:

```python
from django.db.models import Avg, Count

stats = Category.objects.annotate(
    book_count=Count("books"),
    average_price=Avg("books__price"),
)
list(stats.values("name", "book_count", "average_price"))
```

Готові функції в `catalog/queries.py` повертають QuerySet для подальшого використання:

```python
from catalog.queries import available_books, search_books, category_statistics

list(available_books(max_price=Decimal("500.00")))
list(search_books("Python"))
list(category_statistics().values(
    "name", "book_count", "available_count", "average_price", "total_stock",
))
```

`available_count` — кількість найменувань у наявності, `total_stock` — сума
примірників. Порожня категорія має нульові лічильники та `average_price=None`.
SQLite має обмеження пошуку без урахування регістру для кирилиці;
для майбутнього каталогу варто налаштувати відповідний пошук у PostgreSQL.

## Міграції та перевірки

Початкова міграція вже збережена в `catalog/migrations/0001_initial.py`.
Після майбутніх змін моделей:

```powershell
.\.venv\Scripts\python.exe manage.py makemigrations
.\.venv\Scripts\python.exe manage.py migrate
```

Перевірка проєкту, узгодженості міграцій та всі тести:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py test
```

Тести використовують окрему тимчасову базу й перевіряють ORM, обмеження
даних, пошук та фільтри адмінки й відображення інлайнів.
