from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, reverse_lazy
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import CreateView

from .forms import RegistrationForm

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", sensitive_post_parameters("password1", "password2")(CreateView.as_view(
        form_class=RegistrationForm,
        template_name="accounts/register.html",
        success_url=reverse_lazy("accounts:login"),
    )), name="register"),
]
