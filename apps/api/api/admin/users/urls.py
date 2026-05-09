from django.urls import path

from api.admin.users.views import UsersSearchView

app_name = "admin_users"

urlpatterns = [
    path("", UsersSearchView.as_view(), name="search"),
    # impersonate/ added in Task 6
]
