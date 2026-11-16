from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import AdminUserCreationForm

from .models import User


class UserAddForm(AdminUserCreationForm):
    class Meta(AdminUserCreationForm.Meta):
        model = User


@admin.register(User)
class AccountAdmin(UserAdmin):
    add_form = UserAddForm
