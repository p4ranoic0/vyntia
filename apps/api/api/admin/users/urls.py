from django.urls import path

from api.admin.users.views import ImpersonateView, UsersSearchView

app_name = "admin_users"

urlpatterns = [
    path("", UsersSearchView.as_view(), name="search"),
    path("<uuid:user_id>/impersonate/", ImpersonateView.as_view(), name="impersonate"),
]
