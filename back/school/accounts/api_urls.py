from django.urls import path
from .api_views import RegisterAPI, LoginAPI, AdminLoginAPI, MeAPI, LogoutAPI

app_name = "accounts_api"

urlpatterns = [
    path("auth/register/", RegisterAPI.as_view(), name="register"),
    path("auth/login/", LoginAPI.as_view(), name="login"),
    path("auth/admin-login/", AdminLoginAPI.as_view(), name="admin_login"),
    path("auth/me/", MeAPI.as_view(), name="me"),
    path("auth/logout/", LogoutAPI.as_view(), name="logout"),
]
