from django.urls import include, path

app_name = "admin"

urlpatterns = [
    path("tenants/", include("api.admin.tenants.urls")),
    # users/ + support-sessions/ added in Tasks 5-6
]
