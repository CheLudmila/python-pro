from flask import Flask, render_template, request

app = Flask(__name__)

# Навчальні дані: база даних для цього прикладу не потрібна.
books = [
    {
        "title": "Біблія",
        "tradition": "Християнство",
        "genre": "Священне Письмо",
        "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f9/Ivan_Ohienko_Bible.djvu/page1-500px-Ivan_Ohienko_Bible.djvu.jpg",
        "image_source": "https://commons.wikimedia.org/wiki/File:Ivan_Ohienko_Bible.djvu",
        "photographer": "Іван Огієнко (переклад) / Internet Archive",
        "license": "CC BY-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "caption": "Біблія українською мовою, переклад Івана Огієнка"
    },
    {
        "title": "Коран",
        "tradition": "Іслам",
        "genre": "Священне Письмо",
        "image": "https://upload.wikimedia.org/wikipedia/commons/f/f4/Quran.jpg",
        "image_source": "https://commons.wikimedia.org/wiki/File:Quran.jpg",
        "photographer": "Національна бібліотека Польщі",
        "license": "Суспільне надбання",
        "license_url": "https://creativecommons.org/publicdomain/mark/1.0/",
        "caption": "Сторінка рукописного Корану XVII століття"
    },
    {
        "title": "Бгаґавад-Ґіта",
        "tradition": "Індуїзм",
        "genre": "Духовно-філософський текст",
        "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/ca/1975_Bhagavad-Gita.jpeg/500px-1975_Bhagavad-Gita.jpeg",
        "image_source": "https://commons.wikimedia.org/wiki/File:1975_Bhagavad-Gita.jpeg",
        "photographer": "Francisco Valdomiro Lorenz / Wikimedia Commons",
        "license": "Суспільне надбання",
        "license_url": "https://commons.wikimedia.org/wiki/File:1975_Bhagavad-Gita.jpeg#Licensing",
        "caption": "Обкладинка видання Бгаґавад-Ґіти мовою есперанто, 1975"
    }
]

churches = [
    {
        "name": "Києво-Печерська лавра",
        "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/0b/Kyiv_Pechersk_Lavra_View_from_the_Dnieper_River.jpg/960px-Kyiv_Pechersk_Lavra_View_from_the_Dnieper_River.jpg",
        "image_source": "https://commons.wikimedia.org/wiki/File:Kyiv_Pechersk_Lavra_View_from_the_Dnieper_River.jpg",
        "photographer": "Ввласенко",
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "address": "вул. Лаврська, 9, Київ",
        "description": "Монастирський комплекс, заснований в XI столітті, та пам’ятка всесвітньої спадщини ЮНЕСКО. Важливий осередок духовної історії, культури й мистецтва України.",
        "source": "https://tickets.kplavra.kyiv.ua/site/about",
    },
    {
        "name": "Софійський собор",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Saint_Sophia_Cathedral_in_Kyiv_2006.jpg/960px-Saint_Sophia_Cathedral_in_Kyiv_2006.jpg",
        "image_source": "https://commons.wikimedia.org/wiki/File:Saint_Sophia_Cathedral_in_Kyiv_2006.jpg",
        "photographer": "Sajmon~commonswiki",
        "license": "Суспільне надбання",
        "license_url": "https://commons.wikimedia.org/wiki/File:Saint_Sophia_Cathedral_in_Kyiv_2006.jpg",
        "address": "вул. Володимирська, 24, Київ",
        "description": "Собор на території Національного заповідника «Софія Київська». Місце знайомства з духовною та мистецькою спадщиною міста.",
        "source": "https://guide.kyivcity.gov.ua/organization/natsionalnyy-zapovidnyk-sofiya-kyyivska",
    },
    {
        "name": "Михайлівський Золотоверхий монастир",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Kiev_stmichael_May_2010.JPG/960px-Kiev_stmichael_May_2010.JPG",
        "image_source": "https://commons.wikimedia.org/wiki/File:Kiev_stmichael_May_2010.JPG",
        "photographer": "Bibikoff",
        "license": "Суспільне надбання",
        "license_url": "https://commons.wikimedia.org/wiki/File:Kiev_stmichael_May_2010.JPG",
        "address": "вул. Трьохсвятительська, 8, Київ",
        "description": "Монастирський ансамбль, відновлений наприкінці XX століття. Його історія розповідає про збереження та відродження культурної спадщини.",
        "source": "https://knmc.kyivcity.gov.ua/muzej-istoriyi-myhajlivskogo-zolotoverhogo-monastyrya/",
    },
    {
        "name": "Андріївська церква",
        "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4b/Andrew%27s_Church.jpg/960px-Andrew%27s_Church.jpg",
        "image_source": "https://commons.wikimedia.org/wiki/File:Andrew%27s_Church.jpg",
        "photographer": "Тетяна Борисенко",
        "license": "CC BY-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "address": "Андріївський узвіз, 23, Київ",
        "description": "Церква на пагорбі над Подолом. Одна з духовних та архітектурних пам’яток Андріївського узвозу.",
        "source": "https://andriyivska-tserkva.kiev.ua/",
    },
]


@app.route("/")
def index():
    return render_template("index.html", book_count=len(books), church_count=len(churches),
                           featured_book=books[0] if books else None,
                           featured_church=churches[0] if churches else None)


@app.route("/books")
def book_list():
    query = request.args.get("q", "").strip()
    filtered_books = [book for book in books if query.casefold() in book["title"].casefold()]
    return render_template("items.html", books=filtered_books, query=query)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/churches")
def church_list():
    return render_template("churches.html", churches=churches)


if __name__ == "__main__":
    app.run()
