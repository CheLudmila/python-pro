from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import BookForm, BookFilterForm
from .models import Book
from .queries import search_books


class BookListView(ListView):
    model = Book
    context_object_name = "books"
    paginate_by = 12

    def get_queryset(self):
        self.filters = BookFilterForm(self.request.GET)
        books = Book.objects.select_related("category")
        if self.filters.is_valid():
            data = self.filters.cleaned_data
            if data["q"]:
                books = search_books(data["q"])
            if data["category"]:
                books = books.filter(category=data["category"])
            if data["in_stock"]:
                books = books.filter(stock__gt=0)
        return books

    def get_context_data(self, **kwargs):
        return super().get_context_data(filter_form=self.filters, **kwargs)


class BookDetailView(DetailView):
    queryset = Book.objects.select_related("category")


class BookWriteMixin(PermissionRequiredMixin):
    model = Book
    login_url = reverse_lazy("admin:login")


class BookCreateView(BookWriteMixin, CreateView):
    permission_required = "catalog.add_book"
    form_class = BookForm

    def get_success_url(self):
        return reverse("catalog:book_detail", args=[self.object.pk])


class BookUpdateView(BookWriteMixin, UpdateView):
    permission_required = "catalog.change_book"
    form_class = BookForm

    def get_success_url(self):
        return reverse("catalog:book_detail", args=[self.object.pk])


class BookDeleteView(BookWriteMixin, DeleteView):
    permission_required = "catalog.delete_book"
    success_url = reverse_lazy("catalog:book_list")
