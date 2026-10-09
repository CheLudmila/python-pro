from flask import Flask, render_template

app = Flask(__name__)

# Навчальні дані: база даних для цього прикладу не потрібна.
books = [
    {"title": "Тигролови", "author": "Іван Багряний", "genre": "Пригодницький роман"},
    {"title": "Лісова пісня", "author": "Леся Українка", "genre": "Драма-феєрія"},
    {"title": "Маленький принц", "author": "Антуан де Сент-Екзюпері", "genre": "Казка-притча"},
]


@app.route("/")
def index():
    return render_template("index.html", book_count=len(books))


@app.route("/books")
def book_list():
    return render_template("items.html", books=books)


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run()
