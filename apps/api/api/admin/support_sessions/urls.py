from django.urls import path

from api.admin.support_sessions.views import SupportSessionsListView

app_name = "admin_support_sessions"

urlpatterns = [
    path("", SupportSessionsListView.as_view(), name="list"),
]
