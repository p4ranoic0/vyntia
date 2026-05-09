from django.urls import include, path

app_name = "admin"

urlpatterns = [
    path("tenants/", include("api.admin.tenants.urls")),
    path("users/", include("api.admin.users.urls")),
    path("support-sessions/", include("api.admin.support_sessions.urls")),
]
