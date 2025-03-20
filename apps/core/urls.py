from django.urls import path
from apps.core import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.landing, name="landing"),
]
