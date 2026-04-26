"""URLs para autenticación API v1."""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .test_views import test_permisos_debug
from .views import (
    ChangePasswordAPIView,
    ForgotPasswordAPIView,
    LoginAPIView,
    LogoutAPIView,
    MenuAPIView,
    MenuStructureAPIView,
    PermissionsStructureAPIView,
    ResetPasswordAPIView,
    UserProfileAPIView,
)

app_name = "auth"

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", UserProfileAPIView.as_view(), name="user_profile"),
    path(
        "user-profile/change-password/",
        ChangePasswordAPIView.as_view(),
        name="change_password",
    ),
    path("forgot-password/", ForgotPasswordAPIView.as_view(), name="forgot_password"),
    path("reset-password/", ResetPasswordAPIView.as_view(), name="reset_password"),
    path("menu/", MenuAPIView.as_view(), name="menu"),
    path("menu-structure/", MenuStructureAPIView.as_view(), name="menu_structure"),
    path(
        "permissions-structure/",
        PermissionsStructureAPIView.as_view(),
        name="permissions_structure",
    ),
    path("test-permisos/", test_permisos_debug, name="test_permisos"),
]
