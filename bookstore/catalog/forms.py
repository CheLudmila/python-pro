from django import forms

from .models import Book, Category


class BookFilterForm(forms.Form):
    q = forms.CharField(
        label="Назва або автор", required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    category = forms.ModelChoiceField(
        label="Категорія", queryset=Category.objects.all(), to_field_name="slug",
        required=False, empty_label="Усі категорії",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    in_stock = forms.BooleanField(
        label="Лише в наявності", required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ("title", "author", "category", "price", "stock", "description")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "author": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "stock": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
        }
