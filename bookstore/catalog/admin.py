from django.contrib import admin

from .models import Book, Category
from .queries import category_statistics


class BookInline(admin.TabularInline):
    model = Book
    fields = ("title", "author", "price", "stock")
    extra = 1
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "book_count")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = (BookInline,)

    def get_queryset(self, request):
        return category_statistics()

    @admin.display(description="Кількість книг", ordering="book_count")
    def book_count(self, obj):
        return obj.book_count


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "price", "stock")
    list_filter = ("category", "author", "stock")
    search_fields = ("title", "author", "description")
    list_editable = ("price", "stock")
    list_select_related = ("category",)
    autocomplete_fields = ("category",)
