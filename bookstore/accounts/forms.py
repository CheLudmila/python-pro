from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Електронна пошта")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")
