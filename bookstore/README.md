# Книжковий інтернет-магазин — Django

Каталог книг із публічними сторінками списку та деталей, формами керування
книгами, адмінкою й прикладами ORM. Кошик і замовлення можна додавати
наступними етапами.

## Запуск у Docker Compose

Запускайте команди з теки `bookstore`. Для нової інсталяції скопіюйте
`.env.example` у `.env` і задайте власні `POSTGRES_PASSWORD` та
`DJANGO_SECRET_KEY`.

```powershell
docker compose up --build --wait
```

Каталог доступний за адресою http://127.0.0.1:8000/. Під час запуску
`web` застосовує міграції Django та збирає статику. PostgreSQL зберігає
дані у томі `postgres_data`, а Django зберігає зібрану статику у
`static_data`. Redis використовується як кеш Django.

### Одноразове перенесення з SQLite

Виконайте імпорт у нову базу PostgreSQL до початку роботи з каталогом.
Джерело `bookstore.sqlite3` монтується в режимі читання. Перед імпортом
зупиніть процеси, які записують у цей SQLite-файл.

```powershell
$sqlite = (Resolve-Path ./bookstore.sqlite3).Path
docker compose build web
docker compose run --rm -e SQLITE_IMPORT_PATH=/legacy/bookstore.sqlite3 --volume "${sqlite}:/legacy/bookstore.sqlite3:ro" web sh /app/import-sqlite.sh
docker compose up --wait
```

Імпорт переносить каталог, облікові записи, групи, дозволи та службові
дані застосунку. Django створює історію міграцій у PostgreSQL під час
застосування схеми.

## Локальний запуск із SQLite у PowerShell

Потрібен Python 3.12 або новіший. Перейдіть у теку `bookstore` та виконайте:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

Відкрийте http://127.0.0.1:8000/ для перегляду каталогу. Увійдіть через
http://127.0.0.1:8000/admin/ з обліковими даними, які задали через
`createsuperuser`. Створіть категорію в адмінці, потім поверніться
до каталогу й натисніть «Додати книгу».

## Облікові записи та права

- `/accounts/register/` створює обліковий запис без прав редагування.
- `/accounts/login/` виконує вхід за іменем користувача й паролем.
- Кнопка «Вийти» надсилає POST на `/accounts/logout/`.

Міграція створює групу `Catalog editors` з правами `catalog.add_book`,
`catalog.change_book` і `catalog.delete_book`. Увійдіть у `/admin/` як
суперкористувач, відкрийте обліковий запис у розділі Accounts і додайте
його до групи. Там само можна призначати окремі дозволи. Читання каталогу
доступне всім.

Модель `accounts.User` успадковує `AbstractUser`. Команда `migrate`
створює базу `bookstore.sqlite3` під час локального запуску без
`POSTGRES_HOST`. Файл `db.sqlite3`, якщо він є, належить до попередньої
схеми з моделлю `auth.User`.

## Налагодження та журнал запитів

Django Debug Toolbar доступний на локальних HTML-сторінках в режимі DEBUG
з адрес `127.0.0.1` та `::1`. Щоб вимкнути панель для локального запуску,
встановіть `$env:DJANGO_DEBUG_TOOLBAR = '0'` перед запуском сервера.
`DJANGO_DEBUG=0` і `manage.py test` також вимикають панель.

Middleware пише в консоль HTTP-метод, ім’я маршруту, статус і тривалість
запиту в мілісекундах через логер `bookstore.requests`. Для запитів,
маршрут яких не визначився, використовується `<unresolved>`.

## Сторінки каталогу

| Адреса | CBV | Ім’я маршруту |
| --- | --- | --- |
| `/` | ListView | `catalog:book_list` |
| `/books/<pk>/` | DetailView | `catalog:book_detail` |
| `/books/add/` | CreateView | `catalog:book_create` |
| `/books/<pk>/edit/` | UpdateView | `catalog:book_update` |
| `/books/<pk>/delete/` | DeleteView | `catalog:book_delete` |

Пошук за назвою або автором, категорію й наявність можна поєднувати.
У списку відображаються 12 книг на сторінку; посилання пагінації
зберігають параметри фільтра. Змінювати каталог можуть користувачі
з відповідними правами Django. Видалення потребує підтвердження через POST.

Спільний шаблон із навігацією — `catalog/templates/catalog/base.html`.
Bootstrap CSS завантажується з CDN, а власний CSS —
`catalog/static/catalog/store.css` — підключено через тег `static`.

Локальний запуск без Docker за замовчуванням використовує SQLite,
`DEBUG=True` і локальний ключ Django.

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
