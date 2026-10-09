# Моя книжкова полиця

Невеликий навчальний Flask-додаток: три маршрути та чотири HTML-шаблони.

## Запуск

Відкрийте термінал у папці `project_folder` та виконайте:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py
```

Відкрийте http://127.0.0.1:5000 у браузері. Для зупинки натисніть `Ctrl+C` у терміналі.

## Структура

```text
project_folder/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── items.html
│   └── about.html
└── static/
    └── style.css
```

## Маршрути

| URL | Призначення | Шаблон |
| --- | --- | --- |
| `/` | Головна сторінка з кількістю книг | `index.html` |
| `/books` | Назви книг, автори та жанри | `items.html` |
| `/about` | Опис додатку | `about.html` |

Усі сторінки успадковують `base.html` зі спільним меню та стилями.
Функція `render_template()` передає дані Python у шаблони Jinja.
У `items.html` цикл `for` формує картки книг, а `else` показує повідомлення для порожнього списку.

Щоб змінити добірку, відредагуйте список `books` у `app.py`.
База даних та реєстрація не потрібні.
